"""A simple wrapper around the Places API client.

The sole purpose of this wrapper is to centralize the client key and to
encapsulate the session setup for increasing the number of concurrently
executing requests.
"""

import googlemaps
import requests


class PlacesApiClient:
  API_KEY = 'AIzaSyCAHmFhp0YvhTLfC3jfFkNWWPdvX3JGxDQ'

  def __init__(self):
    # Allow for additional parallelism. Without these settings, we get errors
    # for connections being dropped due to the pool being full.
    session = requests.Session()
    session.mount(
        'https://maps.googleapis.com/',
        requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=30),
    )
    session.mount(
        'https://lh3.googleusercontent.com/',
        requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=30),
    )
    self.client = googlemaps.Client(
        key=PlacesApiClient.API_KEY, requests_session=session
    )

  def place(self, **kwargs):
    return self.client.place(**kwargs)

  def find_place(self, **kwargs):
    return self.client.find_place(**kwargs)

  def places_photo(self, **kwargs):
    return self.client.places_photo(**kwargs)

  def places_autocomplete(self, **kwargs):
    return self.client.places_autocomplete(**kwargs)

  def geocode(self, place_id):
    return self.client.geocode(place_id=place_id)
