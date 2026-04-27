from abc import ABC
from collections.abc import Iterable

from ...protocols import PartitionProtocol, SpanProtocol, TimeProtocol


class AbstractPartition[T: TimeProtocol](PartitionProtocol, ABC):
    def __init__(
        self,
        spans: Iterable[SpanProtocol[T]],
        names: Iterable[str | None] | None = None,
    ) -> None: ...
