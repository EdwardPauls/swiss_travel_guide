from haversine import haversine
import logging
import math
from typing import Any, Callable, Tuple


class GeoIndex:
  def __init__(self, coords_fn: Callable[[Any], Tuple[float, float]]):
    self._map = {}
    self._coords_fn = coords_fn

  def add(self, obj: Any):
    coords = self._coords_fn(obj)
    for key in self._get_keys(coords):
      if key in self._map:
        self._map[key].append(obj)
      else:
        self._map[key] = [obj]

  def lookup(self, coords: Tuple[float, float], max_distance_km: float):
    candidates = {}
    for key in self._get_keys(coords):
      for item in self._map.get(key, []):
        candidates[item.id] = item

    results = []
    for candidate in candidates.values():
      distance_km = haversine(coords, self._coords_fn(candidate))
      if distance_km < max_distance_km:
        results.append(candidate)
    return results

  def _get_keys(self, coords: Tuple[float, float]):
    def make_key(lat: int, lng: int):
      return lat * 1000 + lng

    lat_floor = int(math.floor(coords[0]))
    lng_floor = int(math.floor(coords[1]))
    return [
        make_key(lat_floor-1, lng_floor-1),
        make_key(lat_floor-1, lng_floor),
        make_key(lat_floor-1, lng_floor+1),
        make_key(lat_floor, lng_floor-1),
        make_key(lat_floor, lng_floor),
        make_key(lat_floor, lng_floor+1),
        make_key(lat_floor+1, lng_floor-1),
        make_key(lat_floor+1, lng_floor),
        make_key(lat_floor+1, lng_floor+1),
    ]
