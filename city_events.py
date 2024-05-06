"""Code for generating event lists for a city.
"""


import json
import logging
import re
from flask_babel import _
from typing import Any, Dict, List, Optional
from languages import supported_languages
from events import get_events
from swiss_cities import SWISS_CITY_ID_MAP
from flask import render_template


EVENTS_BOT_PARAMS = {
    'model': 'text-bison',
    'temperature': 0.2,
    'max_output_tokens': 1024,
    'top_p': 0.8,
    'top_k': 40,
    'candidate_count': 1,
}


EVENTS_BOT_PROMPT = """
Context:
You are a generator of text for travel inspiration. You should write about
events happening in a city and country I'm considering to visit.
You will be given events in the following JSON format:
[{{"event title": "event title", "event start date": "dd.mm.yyyy", "event end date": "dd.mm.yyyy"", "type of event": "type of event"}}]

When choosing events from the list, make sure to:
- Do not include events for the country in the list of events for the City.
- Select events strictly from the given Input.
- Include events from the given list that can be of interest for a typical tourist.
- If the Input includes "Preferences" you should also include events from the list that are relevant for those preferences.
- Don't include any websites or links in the output.
- The output must contain a maximum of 6 events for the City, and 6 events for the country.
- You can write a small paragraph before the events, you should prefix it with the "(HDR)" string.
- Write a brief description of the event, along with the dates in which is happening, write
varied descriptions for each event that don't follow the same wording.
- Do not return more than 10 events overall in the Output.
- Only return events that are happening between the given month range.

Example 1:

Input:
City - Events in Barcelona = [{{"event title": "Formula 1 Grand Prix Spain", "event start date": "23.06.2024", "event end date": "23.06.2024", "type of event": "Special Event"}}]
Country - Events in Spain = [{{"event title": "MotoGP", "event start date": "26.05.2023", "event end date": "26.05.2023", "type of event": "Special Event"}}]
Preferences: motorsports
Months: April to June

Output:
(HDR)Events happening in Barcelona that might be of your interest:
* [Formula 1 Grand Prix Spain]: This is a must-see for any fan of Formula 1 racing. The race takes place on the Circuit de Barcelona-Catalunya, which is located just outside of the city and
and will be held on the 23rd of June, 2024.

(HDR)Also, take a look at these other events happening in Spain:
* [MotoGP]: a motorcycle racing event that will be held in Spain on May 26th, 2023.

Example 2:
Input:
City - Events in Aberdeen: []
Country - Events in UK:  [{{"event title": "UEFA Champions League Final", "event start date": "01.10.2024", "event end date": "01.10.2024", "type of event": "Special Event"}}]
Preferences: sports
Months: October

Output:
(HDR)I could not find suggestions for events happening in Aberdeen in the requested months, however check out these other events happening around the UK which you might also be interested in:
* [UEFA Champions League Final]: The final will be held at Wembley Stadium in London on October 1st, 2024.

Input:
City - Events in {city} = {city_events}
Country - Events in {country} = {country_events}
{preferences}
{months}

Please write the response in {language}

Output:
"""


def generate_prompt(**kwargs) -> Dict[str, str]:
  city_id = kwargs['id']
  city = kwargs['city']
  country = kwargs['country']
  start_month = kwargs.get('start_month', None)
  end_month = kwargs.get('end_month', None)
  if start_month:
    logging.info('Events for min month: %s', str(start_month))
  if end_month:
    logging.info('Events for max month: %s', str(end_month))

  preferences = kwargs.get('preferences')
  preferences = f'Preferences: {preferences}.' if preferences else ''

  city_events = []
  country_events = []
  swiss_city = SWISS_CITY_ID_MAP.get(city_id)
  if swiss_city:
    city_code = swiss_city.city_code
    country_code = swiss_city.country_code
    city_events = get_events(
        city_code=city_code, start_month=start_month, end_month=end_month
    )
    logging.info('Events for %s:  %s', city_code, str(city_events))

    if country_code:
      country_events = get_events(
          country_code=country_code,
          city_code_exclusion=city_code,
          start_month=start_month,
          end_month=end_month,
      )
      logging.info('Events for %s:  %s', country_code, str(country_events))

  if not country_events and not city_events:
    logging.info('No events found for %s, skip.', city)
    return None

  return {
      'preferences': preferences,
      'city': kwargs['city'],
      'country': kwargs['country'],
      'months': '',
      'language': supported_languages[kwargs['language']],
      'city_events': str(city_events),
      'country_events': str(country_events),
  }

class Events:
  HEADER_RE = re.compile('\((?P<h>HDR)\)')

  class EventList:
    def __init__(self):
      self.header: Optional(str) = None
      self.events: List[Events.Event] = []

    def add_event(self, event):
      self.events.append(event)

  class Event:
    EVENT_NAME_RE = re.compile('\[(?P<n>(.*?))\]')

    def __init__(self, title: str, description: str):
      self.title: str = title
      self.description: str = description

    @classmethod
    def parse(cls, line: str):
      event_name_match = cls.EVENT_NAME_RE.search(line)
      if not event_name_match:
        logging.info('No event name match for: %s', line)
        return None
      event_name = event_name_match.group('n')
      for token_to_remove in [event_name, '*', '-', ':', '[', ']']:
        line = line.replace(token_to_remove, '')

      event = cls(event_name, line.strip())
      return event

  def __init__(self):
    self.event_lists: List[Events.EventList] = []

  @classmethod
  def parse(cls, text):
    events = cls()
    event_list = Events.EventList()
    for line in text.splitlines():
      if not line:
        continue
      header_match = cls.HEADER_RE.search(line)
      if header_match:
        if event_list.events:
          events.add_event_list(event_list)
          event_list = Events.EventList()

        print('Match found: ', header_match.group('h'), line)
        header = line.replace('(HDR)', '').strip()
        event_list.header = header
        continue

      event = Events.Event.parse(line)
      if event:
        event_list.add_event(event)

    if event_list.events:
      events.add_event_list(event_list)

    return events

  def add_event_list(self, event_list):
    self.event_lists.append(event_list)


def render_response(response: str, tmp_dict: Dict[str, Any]) -> Dict[str, Any]:
  if not response:
    parsed_events = Events()
    no_events = Events.EventList()
    no_events.header = _(
        'I could not find suggestions for events happening in the requested months.'
    )
    parsed_events.add_event_list(no_events)
  else:
    logging.info('Events response for %s: %s', tmp_dict['city'], str(response))
    parsed_events = Events.parse(response)

    if not parsed_events:
      logging.info('Cannot parse events for %s', tmp_dict['city'])
      return {'error': 'Cannot parse events'}

    logging.info(
        'Parsed events for %s with (%s) event lists',
        tmp_dict['city'],
        len(parsed_events.event_lists),
    )

  return json.dumps({
      'events': render_template('events.html', events=parsed_events),
  })
