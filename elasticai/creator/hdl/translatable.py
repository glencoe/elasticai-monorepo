from abc import abstractmethod
from typing import Iterable, Protocol


class Translatable(Protocol):
    @abstractmethod
    def translate(self) -> "Saveable":
        ...


class Saveable(Protocol):
    @abstractmethod
    def save_to(self, destination: "Path"):
        ...


class Path(Protocol):
    @abstractmethod
    def as_file(self, suffix: str) -> "File":
        ...

    @abstractmethod
    def create_subpath(self, subpath_name: str) -> "Path":
        ...


class File(Protocol):
    @abstractmethod
    def write_text(self, text: Iterable[str]) -> None:
        ...
