from __future__ import annotations

from collections import UserDict
from enum import StrEnum, auto
from typing import Protocol

# from adiumentum.num import round5

type IDType = str


class DurationType(StrEnum):
    MIN = auto()
    NORMAL = auto()
    IDEAL = auto()
    MAX = auto()


class NoteProtocol(Protocol):
    @property
    def id(self) -> str: ...
    @property
    def scheduling_contexts(self) -> set[str]: ...
    @property
    def normalTime(self) -> int: ...
    @property
    def idealTime(self) -> int: ...
    @property
    def minTime(self) -> int: ...
    @property
    def maxTime(self) -> int: ...
    @property
    def priority(self) -> float: ...
    @property
    def text(self) -> str: ...
    @property
    def link(self) -> str: ...


class NotesProtocol(UserDict[str, NoteProtocol]): ...
