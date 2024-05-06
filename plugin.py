"""A plugin defines a set of function calls made available to an LLM.

This class contains the necessary support for exposing the functionality to
the LLM as well as executing its response.
"""

from enum import Enum
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from typing import get_origin, get_args

from parser import CallSpec


class Plugin(object):

  # Plugins should return this string if they are expecting input from the user.
  YIELD_RESPONSE = "__yield__"

  ALLOWED_PARAM_TYPES = set([int, str, List[int], List[str]])

  def __init__(
      self,
      fn: Callable,
      description: Optional[str] = None,
      renderer: Optional[Callable] = None,
  ):
    self.fn: Callable = fn
    self.description: Optional[str] = description
    self.renderer: Optional[Callable] = renderer
    self.expected_types = {}

    for name, param in inspect.signature(fn).parameters.items():
      # Strip away Optional on the type annotation.
      expected_type = param.annotation
      if (get_origin(expected_type) == Union
          and len(get_args(expected_type)) == 2
          and get_args(expected_type)[1] == type(None)):
        expected_type = get_args(expected_type)[0]
      if (
          not expected_type in __class__.ALLOWED_PARAM_TYPES
          and not param.kind == inspect.Parameter.VAR_KEYWORD
      ):
        raise ValueError(
            f"Parameter {name} has an unsupported type {param.annotation}. The"
            f" supported types are {__class__.ALLOWED_PARAM_TYPES}"
        )
      self.expected_types[name] = expected_type

  def type_check(self, name: str, value: Any):
    expected_type = self.expected_types.get(name)
    if not expected_type:
      raise ValueError(f"Does not have a parameter called {name}")
    value_type = type(value)

    # Strip away List on the type of the value.
    if value_type == list:
      if not get_origin(expected_type) == list:
        raise ValueError(f"Expected a basic type for '{name}' but got a list")
      if len(value) > 0:
        value_type = type(value[0])
        expected_type = get_args(expected_type)[0]

    if value_type != expected_type:
      raise ValueError(
          f"Expected {expected_type} for '{name}', but got {value_type}"
    )

  def populate_default_args(self, args: Dict[str, Any]):
    for name, param in inspect.signature(self.fn).parameters.items():
      if param.default is param.empty:
        continue
      if name in args.keys():
        continue
      args[name] = param.default


class PluginDict(object):

  def __init__(self, plugins: List[Plugin]):
    self._plugins = {}
    for plugin in plugins:
      fn_name = plugin.fn.__name__
      if not fn_name:
        raise ValueError("All plugins must have a name")
      if fn_name in self._plugins.keys():
        raise ValueError(f"A plugin with name {fn_name} already exists")
      self._plugins[fn_name] = plugin

  def call_plugin(self, call_spec: CallSpec) -> str:
    plugin = self._plugins.get(call_spec.name)
    if not plugin:
      raise ValueError(f"No plugins defined with name '{call_spec.name}'")
    valid_args = {}
    for name, value in call_spec.args.items():
      try:
        plugin.type_check(name, value)
        valid_args[name] = value
      except ValueError as e:
        logging.exception("Type error for %s: %s", call_spec.name, e)

    return self._plugins[call_spec.name].fn(**valid_args)

  def render_output(
      self, call_spec: CallSpec, response: Any, state_dict: Dict[str, Any]
  ) -> Dict[str, Any]:
    if not call_spec.name in self._plugins:
      raise ValueError(f"No plugins defined with name {call_spec.name}")
    if not self._plugins[call_spec.name].renderer:
      raise ValueError(f"Plugin {call_spec.name} does not have a renderer")
    state_dict['intent'] = call_spec.name
    params = dict(call_spec.args)
    plugin = self._plugins[call_spec.name]
    plugin.populate_default_args(params)
    state_dict[call_spec.name] = params
    return plugin.renderer(response, state_dict)


if __name__ == "__main__":

  def fun(
      i: int,
      s: str,
      oi: Optional[int],
      ls: Optional[List[str]] = None,
      d: int = 5,
  ):
    pass

  def render(_, tpl_dict):
    print(tpl_dict)

  pd = PluginDict([Plugin(fn=fun, description="", renderer=render)])
  call_spec = CallSpec("fun", {"i": 5, "s": "4", "oi": 12, "ls": ["12"]})
  pd.call_plugin(call_spec)
  pd.render_output(call_spec, None, {})
