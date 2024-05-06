"""Code for generating an itinerary for a city.

Includes the prompt and the code that talks to the Places API for grounding
as well as the retrieval of relevant locations mentioned in the itinerary.
"""

import base64
import concurrent
import json
import logging
import re
from typing import Any, Dict, List, Optional, Generator
from languages import supported_languages, language_to_code
from swiss_cities import SWISS_CITY_ID_MAP

from flask import render_template
from google.cloud import translate_v2 as translate
from Levenshtein import distance

from languages import supported_languages, language_to_code
from places_api_client import PlacesApiClient

ITINERARY_BOT_PARAMS = {
    'model': 'text-bison',
    'temperature': 0.2,
    'max_output_tokens': 1024,
    'top_p': 0.8,
    'top_k': 40,
}


ITINERARY_BOT_PROMPT = """
Please generate an itinerary for a tourist visiting {city}, {country}
Amount of days in itinerary: {num_days_to_generate}
Each itinerary day is composed by 3 activities: a morning activity, an afternoon activity and an evening activity.
{preferences}

Please follow this criteria:
- If the itinerary activity refers to visiting a specific establishment or place, please make sure to surround the establishment or place name
by square brackets as listed in Google Maps. Only one per activity.
- Do not include any links to websites.
- Group activities in the same geographical area in the same day.
- Do not include Festivals or temporary events.
- All places, establishments and restaurants and places listed in the itinerary must exist and be named specifically
- Do not repeat the same activity every day.
- Every activity should include a place, establishment, or landmark that exists in Google Maps.
- Do not repeat places or activities across days.
- Keep the activity descriptions brief, just a few words describing the activity.

The format should be as follows:
Day 1:
* Some activity in the morning in [establishment]
* An afternoon activity in [place]
* Some evening activity in [place]

Please write the response in {language}


"""

MAX_ITINERARY_DAYS = 14
DEFAULT_ITINERARY_DAYS = 3

VALIDATION_TYPE_NONE = 'none'
VALIDATION_TYPE_ADVANCED = 'advanced'
VALIDATION_TYPE_BASIC = 'basic'
INVALID_PLACE_TYPES = {'lodging'}

def generate_prompt(**kwargs) -> Dict[str, str]:
  num_days = DEFAULT_ITINERARY_DAYS
  if kwargs.get('num_days'):
    num_days = int(kwargs['num_days'])

  if int(num_days) > MAX_ITINERARY_DAYS:
    num_days = MAX_ITINERARY_DAYS

  preferences = kwargs.get('preferences')
  preferences = f'''The tourist has preferences: {preferences}.
  Include activities that match these preferences if you can at least every
  other day.''' if preferences else ''

  city = SWISS_CITY_ID_MAP[kwargs.get('id')]
  validation_type = kwargs.get('validation_type', VALIDATION_TYPE_BASIC)

  return {
      'preferences': preferences,
      'id': city.id,
      'city': city.name['en'],
      'country': city.country['en'],
      'language': supported_languages[kwargs['language']],
      'num_days': num_days,
      'num_days_to_generate': (
          num_days * 2 if validation_type != VALIDATION_TYPE_NONE else num_days
      ),  # Generating alternatives for validation
      'validation_type': validation_type,
  }

executor = concurrent.futures.ThreadPoolExecutor(max_workers=50)


class PlaceMatch:

  def __init__(
      self,
      place_id: str,
      query_id: str,
      matched_name: str,
  ):
    self.place_id = place_id
    self.matched_name = matched_name
    self.query_id = query_id


class Place:

  def __init__(
      self,
      id: str,
      query_id: str,
      name: str,
      description: Optional[str],
      image: bytes,
      attribution: Optional[str],
      website: Optional[str],
      url: str,
  ):
    self.id = id
    self.query_id = query_id
    self.name = name
    self.description = description
    self.image_b64 = base64.b64encode(image).decode('utf-8')
    self.attribution = attribution
    self.website = website
    self.url = url

  def to_string(self) -> str:
    return (
        f'Place: {self.id}, {self.query_id}, {self.name}, {self.description},'
        f' {self.url}'
    )


class City:

  def __init__(self, name: str, country: str, lat: str, lng: str):
    self.name: str = name
    self.country: str = country
    self.lat: str = lat
    self.lng: str = lng


class Query:

  def __init__(self, text: str, id: str):
    self.text: str = text
    self.id: str = id
    self.valid = False


# Itinerary validation parameters
VALID_WORD_DISTANCE = 1


# Radius used when validating places, in meters.
VALID_RADIUS = 200000
ALLOWED_DELIMITERS = ' |-|,'


class PlaceRetriever:
  client = PlacesApiClient()
  translate_client = translate.Client()

  @classmethod
  def get_place_details(
      cls, query: Query, lang: str, city: City, place_id: Optional[str]
  ) -> Place:
    if place_id is None:
      place_match = PlaceRetriever.get_place_search_match(query.text, city, lang)
      if not place_match:
        logging.info('No Places API results for query: %s', query.text)
        return None

      if not TermValidator.place_name_valid(
          place_match.matched_name, query.text):
        logging.info(
            '[Fetch Place [%s]: Could not match "%s"(LLM) against "%s"(Places API)',
            city.name,
            query.text,
            place_match.matched_name,
        )
        return None
      place_id = place_match.place_id
    else:
      logging.info('Fetching details for provided place_id for %s', query.text)

    fields = ['photo', 'editorial_summary', 'website', 'url', 'name']
    place_future = executor.submit(
        cls.client.place,
        place_id=place_id,
        language=lang,
        fields=fields
    )
    place = place_future.result()['result']
    if 'photos' not in place.keys():
      logging.info('No photos for: %s:, %s', query.text, query.id)
      return None

    photo = place['photos'][0]
    photo_future = executor.submit(
        cls.client.places_photo,
        photo_reference=photo['photo_reference'],
        max_width=300,
    )

    attribution = None
    if photo.get('html_attributions'):
      attribution = photo['html_attributions'][0]

    if 'editorial_summary' not in place.keys():
      logging.info('No editoral summary found for : %s:', query.text)
      description = None
    else:
      description = place['editorial_summary']['overview']

    if 'website' not in place.keys():
      website = None
    else:
      website = place['website']

    photo = b''.join([chunk for chunk in photo_future.result()])
    place_result = Place(
        id=place_id,
        query_id=query.id,
        name=place['name'],
        description=description,
        image=photo,
        attribution=attribution,
        website=website,
        url=place['url'],
    )
    logging.debug('place_result: Place: %s', place_result.to_string())
    return place_result

  @classmethod
  def get_city_with_location(cls, city_name: str, country: str) -> City:
    query = ', '.join([city_name, country])
    results = cls.client.find_place(
        query, input_type='textquery', fields=['name', 'geometry']
    )
    if not results or not results['candidates']:
      logging.info('City not found in places: %s', query)
      return None

    location = results['candidates'][0]['geometry']['location']
    return City(city_name, country, str(location['lat']), str(location['lng']))

  @classmethod
  def translate_query(cls, query, lang) -> str:
    translated_result = cls.translate_client.translate(
        query, target_language=lang
    )
    return translated_result['translatedText']

  @classmethod
  def get_place_autocomplete_match(
      cls, query: str, city: City, lang: str) -> PlaceMatch:

    results = cls.client.places_autocomplete(
        input_text=query,
        location=','.join([city.lat, city.lng]),
        radius=VALID_RADIUS,
        language=lang,
        strict_bounds=True,
    )

    if not results:
      logging.info('No places results in %s for query: %s', city.name, query)
      return None

    result = None
    for autocomplete_result in results:
      invalid_types = set(autocomplete_result['types']).intersection(
          INVALID_PLACE_TYPES
      )
      if invalid_types:
        logging.info(
            'Skipping autocomplete result with types %s, %s',
            str(autocomplete_result['types']),
            autocomplete_result['description'],
        )
        continue
      result = autocomplete_result
      break

    if result is None:
      logging.info('No places match for: %s in %s', query, city.name)
      return None
    structured_formatting = result['structured_formatting']
    if structured_formatting is None:
      logging.info('No places match for: %s in %s', query, city.name)
      return None
    else:
      place_name = structured_formatting['main_text']
      return PlaceMatch(
          place_id=result['place_id'],
          query_id=query,
          matched_name=place_name,
      )

  @classmethod
  def get_place_search_match(
      cls, query: str, city: City, lang: str
  ) -> PlaceMatch:
    location = (
        'circle:' + str(VALID_RADIUS) + '@' + ','.join([city.lat, city.lng])
    )
    fields = ['name', 'place_id']

    results = cls.client.find_place(
        input_type='textquery',
        input=query,
        location_bias=location,
        language=lang,
        fields=fields,
    )

    if (
        not results
        or results['candidates'] is None
        or not results['candidates']
    ):
      logging.info('No places results in %s for query: %s', city.name, query)
      return None

    result = results['candidates'][0]
    place_name = result['name']
    if place_name is None:
      logging.info('No places match for: %s in %s', query, city.name)
      return None
    else:
      return PlaceMatch(
          place_id=result['place_id'],
          query_id=query,
          matched_name=place_name,
      )


class TermValidator:

  @staticmethod
  def is_string_similar(a, b) -> bool:
    dist = distance(a, b)
    if dist <= VALID_WORD_DISTANCE and dist > 0:
      logging.info(
          '[Term Validation]: allow similarity: between "%s" and "%s"', a, b
      )
    return dist <= VALID_WORD_DISTANCE

  @staticmethod
  def contains_word(a: str, terms: List[str]) -> bool:
    for b in terms:
      if TermValidator.is_string_similar(a.lower(), b.lower()):
        return True
    return False

  @staticmethod
  def place_name_valid(place_name: str, query_text: str) -> bool:
    places_terms = re.split(ALLOWED_DELIMITERS, place_name)
    query_terms = re.split(ALLOWED_DELIMITERS, query_text)

    if not TermValidator.are_terms_valid(query_terms, places_terms):
      translated_place = PlaceRetriever.translate_query(
          place_name, 'en')
      translated_query = PlaceRetriever.translate_query(query_text, 'en')
      places_terms = re.split(ALLOWED_DELIMITERS, translated_place)
      query_terms = re.split(ALLOWED_DELIMITERS, translated_query)

      return TermValidator.are_terms_valid(query_terms, places_terms)

    return True


  # Heuristic: all words in the main text of the Place entry have
  # to exist in the query, if this fails try the other way around.
  @staticmethod
  def are_terms_valid(query_terms: List[str], places_terms: List[str]) -> bool:
    matches_places_terms = True
    for places_term in places_terms:
      if not TermValidator.contains_word(places_term, query_terms):
        matches_places_terms = False
        break

    if not matches_places_terms:
      for query_term in query_terms:
        if not TermValidator.contains_word(query_term, places_terms):
          return False

    return True


class Itinerary:
  DAY_RE = re.compile('\s*(Day|Tag|Jour) [0-9]')

  class Activity:
    QUERY_RE = re.compile('^(.*?)\[(.*?)\](.*?)$')

    def __init__(self, text: str, query: Query, prefix: str, suffix: str):
      self.text: str = text
      self.query: Query = query
      self.prefix: str = prefix
      self.suffix: str = suffix
      self.place: PlaceMatch = None

    @classmethod
    def parse(cls, line: str, line_id: str):
      line = line.replace('*', '')
      query_match = cls.QUERY_RE.search(line)
      if not query_match:
        logging.info('No query match for: %s', line)
        query = None
        prefix = None
        suffix = None
      else:
        query_text = query_match.group(2)
        query = Query(query_text, line_id)
        prefix = query_match.group(1)
        suffix = query_match.group(3).replace('[', '').replace(']', '')

      activity = cls(line, query, prefix, suffix)
      return activity


  class Day:

    def __init__(self):
      self.index = 1
      self.activities: List[Itinerary.Activity] = []

    def add_activity(self, activity):
      self.activities.append(activity)

  def __init__(self):
    self.days: List[Itinerary.Day] = []
    self.alt_days: List[Itinerary.Day] = []

  @classmethod
  def parse(cls, text: str, city: str, num_days: int):
    itinerary = cls()
    day = Itinerary.Day()
    activity_index = 0
    for line in text.splitlines():
      if not line:
        continue
      match = Itinerary.DAY_RE.search(line)
      if match:
        if day.activities:
          if len(itinerary.days) == num_days:
            itinerary.add_alt_day(day)
          else:
            itinerary.add_day(day)
          day = Itinerary.Day()
      else:
        activity_id = 'activity-{0}-{1}'.format(activity_index, city).replace(
            ' ', '-'
        )
        activity = Itinerary.Activity.parse(line, activity_id)
        activity_index += 1
        if activity:
          day.add_activity(activity)
    if day.activities:
      if len(itinerary.days) < num_days:
        itinerary.add_day(day)
      else:
        itinerary.add_alt_day(day)
    return itinerary

  def add_day(self, day):
    self.days.append(day)

  def add_alt_day(self, day):
    self.alt_days.append(day)

  def get_queries(self) -> List[Place]:
    queries = []
    for day in self.days:
      for activity in day.activities:
        if (
            activity.query is not None
            and activity.query.valid
            and activity.place is not None
        ):
          query = {
              'query': activity.query.text,
              'id': activity.query.id,
              'place_id': activity.place.place_id,
          }
          queries.append(query)

    logging.info('Queries: %s', str(queries))
    return queries

  @classmethod
  def validate_day(cls, day: Day, city: City, lang: str,
                   validation_type: str = VALIDATION_TYPE_BASIC) -> bool:
    if validation_type == VALIDATION_TYPE_NONE:
      return True

    for activity in day.activities:
      if  activity.query is None:
        logging.debug(
            '[Activity Validation] [%s]: Allow activity without '
            'place/establishment: %s',
            city.name,
            activity.text,
        )
        if activity.query:
          activity.query.valid = True
        continue

      query = activity.query
      query_text = query.text

      if validation_type == VALIDATION_TYPE_ADVANCED:
        place = PlaceRetriever.get_place_search_match(
            query_text, city, lang)
      else:
        place = PlaceRetriever.get_place_autocomplete_match(
            query_text, city, lang)

      if place is None:
        logging.info(
            '[Activity Validation] [%s] REJECT: No places match for: %s',
            city.name,
            query_text,
        )
        return False

      if not TermValidator.place_name_valid(place.matched_name, query_text):
        logging.info(
            '[Activity Validation] [%s]: REJECT activity "%s":\n'
            'Could not match "%s"(LLM) against "%s"(Places API)',
            city.name,
            activity.text,
            query_text,
            place.matched_name,
        )
        return False

      logging.info(
          '[Activity Validation] [%s]: ACCEPT activity. Validated '
          '"%s"(LLM) against "%s"(Places API) \n Activity: %s',
          city.name,
          query_text,
          place.matched_name,
          activity.text,
      )
      activity.query.valid = True
      activity.place = place

    return True


def render_response(
    day: Itinerary.Day, tmp_dict: Dict[str, Any]
) -> Dict[str, Any]:
  itinerary = Itinerary()
  itinerary.add_day(day)

  return json.dumps({
      'itinerary': render_template(
          'itinerary.html', **{'itinerary': itinerary}
      ),
      'queries': itinerary.get_queries(),
  }) + '\n'

def generate_places(params: Dict[str, Any]) -> List[Place]:
  logging.info('generate_places results for: %s', str(params))

  queries = params.get('queries')
  city_id = params.get('city_id')
  language_code = params.get('language')

  swiss_city = SWISS_CITY_ID_MAP[city_id]
  city_with_location = City(
      name=swiss_city.name[language_code],
      country=swiss_city.country[language_code],
      lat=str(swiss_city.location['lat']),
      lng=str(swiss_city.location['lng']),
  )

  if not queries:
    return []
  place_futures = []
  for q in queries:
    query = Query(q.get('query'), q.get('id'))
    place_id = q.get('place_id')
    place_futures.append(
        executor.submit(PlaceRetriever.get_place_details,
                        query, language_code, city_with_location, place_id)
    )

  place_id_set = set()
  places = []
  for future in place_futures:
    try:
      place = future.result()
      if place and place.id not in place_id_set:
        places.append(place)
        place_id_set.add(place.id)
    except Exception as e:
      logging.info('generate_places: got exception: %s', str(e))
      continue
  return places

def lines_from_stream(response_stream: Generator[Any, None, None]):
  lines = ['']
  full_response = ''
  for partial_response  in response_stream:
    if not partial_response.text:
      continue

    full_response += str(partial_response)
    partial_lines = str(partial_response).splitlines()
    index = -1
    for partial_line in partial_lines:
      index += 1
      if index == 0:
        if partial_line.startswith('*'):
          yield lines[-1]
          lines = lines + [partial_line]
        else:
          lines[-1] += partial_line

      if len(partial_lines) == 1:
        break

      if index > 0:
        lines = lines + [partial_line]
        if index == len(partial_lines) - 1:
          break

      line = lines[-1]
      if not line:
        continue

      yield line
  yield lines[-1]
  logging.info('full_response: %s', full_response)

def day_from_lines(lines, city: str):
  day = Itinerary.Day()
  activity_index = 1

  for line in lines:
    match = Itinerary.DAY_RE.search(line)
    if match:
      if day.activities:
        yield day
        day = Itinerary.Day()
    else:
      activity_id = 'activity-{0}-{1}'.format(
          activity_index, city
      ).replace(' ', '-')
      activity = Itinerary.Activity.parse(line, activity_id)
      activity_index += 1
      if activity:
        day.add_activity(activity)
      else:
        logging.info('Cannot parse activity: %s', line)
  if day.activities:
    yield day


def stream_handler(
    responses: Generator[Any, None, None], params: Dict[str, Any]
):
  language_code = language_to_code[params['language']]
  validation_type = params.get('validation_type', VALIDATION_TYPE_BASIC)
  swiss_city = SWISS_CITY_ID_MAP[params.get('id')]
  city_with_location = City(
      name=swiss_city.name[language_code],
      country=swiss_city.country[language_code],
      lat=str(swiss_city.location['lat']),
      lng=str(swiss_city.location['lng'])
  )

  days_to_return = params.get('num_days', 3)
  returned_days = 0
  expected_days = params.get('num_days_to_generate', 3)
  lines = lines_from_stream(responses)
  for day in day_from_lines(lines, city_with_location.name):
    if Itinerary.validate_day(
        day, city_with_location, language_code, validation_type
    ):
      returned_days += 1
      day.index = returned_days
      yield day
      if returned_days == days_to_return:
        break
      continue

    if expected_days - returned_days <= days_to_return - returned_days:
      returned_days += 1
      logging.info(
          'Accepted bad itinerary for %s, Day: %s',
          city_with_location.name,
          returned_days,
      )
      day.index = returned_days
      yield day
    else:
      expected_days = expected_days - 1
      logging.info('   -- streaming validation: skipping invalid day.')


def render_places(response) -> str:
  return render_template('places.html', **{'places': response.value})
