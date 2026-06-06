from __future__ import annotations

import re
from typing import Callable

Validator = Callable[[set[str]], bool]


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
    if re.search(r"[^A-Za-z0-9_,.()\s]", expr):
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

Token = str  # one of: ATOM, '(', ')', ',', '.'


def _tokenise(expr: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_]+|[(),.]", expr.replace(" ", ""))


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


class _Parser:
    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected: str | None = None) -> str:
        tok = self.tokens[self.pos]
        if expected is not None and tok != expected:
            raise ValueError(f"Expected {expected!r}, got {tok!r}")
        self.pos += 1
        return tok

    def parse(self) -> Validator:
        v = self.parse_expr()
        if self.pos != len(self.tokens):
            raise ValueError(f"Unexpected token: {self.peek()!r}")
        return v

    def parse_expr(self) -> Validator:
        """Top-level: may be AND-chain, OR-chain, or single atom/group."""
        left = self.parse_term()

        if self.peek() == ".":
            # AND chain
            operands = [left]
            while self.peek() == ".":
                self.consume(".")
                operands.append(self.parse_term())
            return _all_of(operands)

        if self.peek() == ",":
            # OR chain (top-level bare comma list)
            operands = [left]
            while self.peek() == ",":
                self.consume(",")
                operands.append(self.parse_term())
            return _any_of(operands)

        return left

    def parse_term(self) -> Validator:
        """A term is either a parenthesised OR-group or a bare atom."""
        if self.peek() == "(":
            self.consume("(")
            # Inside parens: must be a comma-separated OR list
            first = self.parse_atom()
            operands = [first]
            while self.peek() == ",":
                self.consume(",")
                operands.append(self.parse_atom())
            self.consume(")")
            return _any_of(operands)
        return self.parse_atom()

    def parse_atom(self) -> Validator:
        tok = self.peek()
        if tok is None or not re.fullmatch(r"[A-Za-z0-9_]+", tok):
            raise ValueError(f"Expected atom, got {tok!r}")
        self.consume()
        return lambda s, t=tok: t in s


# ---------------------------------------------------------------------------
# Combinator helpers
# ---------------------------------------------------------------------------

def _all_of(validators: list[Validator]) -> Validator:
    return lambda s: all(v(s) for v in validators)

def _any_of(validators: list[Validator]) -> Validator:
    return lambda s: any(v(s) for v in validators)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_context(context_expression: str) -> Validator:
    """
    Parse an AND/OR expression into a validator.

        parse("a.b")({"a", "b"})       # True  — AND
        parse("a,b")({"a"})            # True  — OR
        parse("(a,b).c")({"a", "c"})  # True  — (a OR b) AND c
    """
    check_syntax(context_expression)
    tokens = _tokenise(context_expression)
    return _Parser(tokens).parse()
