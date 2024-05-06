# pytype: disable=attribute-error

import json
import requests
from typing import Any, Dict, List, Optional
import os
import time

from flask import Flask, Response, abort, render_template, request, stream_with_context
from flask_babel import Babel, gettext
from flask_assets import Bundle, Environment


from suggestion_card_data import SUGGESTION_CARDS

# Set up Cloud logging
# This needs to be done before importing the Python logging library.
import google.cloud.logging
logging_client = google.cloud.logging.Client()
logging_client.setup_logging()
import logging

from model import CachingWrapper, NoPrompt, ORSAPrompt, SimplePrompt, StreamingPrompt
from plugin import PluginDict
import city_bot
import city_events
import itinerary
import languages
import swiss_bot
import validation

GOOGLE_ANALYTICS_ID = 'G-14LY0RKPNQ'
ENABLE_CACHING = True

# Important: If changed, also update ENABLE_SUGGESTION_CARDS in index.js
ENABLE_SUGGESTION_CARDS = True

def get_locale():
  supported_languages = languages.supported_languages.keys()
  language = request.args.get('l')
  return (
      language
      if language is not None and language in supported_languages
      else request.accept_languages.best_match(supported_languages)
  )


app = Flask(__name__)
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './translations'
babel = Babel(app)
babel.init_app(app, locale_selector=get_locale)

bundles = {
    'index_js': Bundle(
        'filters.js',
        'script.js',
        'swiss.js',
        output='app/index.js',
        filters='rjsmin'),

    'index_css': Bundle(
        'third_party/index.css',
        'style.css',
        'third_party/slider.css',
        'swiss-style.css',
        'suggestion-cards.css',
        output='app/index.css',
        filters='rcssmin'),
}

assets = Environment(app)
assets.register(bundles)

class Factory:

  def __init__(
      self, name: str, cls: type, params: Dict[str, Any], cache: bool = False
  ):
    self.name: str = name
    self._cls: type = cls
    self._params: Dict[str, Any] = params
    self._cache: cache = cache

  def create(self):
    prompt = self._cls(**self._params)
    if ENABLE_CACHING and self._cache:
      prompt = CachingWrapper(prompt, f'{self.name}_cache')
    return prompt


bot_factories = [
    Factory(
        name='swiss',
        cls=ORSAPrompt,
        params={
            'bot_params': swiss_bot.BOT_PARAMS,
            'context_prompt': swiss_bot.BOT_PROMPT,
            'prompt_generator': swiss_bot.generate_prompt,
            'plugins': swiss_bot.PLUGINS,
            'renderer': swiss_bot.render,
        },
    ),
    Factory(
        name='cities',
        cls=SimplePrompt,
        params={
            'bot_params': city_bot.CURATOR_BOT_PARAMS,
            'context_prompt': city_bot.CURATOR_BOT_PROMPT,
            'prompt_generator': city_bot.curator_generate_prompt,
            'renderer': city_bot.curator_render_response,
        },
        cache=True,
    ),
    Factory(
        name='city_lookup',
        cls=NoPrompt,
        params={
            'generator': city_bot.city_lookup_generator,
            'renderer': city_bot.city_lookup_renderer,
        },
    ),
    Factory(
        name='city_summary',
        cls=SimplePrompt,
        params={
            'bot_params': city_bot.SUMMARY_BOT_PARAMS,
            'context_prompt': city_bot.SUMMARY_BOT_PROMPT,
            'prompt_generator': city_bot.summary_generate_prompt,
            'renderer': city_bot.summary_render_response,
        },
        cache=True,
    ),
    Factory(
        name='city_itinerary',
        cls=StreamingPrompt,
        params={
            'bot_params': itinerary.ITINERARY_BOT_PARAMS,
            'context_prompt': itinerary.ITINERARY_BOT_PROMPT,
            'prompt_generator': itinerary.generate_prompt,
            'renderer': itinerary.render_response,
            'stream_handler': itinerary.stream_handler,
        },
    ),
    Factory(
        name='city_events',
        cls=SimplePrompt,
        params={
            'bot_params': city_events.EVENTS_BOT_PARAMS,
            'context_prompt': city_events.EVENTS_BOT_PROMPT,
            'prompt_generator': city_events.generate_prompt,
            'renderer': city_events.render_response,
        },
        cache=True,
    ),
    Factory(
        name='places',
        cls=NoPrompt,
        params={
            'generator': itinerary.generate_places,
            'renderer': itinerary.render_places,
        },
    ),
    Factory(
        name='validation',
        cls=SimplePrompt,
        params={
            'bot_params': validation.VALIDATION_BOT_PARAMS,
            'context_prompt': validation.VALIDATION_BOT_PROMPT,
            'prompt_generator': validation.generate_prompt,
            'renderer': validation.render_response,
        },
    ),
]


def create_bot(bot_name: str):
  for b in bot_factories:
    if b.name == bot_name:
      return b.create()
  return None


@app.route("/proxy", methods=["GET", "POST"])
def proxy():
  data = request.json
  if not data or not ('backend' in data and 'args' in data):
    return ''

  r = requests.post(data['backend'], json=data['args'])
  if not r.ok:
    return str(r.status_code) + ': ' + r.reason
  return r.json()


@app.route("/newsletter")
def newsletter():
  BACKEND = 'https://swiss-ai-newsletter-demo-dot-gain-in-cx.uc.r.appspot.com/newsletter'
  params = {}
  if len(request.args) == 0:
    return render_template('newsletter.html')
  origin = request.args.get('o')
  if not origin:
    params['error'] = 'Origin missing'
    return render_template('newsletter.html', **params)
  params['origin'] = origin

  destination = request.args.get('d')
  if not destination:
    params['error'] = 'Destination missing'
    return render_template('newsletter.html', **params)
  params['destination'] = destination

  language = request.args.get('l')
  if language:
    params['language'] = language

  interest = request.args.get('i')
  if interest:
    params['interest'] = interest

  r = requests.post(BACKEND, json=params)
  if not r.ok:
    params['error'] = str(r.status_code) + ': ' + r.reason
    return render_template('newsletter.html', **params)
  return r.json()['rawHtml']


@app.route("/")
def index():
  return render_template(
      'index.html', ga_id=GOOGLE_ANALYTICS_ID,
      suggestion_cards_enabled=ENABLE_SUGGESTION_CARDS,
      suggestion_cards=SUGGESTION_CARDS,
  )


@app.route("/<bot_name>", methods=["GET", "POST"])
def run_bot(bot_name):
  bot = create_bot(bot_name)
  if not bot:
    return render_template(
        'index.html',
        error=f'No bots registered with name {bot_name}',
    )

  bot_params = {'language': get_locale()}
  if request.method == 'GET':
    bot_params.update(dict(request.args.lists()))
  else:
    bot_params.update(request.get_json())
  response = bot.query(bot_params)
  return bot.render_response(response)


@app.route("/city_itinerary",methods=["GET", "POST"])
def itineraries():
  bot = create_bot('city_itinerary')

  bot_params = {'language': get_locale()}
  if request.method == 'GET':
    bot_params.update(dict(request.args.lists()))
  else:
    bot_params.update(request.get_json())

  def generate():
    for response in bot.query(bot_params):
      yield bot.render_response(response)

  response = Response(stream_with_context(generate()))
  response.headers['X-Accel-Buffering'] = 'no'
  return response


if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
