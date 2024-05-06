"""Basic connector for talking to the LLM.

This library provides the bare essentials of interacting with the LLM.
"""

import base64
import concurrent.futures
import datetime
import json
import logging
import os
import pickle
import random
import re
from typing import Any, Callable, Dict, List, Optional
import uuid

from flask import Flask, render_template, request

import google.auth
from google.cloud import datastore
import vertexai
from vertexai.language_models import TextGenerationModel

from parser import CallSpec, FunctionCallParser
from plugin import Plugin, PluginDict


class Model:
  LOCATION = 'us-central1'

  def __init__(
      self,
      model,
      temperature: float,
      max_output_tokens: int,
      top_p: float,
      top_k: int,
      candidate_count: int = 1,
      response_parser: Callable[[str], Any] = lambda s: s,
      candidate_merger: Callable[[List[Any]], Any] = lambda lc: lc[0],
      streaming_enabled: bool = False,
  ):
    self._temperature: float = temperature
    self._max_output_tokens: int = max_output_tokens
    self._top_p: float = top_p
    self._top_k: int = top_k
    self._candidate_count: int = candidate_count
    self._response_parser: Callable[[str], Any] = response_parser
    self._candidate_merger: Callable[[List[Any]], Any] = candidate_merger
    self._streaming_enabled: bool = streaming_enabled

    credentials, project_id = google.auth.default()
    vertexai.init(
        project=project_id,
        location=Model.LOCATION,
        credentials=credentials,
    )
    self._model = TextGenerationModel.from_pretrained(model)

  def query(self, query: str) -> str:
    parameters = {
        'temperature': self._temperature,
        'max_output_tokens': self._max_output_tokens,
        'top_k': self._top_k,
        'top_p': self._top_p,
    }
    if not self._streaming_enabled:
      parameters['candidate_count'] = self._candidate_count

    try:
      if self._streaming_enabled:
        return self._model.predict_streaming(query, **parameters)

      response = self._model.predict(query, **parameters)

    except Exception as exception:
      logging.error(f'Vertex AI exception: {exception}')
      return None
    candidates = (
        [response] if self._candidate_count == 1 else response.candidates
    )
    parsed_candidates = []
    for candidate in candidates:
      parsed_candidate = self._response_parser(candidate.text)
      if parsed_candidate is not None:
        parsed_candidates.append(parsed_candidate)
    output = self._candidate_merger(parsed_candidates)
    logging.info(f'Model output {output}')
    return output


class ModelResponse:

  def has_error() -> bool:
    raise NotImplementedError

  def get_error() -> str:
    raise NotImplementedError


class SimplePrompt:

  class Response(ModelResponse):

    def __init__(self, value, prompt_params):
      self.value = value
      self.prompt_params = prompt_params

    def has_error(self):
      return False

  def __init__(
      self,
      bot_params: Dict[str, Any],
      context_prompt: str,
      prompt_generator: Callable[[Dict[str, Any]], Dict[str, str]],
      renderer: Callable[[str, Dict[str, Any]], str],
  ):
    self._model = Model(**bot_params)
    self._context_prompt = context_prompt
    self._prompt_generator = prompt_generator
    self._renderer = renderer

  def query(self, params: Dict[str, Any]):
    prompt_dict = self._prompt_generator(**params)
    if not prompt_dict:
      return SimplePrompt.Response(None, params)
    prompt = self._context_prompt.format(**prompt_dict)
    response = self._model.query(prompt)
    return SimplePrompt.Response(response, prompt_dict)

  def render_response(self, response: Response) -> str:
    return self._renderer(response.value, response.prompt_params)


class StreamingPrompt:

  class Response(ModelResponse):

    def __init__(self, value, prompt_params):
      self.value = value
      self.prompt_params = prompt_params

    def has_error(self):
      return False

  def __init__(
      self,
      bot_params: Dict[str, Any],
      context_prompt: str,
      prompt_generator: Callable[[Dict[str, Any]], Dict[str, str]],
      renderer: Callable[[Any, Dict[str, Any]], str],
      stream_handler: Callable[[Any, Dict[str, Any]], Any],
  ):
    self._model = Model(**bot_params, streaming_enabled=True)
    self._context_prompt = context_prompt
    self._prompt_generator = prompt_generator
    self._renderer = renderer
    self._stream_handler = stream_handler

  def query(self, params: Dict[str, Any]):
    prompt_dict = self._prompt_generator(**params)
    prompt = self._context_prompt.format(**prompt_dict)
    responses = self._model.query(prompt)
    for partial_response in self._stream_handler(responses, prompt_dict):
      yield StreamingPrompt.Response(partial_response, prompt_dict)

  def render_response(self, response: Response) -> str:
    return self._renderer(response.value, response.prompt_params)


class ORSAPrompt:

  class Action:

    def __init__(self, call: CallSpec, response: Any):
      self.call = call
      self.response = response

    def __repr__(self):
      return repr(self.call)

  class Turn:

    def __init__(
        self, observation: str, reason: str = '', say: str = '', action=None
    ):
      self.observation: str = observation
      self.reason: str = reason
      self.say: str = say
      self.action: Optional[ORSAPrompt.Action] = action

  class Response(ModelResponse):

    def __init__(
        self,
        sid: str,
        language: str,
        turns: List[Any] = None,
        error: str = None,
    ):
      self.sid: str = sid
      self.language: str = language
      self.turns: List[ORSAPrompt.Turn] = turns
      self.error: str = error

    def has_error(self) -> bool:
      return self.error is not None

    def get_error(self):
      return self.error

  CHUNK_OBSERVE = 1
  reason_re = re.compile(
      '\s*[Oo]bserve (?P<turn>(\d+)): (?P<payload>.*)', re.MULTILINE
  )

  CHUNK_REASON = 2
  reason_re = re.compile(
      '\s*[Rr]eason (?P<turn>(\d+)): (?P<payload>.*)', re.MULTILINE
  )

  CHUNK_SAY = 3
  say_re = re.compile(
      '\s*[Ss]ay (?P<turn>(\d+)): (?P<payload>.*)', re.MULTILINE
  )

  CHUNK_ACT = 4
  act_re = re.compile(
      '\s*[Aa]ct (?P<turn>(\d+)): (?P<payload>.*)', re.MULTILINE
  )

  _datastore_client = datastore.Client()

  def __init__(
      self,
      bot_params: Dict[str, Any],
      context_prompt: str,
      prompt_generator: Callable[[Dict[str, Any]], Dict[str, str]],
      plugins: PluginDict,
      renderer: Callable[[Dict[str, Any]], str]
  ):
    self._model = Model(**bot_params)
    self._context_prompt: str = context_prompt
    self._prompt_generator = prompt_generator
    self._plugins: PluginDict = plugins
    self._renderer: Callable[[Dict[str, Any]], str] = renderer
    self._turns: List[ORSAPrompt.Turn] = []

  def query(self, params: Dict[str, Any]) -> Response:
    sid = params.get('sid')
    language = params.get('language', 'en')
    if sid is not None:
      if not self._restore_state(sid):
        return ORSAPrompt.Response(
            sid, language, error=f'No sessions found with the id {sid}',
        )
    else:
      sid = uuid.uuid4().hex

    if params.get('cancel') is not None:
      logging.info('cancelling')
      self._cancel_last_turn()
      self._save_state(sid)
      return ORSAPrompt.Response(sid, turns=self._turns)

    prompt_dict = self._prompt_generator(**params)
    base_prompt = self._context_prompt.format(**prompt_dict)
    q = params.get('q')
    if q is not None:
      error = self._query(q, base_prompt)
      if error:
        response = ORSAPrompt.Response(sid, language, error=error)
      else:
        response = ORSAPrompt.Response(sid, language, turns=self._turns)
    else:
      response = ORSAPrompt.Response(sid, language, turns=self._turns)
    self._save_state(sid)
    return response

  def render_response(self, response: Response) -> str:
    output_dict = {
        'sid': response.sid,
        'language': response.language,
    }
    if response.has_error():
      output_dict['error'] = response.get_error()
      return output_dict

    state_dict = {}
    if response.turns is not None:
      for turn in response.turns:
        if turn.say:
          output_dict.setdefault('say', [])
          output_dict['say'].append(turn.say)
        if turn.action:
          self._plugins.render_output(
              turn.action.call, turn.action.response, state_dict
          )
    output_dict['state'] = state_dict
    output_dict = self._renderer(output_dict)
    return json.dumps(output_dict)

  def _chunk_output(self, output: str):
    chunks = []
    chunk_type = None
    payload = []
    for line in output.splitlines():
      match = None
      for regex in [
          (ORSAPrompt.CHUNK_REASON, ORSAPrompt.reason_re),
          (ORSAPrompt.CHUNK_SAY, ORSAPrompt.say_re),
          (ORSAPrompt.CHUNK_ACT, ORSAPrompt.act_re),
      ]:
        match = regex[1].match(line)
        if match:
          if chunk_type:
            chunks.append((chunk_type, '\n'.join(payload)))
          chunk_type = regex[0]
          payload = [match.group('payload')]
          break
      if not match:
        payload.append(line)
    if chunk_type:
      chunks.append((chunk_type, '\n'.join(payload)))
    return chunks

  def _generate_prompt(self, base_prompt: str):
    pieces = []
    for i, turn in enumerate(self._turns):
      prompt_index = i + 1  # In the prompt, indices are 1-based.
      if i == 0:
        pieces.append(turn.observation)
        pieces.append('output:')
      else:
        pieces.append(f'Observe {prompt_index}: {turn.observation}')
      if turn.reason:
        pieces.append(f'Reason {prompt_index}: {turn.reason}')
      if turn.say:
        pieces.append(f'Say {prompt_index}: {turn.say}')
      if turn.action:
        pieces.append(f'Act {prompt_index}: {repr(turn.action)}')
    logging.info(pieces)
    return '\n\n'.join([base_prompt, 'input:'] + pieces)

  def _query(self, query: str, base_prompt: str):
    self._turns.append(ORSAPrompt.Turn(observation=query))
    prompt = self._generate_prompt(base_prompt)
    response = self._model.query(prompt)

    for chunk in self._chunk_output(response):
      logging.info(chunk)
      turn = self._turns[-1]
      chunk_type, payload = chunk[0], chunk[1]
      if chunk_type == ORSAPrompt.CHUNK_REASON:
        turn.reason = payload
      elif chunk_type == ORSAPrompt.CHUNK_SAY:
        turn.say = payload
      elif chunk_type == ORSAPrompt.CHUNK_ACT:
        if payload == 'Finish':
          return
        parse_result = FunctionCallParser(payload).parse()
        if parse_result.ok():
          plugin_output = self._plugins.call_plugin(parse_result.value)
          turn.action = ORSAPrompt.Action(parse_result.value, plugin_output)
          if plugin_output != Plugin.YIELD_RESPONSE:
            self._query(str(plugin_output))
          return
        else:
          logging.error(f'Error while parsing {payload}: {parse_result.value}')
    return 'Cannot parse response'

  def _cancel_last_turn(self):
    for t in reversed(self._turns):
      turn = self._turns.pop()
      if (
          turn.action is not None
          and turn.action.response == Plugin.YIELD_RESPONSE
      ):
        break

  @classmethod
  def _create_datastore_key(cls, sid: str) -> datastore.Key:
    return cls._datastore_client.key('Bot', sid)

  def _save_state(self, sid: str) -> None:
    state = datastore.Entity(
        ORSAPrompt._create_datastore_key(sid), exclude_from_indexes=('data',)
    )
    state['data'] = pickle.dumps(self._turns)
    state['ttl'] = datetime.datetime.now() + datetime.timedelta(hours=1)
    ORSAPrompt._datastore_client.put(state)

  def _restore_state(self, sid: str) -> bool:
    entity = ORSAPrompt._datastore_client.get(
        ORSAPrompt._create_datastore_key(sid)
    )
    if not entity:
      return False
    self._turns = pickle.loads(entity['data'])
    return True


class NoPrompt:

  class Response(ModelResponse):

    def __init__(self, value: Any):
      self.value = value

    def has_error(self):
      return False

  def __init__(
      self,
      generator: Callable[[Any], Dict[str, Any]],
      renderer: Callable[[str], Response],
  ):
    self.generator = generator
    self.renderer = renderer

  def query(self, params: Dict[str, Any]) -> Response:
    return NoPrompt.Response(self.generator(params))

  def render_response(self, response: Response) -> str:
    return self.renderer(response)


class CachingWrapper:

  TTL = datetime.timedelta(days=1)
  _datastore_client = datastore.Client()

  def __init__(self, prompt: Any, cache_name: str):
    self._prompt = prompt
    self._cache_name = cache_name

  def query(self, params: Dict[str, Any]):
    cache_key = self._compute_cache_key(params)
    cached_response = self._lookup_cache(cache_key)
    if cached_response:
      return cached_response

    response = self._prompt.query(params)
    if not response.has_error():
      self._cache_response(cache_key, response)
    return response

  def render_response(self, response) -> str:
    return self._prompt.render_response(response)

  def _compute_cache_key(self, params):
    return CachingWrapper._datastore_client.key(
        self._cache_name,
        base64.b64encode(pickle.dumps(tuple(params.items()))).decode(),
    )

  def _lookup_cache(self, key):
    entity = CachingWrapper._datastore_client.get(key)
    if not entity:
      return None
    return pickle.loads(entity['data'])

  def _cache_response(self, key, response):
    entity = datastore.Entity(key, exclude_from_indexes=('data',))
    entity['data'] = pickle.dumps(response)
    entity['ttl'] = datetime.datetime.now() + CachingWrapper.TTL
    CachingWrapper._datastore_client.put(entity)
