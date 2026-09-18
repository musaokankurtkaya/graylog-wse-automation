from datetime import datetime
from typing import Any, NotRequired, TypedDict


class GraylogConfig(TypedDict):
    """Graylog config type"""

    GRAYLOG_URL: str
    GRAYLOG_USERNAME: str
    GRAYLOG_PASSWORD: str
    GRAYLOG_SEARCH_QUERY_INTERVAL: NotRequired[str]
    GRAYLOG_MAX_SEARCH_QUERY_INTERVAL: NotRequired[str]
    GRAYLOG_SEARCH_QUERY_LIMIT: NotRequired[str]


class ApiSearchUniversalRelativeResponse(TypedDict, total=False):
    """Graylog /api/search/universal/relative response type.

    For more details, see [SearchResponse](https://github.com/yumimobi/graylog.py/blob/master/docs/SearchResponse.md)
    """

    to: datetime
    fields: list[str]
    from_: datetime
    time: int
    query: str
    messages: list[dict[str, Any]]
    built_query: str
    decoration_stats: dict[str, Any]
    total_results: int
    used_indices: list[dict[str, Any]]
