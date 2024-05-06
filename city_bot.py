"""Prompts for displaying information about a specific city.

This file defines the prompts that generate the summary for a city given the
user's preferences as well as the Places API queries for obtaining interesting
places.
"""

import concurrent.futures
import json
import logging
import random
from typing import Any, Dict, List, Optional
from uuid import uuid4
from flask import render_template
from languages import supported_languages
import places_api_client
from swiss_cities import SWISS_CITIES, SWISS_CITY_PLACE_ID_MAP
from swiss_cities import SWISS_CITY_GEO_INDEX
from swiss_cities import SwissCity, find_city, filter_cities


ENABLE_GEOCODING_CALLS = True


CURATOR_BOT_PROMPT = """
You are an expert travel agent and your job is to match the travel preferences
of customers against a list of travel destinations.

Customer is traveling from {origin}.

{duration}

Do not recommend places that are within a few hours driving distance to {origin}.

{preferences}
{region}

Use the following format:
* City, Region, Country

The top-10 cities to fly to for this customer are:

"""


def curator_generate_prompt(**kwargs) -> Dict[str, str]:
  origin = kwargs.get('origin')
  if not origin:
    origin = 'Zurich'
  cities = filter_cities(
      SWISS_CITIES,
      origin=origin,
      min_price=kwargs.get('min_price'),
      max_price=kwargs.get('max_price'),
  )
  region = kwargs.get('region')
  region = (
      f' And the customer would like to travel to {region}. Please only'
      f' recommend destinations that are in {region}.'
      if region
      else ''
  )
  duration = kwargs.get('duration')
  duration = (
      f'Customer is traveling for {duration} days. They are traveling by plane'
      ' so you can suggest destinations that are reachable by plane in a'
      ' reasonable time given their travel duration.'
      if duration
      else ''
  )

  preferences = kwargs.get('preferences')
  preferences = (
      f" The customer's preferences are {preferences}." if preferences else ''
  )

  city_names = [c.name['en'] for c in cities]
  random.shuffle(city_names)
  return {
      'cities': '\n'.join(city_names),
      'preferences': preferences,
      'region': region,
      'origin': kwargs['origin'],
      'duration': duration,
      'language': kwargs['language'],
      'direct': kwargs.get('direct'),
  }


places_api = places_api_client.PlacesApiClient()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=50)


class ParsedCity:
  def __init__(self, city: str, region: str, country: str):
    self.city = city
    self.region = region
    self.country = country

  @classmethod
  def parse(cls, llm_output: str):
    parts = [p.strip(' ') for p in llm_output.split(',')]
    if len(parts) == 2:
      return cls(parts[0], None, parts[1])
    elif len(parts) == 3:
      return cls(*parts)
    else:
      return None

  def resolve(self) -> Optional[SwissCity]:
    return find_city(self.city, self.country)


def curator_parse_response(response: str) -> List[str]:
  cities = []
  for line in response.splitlines():
    cities.append(line.strip(' -*'))
  return cities


def curator_merge_candidates(
    candidates: List[List[str]],
) -> List[SwissCity]:
  city_counts = {}
  for candidate in candidates:
    for city in candidate:
      city_counts[city] = city_counts.get(city, 0) + 1
  cities = [
      city
      for city, count in sorted(
          city_counts.items(), key=lambda i: i[1], reverse=True
      )
  ]
  logging.info(cities)

  result = {}
  autocomplete_futures = []
  for city in cities:
    parsed_city = ParsedCity.parse(city)
    if not parsed_city:
      logging.debug(f'Cannot parse city {city}')
      continue
    swiss_city = parsed_city.resolve()
    if swiss_city:
      result[swiss_city.id] = swiss_city
    else:
      logging.debug(f'Cannot find {parsed_city.__dict__}')
      autocomplete_futures.append(
          executor.submit(places_api.places_autocomplete, input_text=city)
    )

  geocode_futures = []
  for future in autocomplete_futures:
    try:
      predictions = future.result()
      if not predictions:
        continue
      description = predictions[0]['description']
      place_id = predictions[0]['place_id']
      city = SWISS_CITY_PLACE_ID_MAP.get(place_id)
      if city:
        result[city.id] = city
      elif ENABLE_GEOCODING_CALLS:
        geocode_futures.append((
            description,
            executor.submit(
                places_api.geocode,
                place_id=place_id,
            ),
        ))
    except Exception as e:
      logging.exception(e)
      continue

  def get_country_code(geocoding_result):
    for address_component in reversed(geocoding_result['address_components']):
      if 'country' in address_component['types']:
        return address_component['short_name'].lower()
    return None

  for description, future in geocode_futures:
    try:
      country_code = get_country_code(future.result()[0])
      location = future.result()[0]['geometry']['location']
      lat_lng = (location['lat'], location['lng'])
      for city in SWISS_CITY_GEO_INDEX.lookup(lat_lng, 100):
        if city.country_code != country_code:
          logging.info(f'Dropping {city.name["en"]} due to country')
          continue
        if city.id in result:
          continue
        result[city.id] = city
    except Exception as e:
      logging.exception(e)
      continue

  logging.info(
      f'City selection calls, autocomplete: {len(autocomplete_futures)},'
      f' geocoding: {len(geocode_futures)}'
  )
  return list(result.values())


class City:

  def __init__(self, city: SwissCity, language: str):
    self.id = city.id
    self.name = city.name[language]
    self.country = city.country[language]


def curator_render_response(
    cities: List[SwissCity], params: Dict[str, Any]
) -> Dict[str, Any]:
  origin = params.get('origin', 'Zurich')
  cities = filter_cities(
      cities,
      origin,
      params.get('min_price'),
      params.get('max_price'),
  )[:20]
  language = params['language']

  filter_direct = params.get('direct')
  if filter_direct:
    cities = [c for c in cities if c.is_direct(origin)]
  else:
    # Rank the cities with a direct flight from the selected origin higher.
    cities.sort(key=lambda c: 1 if c.is_direct(origin) else 2)


  return {
      'cities': [City(c, language).__dict__ for c in cities],
      'html': render_template(
          'cities.html',
          **{
              'cities': cities,
              'language': params['language'],
              'origin': origin,
          },
      ),
  }


CURATOR_BOT_PARAMS = {
    'model': 'text-bison@002',
    'temperature': 0.2,
    'max_output_tokens': 256,
    'top_p': 0.8,
    'top_k': 40,
    'candidate_count': 5,
    'response_parser': curator_parse_response,
    'candidate_merger': curator_merge_candidates,
}


SUMMARY_BOT_PARAMS = {
    'model': 'text-bison@002',
    'temperature': 0.7,
    'max_output_tokens': 256,
    'top_p': 0.8,
    'top_k': 40,
}


SUMMARY_BOT_PROMPT = """
In 80 words or less, write a paragraph explaining why someone with preferences
for {preferences} might want to visit {city}.

Please write the response in {language}
"""


def summary_generate_prompt(**kwargs) -> Dict[str, str]:
  preferences = kwargs.get('preferences')
  preferences = (
      f'for someone with preferences {preferences},' if preferences else ''
  )
  return {
      'preferences': preferences,
      'city': kwargs['city'],
      'language': supported_languages[kwargs['language']],
  }


def _substitute_german_characters(text: str) -> str:
  return text.replace('ß', 'ss')

# Functions applied to the LLM output for post-processing.
POST_PROCESSING_ACTIONS = [_substitute_german_characters]


def summary_render_response(response: str, _) -> Dict[str, Any]:
  for action in POST_PROCESSING_ACTIONS:
    response = action(response)
  return json.dumps({'city': {'summary': response}})


def city_lookup_generator(params: Dict[str, Any]) -> Dict[str, Any]:
  origin = params.get('origin', 'Zurich')
  language = params.get('language', 'en')
  allowed_cities = {c.name['en']: c for c in SWISS_CITIES}
  cities = []
  for c in params.get('cities', []):
    city = allowed_cities.get(c)
    cities.append(city)
  return {
      'cities': cities,
      'language': language,
      'origin': origin,
  }


def city_lookup_renderer(response) -> str:
  cities = response.value['cities']
  language = response.value['language']
  origin = response.value['origin']
  return {
      'cities': [City(c, language).__dict__ for c in cities],
      'html': render_template(
          'cities.html',
          **{
              'cities': cities,
              'language': language,
              'origin': origin,
          },
      ),
  }
