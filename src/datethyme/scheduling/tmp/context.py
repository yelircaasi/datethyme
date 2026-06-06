from __future__ import annotations

from ast import And
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, StrEnum, auto
import re
from typing import Callable, Literal
from wsgiref import validate

from adiumentum.collections import FrozenDict
from adiumentum.fp import sfilter, smap

UNIVERSAL_CONTEXT: str = "_any"
LOCKED_CONTEXT: str = "_locked"

type ContextValidator = Callable[[set[str]], bool]
type Aggregator = Callable[[Iterable[ContextValidator]], ContextValidator]


def trivial_validator(_: object) -> bool:
    return True


def _locked_validator(_: object) -> bool:
    return False


def _all_of(validators: Iterable[ContextValidator]) -> ContextValidator:
    def inner(ss: set[str]) -> bool:
        for v in validators:
            if not v(ss):
                print(False, v)
                return False
        return True
    
    return inner


def _any_of(validators: Iterable[ContextValidator]) -> ContextValidator:
    def inner(ss: set[str]) -> bool:
        for v in validators:
            if v(ss):
                print(True, v)
                return True
        return False

    return inner


# ---------------------------------------------------------------------------
# Regex: catch obvious violations before parsing
# ---------------------------------------------------------------------------

VALID_RE = re.compile(
    r"""
    ^
    (?:
        # A single atom (no operators)
        [A-Za-z0-9_]+
        |
        # One or more dot-joined atoms or parenthesised groups
        (?:[A-Za-z0-9_]+|\([A-Za-z0-9_]+(?:,[A-Za-z0-9_]+)+\))
        (?:\.(?:[A-Za-z0-9_]+|\([A-Za-z0-9_]+(?:,[A-Za-z0-9_]+)+\)))*
        |
        # A bare comma-list (OR at top level)
        [A-Za-z0-9_]+(?:,[A-Za-z0-9_]+)+
    )
    $
    """,
    re.VERBOSE,
)


def check_syntax(expr: str) -> None:
    """Raise ValueError on obvious syntax violations."""
    expr = expr.strip()
    if not expr:
        raise ValueError("Empty expression.")
    if re.search(r"[^A-Za-z0-9_&|,.()\s]", expr):
        raise ValueError(f"Illegal character in expression: {expr!r}")
    if re.search(r"\(\)", expr):
        raise ValueError("Empty parentheses.")
    if re.search(r"[.,][.,]", expr):
        raise ValueError("Adjacent operators.")
    if re.search(r"[.(,][)]|[(][.,)]", expr):
        raise ValueError("Operator adjacent to parenthesis.")
    if not VALID_RE.match(expr.replace(" ", "")):
        raise ValueError(
            f"Invalid expression {expr!r}. "
            "Use 'a.b' (AND), 'a,b' (OR), with parentheses for mixed operators."
        )


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------


def _tokenize(expr: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_]+|[(),.&\|]", expr.replace(" ", ""))


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------
# Grammar (after syntax check guarantees no mixed bare operators):
#
#   expr   ::= and_expr | or_expr | atom
#   and_expr ::= term ('.' term)+
#   or_expr  ::= atom (',' atom)+          -- only at top level OR inside ()
#   term   ::= '(' or_expr ')' | atom
#   atom   ::= [A-Za-z0-9_]+


@dataclass
class _Symbols:
    main: str
    secondary: str
    # tertiary: str

    def __hash__(self) -> int:
        return hash((self.main, self.secondary))
    
    def __contains__(self, elem: object) -> bool:
        return (elem == self.main) or (elem == self.secondary)


class Token(_Symbols, Enum):
    AND = ".", "&"
    OR = ",", "|"
    LEFT = "(", "{"
    RIGHT = ")", "}"


type Operator = Literal[Token.AND] | Literal[Token.OR]


class Tokens(list[str]):
    def next_is(self, tok: Token) -> bool:
        if not self:
            return False
        return self[0] in tok.value

    def consume(self, tok: Token | None = None) -> str:
        print(f"Consuming {self[0]}")
        if tok is None:
            return self.pop(0)
        if not self.next_is(tok):
            raise ValueError(f"Expected {tok}; got {self[0]}.")
        return self.pop(0)

    def consume_op(self) -> Operator:
        if self.next_is(Token.AND):
            self.consume()
            return Token.AND
        if self.next_is(Token.OR):
            self.consume()
            return Token.OR
        raise ValueError

    def peek_op(self) -> Operator:
        if self.next_is(Token.AND):
            return Token.AND
        if self.next_is(Token.OR):
            return Token.OR
        raise ValueError(f"Expected operator; got {self[0]}")

    def peek(self) -> str | None:
        if not self:
            return None
        return self[0]


class _Parser:
    def __init__(self, tokens: list[str]) -> None:
        self.tokens = Tokens(tokens)
        # self.pos = 0

    # def peek(self) -> str | None:
    #     if not
    #     return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    # def next_is_and(self) -> bool:
    #     next_ = self.peek()
    #     if not next_:
    #         return False
    #     return next_ in {".", "&"}

    # def next_is_left(self) -> bool:
    #     next_ = self.peek()
    #     if not next_:
    #         return False
    #     return next_ == "("

    # def next_is_right(self) -> bool:
    #     next_ = self.peek()
    #     if not next_:
    #         return False
    #     return next_ == ")"

    # def next_is_or(self) -> bool:
    #     next_ = self.peek()
    #     if not next_:
    #         return False
    #     return next_ in {",", "|"}

    # def consume_left(self) -> None:
    #     tok = self.tokens[self.pos]
    #     if tok != "(":
    #         raise ValueError(f"Expected '(', got {tok!r}")
    #     self.pos += 1
    #     return tok

    # def consume_right(self) -> None:
    #     tok = self.tokens[self.pos]
    #     if tok != ")":
    #         raise ValueError(f"Expected ')', got {tok!r}")
    #     self.pos += 1
    #     return tok

    # def consume_and(self) -> None:
    #     tok = self.tokens[self.pos]
    #     if tok not in {".", "&"}:
    #         raise ValueError(f"Expected AND, got {tok!r}")
    #     self.pos += 1
    #     return tok

    # def consume_or(self) -> None:
    #     tok = self.tokens[self.pos]
    #     if tok not in {",", "|"}:
    #         raise ValueError(f"Expected OR, got {tok!r}")
    #     self.pos += 1
    #     return tok

    # def consume(self, expected: str | None = None) -> str:
    #     tok = self.tokens[self.pos]
    #     if expected is not None and tok != expected:
    #         raise ValueError(f"Expected {expected!r}, got {tok!r}")
    #     self.pos += 1
    #     return tok

    def parse(self) -> ContextValidator:
        v = self.parse_expressions()
        # if self.pos != len(self.tokens):
        #     raise ValueError(f"Unexpected token: {self.tokens.peek()!r}")
        return v

    def parse_expressions(self) -> ContextValidator:
        if self.tokens.next_is(Token.LEFT):
            first = self.parse_bracketed()
        else:
            first = self.parse_atom()
        operands = [first]

        if self.tokens:
            op = self.tokens.peek_op()
            print(op)
            while self.tokens and self.tokens.next_is(op):
                self.tokens.consume_op()
                term = self.parse_bracketed()
                operands.append(term)

        aggregator = self.get_aggregator(op)
        print("aggregator", aggregator)
        return aggregator(operands)

    def parse_bracketed(self) -> ContextValidator:
        """A term is either a parenthesised OR-group or a bare atom."""
        if self.tokens.next_is(Token.LEFT):
            print("IN LEFT LOOP")
            self.tokens.consume(Token.LEFT)
            parsed = self.parse_expressions()
            self.tokens.consume(Token.RIGHT)
        else:
            parsed = self.parse_atom()

        print("IN ATOM LOOP")
        return parsed

    def get_aggregator(self, op: Operator) -> Aggregator:
        return {
            Token.AND: _all_of,
            Token.OR: _any_of,
        }[op]

    def parse_atom(self) -> ContextValidator:
        tok = self.tokens.peek()
        print(f"{tok=}")
        if tok is None or not re.fullmatch(r"[A-Za-z0-9_]+", tok):
            raise ValueError(f"Expected atom, got {tok!r}")
        self.tokens.consume()
        return self._condition_from_atom(tok)

    @staticmethod
    def _condition_from_atom(context: str) -> ContextValidator:
        def inner(ss: set[str]) -> bool:
            return context in ss

        return inner


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------




def make_context_validator(context_expression: str, child_mapper: dict[str, str]) -> ContextValidator:
    """
    Parse an AND/OR expression into a validator.

        parse("a.b")({"a", "b"})       # True  — AND
        parse("a,b")({"a"})            # True  — OR
        parse("(a,b).c")({"a", "c"})  # True  — (a OR b) AND c
    """
    if context_expression == LOCKED_CONTEXT:
        return _locked_validator
    if context_expression == UNIVERSAL_CONTEXT:
        return trivial_validator

    check_syntax(context_expression)
    tokens = _tokenize(context_expression)
    print(tokens)
    validator = _Parser(tokens).parse()

    def validate_contexts(child_contexts: set[str]) -> bool:
        # CONTEXT_MAPPER: dict[str, str] = 
        mapped_contexts = child_contexts | {c for c in map(child_mapper.get, child_contexts) if c is not None}

        return validator(mapped_contexts)

    return validate_contexts


cf = make_context_validator("a.b.(c,d)", {})
a = cf({"a"})
ab = cf({"a", "b"})
abc = cf({"a", "b", "c"})
abd = cf({"a", "b", "d"})
abe = cf({"a", "b", "e"})

assert not a
assert not ab
assert abc
assert abd
assert not abe

'''
# TODO: add context expression parser and integrate it with 'virtual contexts',
#     i.e. special values such as '_any' and '_locked'
def resolve_contexts(
    parent_contexts: set[str] | None, child_contexts: set[str], none_means_any: bool = False
) -> set[str]:
    if none_means_any and (parent_contexts is None):
        return {"_any"}

    parent_contexts = parent_contexts or set()
    if "_any" in parent_contexts:
        return {"_any"}

    if "_locked" in parent_contexts:
        return set()

    CONTEXT_MAPPER: dict[str, str] = {"lds": "project", "plt": "project"}

    mapped_contexts = child_contexts | sfilter(smap(CONTEXT_MAPPER.get, child_contexts))
    return parent_contexts.intersection(mapped_contexts)
'''