from typing import NotRequired, TypedDict


class WindowsSecurityEventFilterOptions(TypedDict):
    """Windows security event filter options type"""

    src_users: list[str]
    dst_users: list[str]
    groups: NotRequired[list[str]]


class WindowsSecurityEventFilters(TypedDict):
    """Windows security event filters type"""

    included: WindowsSecurityEventFilterOptions
    excluded: WindowsSecurityEventFilterOptions


class WindowsSecurityEvent(TypedDict):
    """Windows security event type"""

    id: str
    name: str
    description: str
    text: str
    filters: WindowsSecurityEventFilters


class ParsedWindowsSecurityEvent(TypedDict):
    """Parsed windows security event type"""

    id: str
    name: str
    description: str
    text: str
    filters: WindowsSecurityEventFilters
    events: list[str]
    log: str
