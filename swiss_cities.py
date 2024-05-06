import concurrent.futures
import logging
import sys
from typing import Any, Dict, List, Optional, Tuple

from geo_index import GeoIndex
from swiss_cities_data import DATA


def get_city_country_key(city: str, country: str) -> str:
  return ','.join([city, country])


class SwissCity:
  def __init__(
      self,
      id: int,
      name: Dict[str, str],
      country: Dict[str, str],
      image: str,
      country_code: str,
      city_code: str,
      place_id: str,
      round_trip_price: Optional[int] = None,
      origin: Dict[str, Dict[str, Any]] = {},
      location: Dict[str, float] = {},
      disabled: bool = False,
  ):
    self.id: int = id
    self.name: Dict[str, str] = name
    self.country: Dict[str, str] = country
    self.image: str = image
    self.country_code: str = country_code
    self.city_code: str = city_code
    self.place_id: str = place_id
    self.round_trip_price: Optional[int] = round_trip_price
    self.origin: Dict[str, Dict[str, str]] = origin
    self.location: Dict[str, float] = location
    self.disabled: bool = disabled

  def get_booking_link(self, origin, language):
    return self.origin[origin]['links'][language]

  def is_direct(self, origin):
    return self.origin[origin]['is_direct']

  def get_city_country_key(self):
    return get_city_country_key(self.name['en'], self.country['en'])

  def __str__(self):
    return self.name['en']

  def __repr__(self):
    return self.name['en']

  def as_py(self):
    s = ['SwissCity(']
    for key, value in vars(self).items():
      s.append(f'{key}={repr(value)},')
    s.append(')')
    return ''.join(s)


SWISS_CITIES = [SwissCity(**i) for i in DATA]
SWISS_CITY_ID_MAP = {c.id: c for c in SWISS_CITIES}
SWISS_CITY_PLACE_ID_MAP = {c.place_id: c for c in SWISS_CITIES}

SWISS_CITY_NAME_MAP = {c.get_city_country_key(): c for c in SWISS_CITIES}

def find_city(city: str, country: str) -> Optional[SwissCity]:
  key = get_city_country_key(city, country)
  return SWISS_CITY_NAME_MAP.get(key)

SWISS_CITY_GEO_INDEX = GeoIndex(
    lambda city: (city.location['lat'], city.location['lng'])
)
for city in SWISS_CITIES:
  if city.location:
    SWISS_CITY_GEO_INDEX.add(city)

def filter_cities(
    cities: List[SwissCity],
    origin: str,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
) -> List[SwissCity]:
  result = []
  for city in cities:
    if city.disabled:
      continue
    if city.origin.get(origin) is None:
      continue
    if city.round_trip_price is not None:
      if min_price and city.round_trip_price < min_price:
        continue
      if max_price and city.round_trip_price > max_price:
        continue
    result.append(city)
  return result


def get_price_range(cities: List[SwissCity]) -> Tuple[int, int]:
  max_price = float('-inf')
  min_price = float('inf')
  for city in cities:
    if city.round_trip_price is None:
      continue
    if city.round_trip_price > max_price:
      max_price = city.round_trip_price
    if city.round_trip_price < min_price:
      min_price = city.round_trip_price
  return (int(min_price), int(max_price))
