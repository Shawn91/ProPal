from enum import Enum


class Error(str, Enum):
    UNKNOWN = 'UNKNOWN'
    API_CONNECTION = 'APIConnectionError'
