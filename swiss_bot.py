"""Prompts for the Swiss travel concierge demo.

This file defines the prompt for the LLM as well as the plugins made available
to the bot through the prompt.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import render_template

from plugin import Plugin, PluginDict
import swiss_cities
from data.swiss_bot_examples import EXAMPLES


BOT_PARAMS = {
    'model': 'text-bison',
    'temperature': 0.2,
    'max_output_tokens': 256,
    'top_p': 0.8,
    'top_k': 40,
    'candidate_count': 1,
}

MIN_PRICE = 0
MAX_PRICE = 2500
DEFAULT_DURATION = 3

BOT_PROMPT = """
Context:
You are the travel booking agent for an airline company. Your task is to
understand user preferences and call functions to perform searches that fit their criteria.
For searching, you will use one of two functions: list_cities, and show_itinerary.

If the query is generic, or about a region or country you should call "list_cities".
If the query is about a specific city, you should call "show_itinerary".

"list_cities" function parameters:
- origin: where the customer will be flying from.
- preferences: list of preferences the customer has. If the query does not include a preference you can ignore this parameter.
- max_price: the maximum price the customer would like to pay for a ticket
- min_price: the minimum price the customer would like to pay for a ticket
- start_month: the first month that the customer may consider traveling, as an integer from 1 to 12.
- end_month: the last month that the customer may consider traveling, as an integer from 1 to 12.
- duration: the duration of the trip that the customer wants to do, as an integer representing amount of days.
- region: the regions of the world the customer considers traveling.
- direct: whether to look only for direct flights. If present, the value is always "yes"

"show_itinerary" function parameters:
- preferences: list of preferences the customer has. If the query does not include a preference you can ignore this parameter.
- start_month: the first month that the customer may consider traveling
- end_month: the last month that the customer may consider traveling
- duration: the duration of the trip that the customer wants to do, in integer full days
- city: the city for which to produce the itinerary


"show_itinerary" can only be used with cities. Do not use "show_itinerary" with countries or regions.

The customer is flying from Zurich.

If a function parameter doesn't have a value just ignore it from the method call.

If a desired region is not specified you can assume the customer wants destinations
anywhere in the World.
If the user mentions a year, you should ignore it.

{examples}

Let's begin!

"""


def generate_prompt(**kwargs) -> Dict[str, str]:
  return {
      'examples': EXAMPLES[kwargs['language']],
  }


def render(output_dict: Dict[str, Any]):
  output_dict['utterance_html'] = render_template(
      'utterance.html', **output_dict
  )
  output_dict['filters_html'] = render_template('filters.html', **output_dict)
  return output_dict


def get_display_strings(items: List[str]) -> tuple[List[str], List[str]]:
  original_items = []
  translated_items = []
  for item in items:
    parts = item.split('|')
    if len(parts) == 1:
      original_items.append(item)
      translated_items.append(item)
    else:
      original_items.append(parts[0])
      translated_items.append(parts[1])
  return (original_items, translated_items)


def list_cities(
    origin: str = 'Zurich',
    preferences: Optional[List[str]] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    start_month: int = datetime.now().month,
    end_month: int = (datetime.now().month + 11) % 12,
    duration: Optional[int] = None,
    region: Optional[List[str]] = None,
    direct: Optional[str] = None,
) -> str:
  return Plugin.YIELD_RESPONSE


def render_list_cities(
    response: str,
    tpl_dict: Dict[str, Any],
):
  params = tpl_dict['list_cities']
  logging.info(params)
  price_range = swiss_cities.get_price_range(swiss_cities.SWISS_CITIES)
  if not params.get('min_price'):
    params['min_price'] = price_range[0]
  if not params.get('max_price'):
    params['max_price'] = price_range[1]
  preferences = params.get('preferences')
  if preferences:
    params['preferences'], params['preferences_display'] = get_display_strings(
       preferences
    )
  region = params.get('region')
  if region:
    params['region'], params['region_display'] = get_display_strings(
        region
    )
  return tpl_dict


def show_itinerary(
    city: str,
    origin: str = 'Zurich',
    duration: int = DEFAULT_DURATION,
    preferences: Optional[List[str]] = None,
    start_month: int = datetime.now().month,
    end_month: int = (datetime.now().month + 11) % 12,
) -> str:
  return Plugin.YIELD_RESPONSE


def render_show_itinerary(
    response: str,
    params: Dict[str, Any],
):
  preferences = params.get('preferences')
  if preferences:
    params['preferences'], params['preferences_display'] = get_display_strings(
       preferences
    )
  region = params.get('region')
  if region:
    params['region'], params['region_display'] = get_display_strings(
        region
    )
  return params


PLUGINS = PluginDict([
    Plugin(
        fn=list_cities,
        description='Display a list of selected destinations',
        renderer = render_list_cities,
    ),
    Plugin(
        fn=show_itinerary,
        description='Displays an itinerary for a city',
        renderer = render_show_itinerary,
    ),
])
