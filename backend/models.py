from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Tuple, Dict


class Error(str, Enum):
    UNKNOWN = "UNKNOWN"
    API_CONNECTION = "APIConnectionError"


@dataclass
class Match:
    """a search result from database, memory, hard disk, or other sources"""

    source: str = ""  # database, setting, commands, etc...
    category: str = ""  # prompt, command, etc...
    data: Any = None  # a Prompt instance, a Command instance, etc...
    # fields that match the search string, e.g. ["name", "description"]
    match_fields: List[str] = field(default_factory=list)
    match_fields_values: Dict[str, Any] = field(default_factory=dict)  # corresponding values of match_fields
    match_positions: Dict[str, List[Tuple[int, int]]] = field(default_factory=dict)  # positions of matches
