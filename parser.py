"""Parser for bot output.

A hand-rolled parser to parse "function" calls emitted by the LLM.
"""

import re
from typing import Any, Dict, Tuple


class CallSpec(object):

  def __init__(self, name: str, args: Dict[str, Any]):
    self.name: str = name
    self.args: Dict[str, Any] = args

  def __repr__(self):
    args = ', '.join(
        list(map(lambda i: f'{i[0]}:{repr(i[1])}', self.args.items()))
    )
    return f'{self.name}({args})'

class FunctionCallParser(object):

  class Result(object):
    OK = 1
    ERROR = 2

    def __init__(self, value):
      if type(value) == str:
        self.status = FunctionCallParser.Result.ERROR
      else:
        self.status = FunctionCallParser.Result.OK
      self.value = value

    def ok(self):
      return self.status == FunctionCallParser.Result.OK

  _ws_re = re.compile(r'\s*', re.MULTILINE)
  _name_re = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*', re.MULTILINE)
  _int_re = re.compile(r'0|[1-9][0-9]*')

  def __init__(self, s: str, pos: int = 0):
    self._s = s
    self._pos = pos

  def _consume_ws(self):
    match = FunctionCallParser._ws_re.match(self._s, self._pos)
    if match:
      self._pos = match.end()

  def _consume(self, c: str):
    self._consume_ws()
    if (
        self._pos < len(self._s)
        and self._s.find(c, self._pos, self._pos + len(c)) == self._pos
    ):
      self._pos += len(c)
      return True
    return False

  def _consume_string(self):
    s = ''
    delimiter = None
    if self._consume('"'):
      delimiter = '"'
    elif self._consume("'"):
      delimiter = "'"
    else:
      return None
    escape = False
    while self._pos < len(self._s):
      if escape:
        s += self._s[self._pos]
        escape = False
      elif self._s[self._pos] == delimiter:
        self._pos += 1
        return s
      elif self._s[self._pos] == '\\':
        escape = True
      else:
        s += self._s[self._pos]
      self._pos += 1
    return None

  def _peek(self):
    if self._pos >= len(self._s):
      return None
    self._consume_ws()
    return self._s[self._pos]

  def _match(self, compiled_re: re.Pattern):
    self._consume_ws()
    match = compiled_re.match(self._s, self._pos)
    if match:
      self._pos = match.end()
      return match.group()
    return None

  def _parse_list(self):
    value_type = None
    value = []
    self._consume('[')

    next_ch = self._peek()
    if next_ch == ']':
      self._consume(next_ch)
      return value

    while True:
      match = self._match(FunctionCallParser._int_re)
      if match:
        if value_type and value_type != 'int':
          # Mixed types in lists are not allowed.
          raise ValueError('Mixed types in list')
        value_type = 'int'
        value.append(int(match))
      else:
         match = self._consume_string()
         if not match is None:
           if value_type and value_type != 'str':
             # Mixed types in lists are not allowed.
             raise ValueError('Mixed types in list')
           value_type = 'str'
           value.append(match)
         else:
           raise ValueError(f'Expected an int or str, got {self._peek()}')
      next_ch = self._peek()
      if next_ch == ']':
        self._consume(next_ch)
        return value
      if next_ch == ',':
        self._consume(next_ch)
      else:
        raise ValueError(f'Expected a , or ], got {next_ch}')

  def parse(self) -> Result:
    FN_NAME = 1
    FN_ARGS = 2
    state = FN_NAME

    fn_name = None
    fn_args = {}
    while self._pos < len(self._s):
      if state == FN_NAME:
        match = self._match(FunctionCallParser._name_re)
        if match and self._consume('('):
          fn_name = match
          state = FN_ARGS
        else:
          return FunctionCallParser.Result(f"Expected '(' at {self._pos}")
        continue
      if state == FN_ARGS:
        if self._peek() == ')':
          # No arguments, so we are done.
          return FunctionCallParser.Result(CallSpec(fn_name, fn_args))
        name = None
        value = None
        # Parse the argument name.
        match = self._match(FunctionCallParser._name_re)
        if match and self._consume(':'):
          name = match
          if name in fn_args:
            return FunctionCallParser.Result(
                f'Argument {name} specified multiple times at {self.pos}'
            )
        else:
          return FunctionCallParser.Result(f"Expected ':' at {self._pos}")
        # Parse the arg value, which can either be an int, a str or a list
        # of these.
        if self._peek() == '[':
          try:
            value = self._parse_list()
          except ValueError as e:
            return FunctionCallParser.Result(
                f'Malformatted list at {self._pos}, {e}'
            )
          if value is None:
            return FunctionCallParser.Result(
                f'Malformatted list at {self._pos}'
            )
        else:
          match = self._match(FunctionCallParser._int_re)
          if match:
            value = int(match)
          else:
            match = self._consume_string()
            if not match is None:
              value = match
            else:
              return FunctionCallParser.Result(
                  f'Expected an int or str at {self._pos}'
              )
        fn_args[name] = value
        # Match the terminating comma or parenthesis, which concludes the parse.
        next_ch = self._peek()
        if next_ch == ',':
          self._consume(',')
          continue
        elif next_ch == ')':
          return FunctionCallParser.Result(CallSpec(fn_name, fn_args))
        else:
          return FunctionCallParser.Result(
              f"Expected a ',' or ')' at {self._pos}"
          )
    return FunctionCallParser.Result('Input ended prematurely')


if __name__ == '__main__':
  s = r"""listComponents(attr:1231,
             attr2:"value2", attr3:"value3")"""
  p = FunctionCallParser(s)
  print(p.parse().value)
