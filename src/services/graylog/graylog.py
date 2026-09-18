from typing import Any

from src.types import (
    ApiSearchUniversalRelativeResponse,
    ParsedWindowsSecurityEvent,
    WindowsSecurityEvent,
)

from ..http_client import HttpClient, Response


class Graylog:
    """Graylog class to interact with Graylog's API.

    For more details, see [Graylog REST API](https://go2docs.graylog.org/current/setting_up_graylog/rest_api.html)

    Instance Attributes
    -------------------
    http_client : HttpClient
        HTTP client to make requests.
    """

    def __init__(self, url: str, username: str, password: str):
        self.http_client: HttpClient = HttpClient(url=url, auth=(username, password))

    def get_api_search_universal_relative(
        self, query: str, range: int = 15, limit: int = 9999
    ) -> list[dict[str, Any]]:
        """Get the search results based on the given query, range, and limit.

        For more details, see [Graylog API Browser](https://go2docs.graylog.org/current/setting_up_graylog/api_browser.html)

        Parameters
        ----------
        query : str
            The query to search for.
        range : int, optional
            The less than minutes. Default is 15.
        limit : int, optional
            The limit of the search. Default is 9999.

        Returns
        -------
        list[dict[str, Any]]
            The search results.
        """

        res: Response | None = self.http_client.request(
            method="get",
            endpoint="/api/search/universal/relative",
            params={
                "query": query,
                "range": self.range_minutes_to_seconds(minutes=range),
                "limit": limit,
            },
        )
        if res is None:
            return []

        data: ApiSearchUniversalRelativeResponse = res.json()
        events: list[dict[str, Any]] = data.get("messages", [])
        return events

    @staticmethod
    def parse_search_results(
        search_results: list[dict[str, Any]],
        windows_security_events: list[WindowsSecurityEvent],
    ) -> list[ParsedWindowsSecurityEvent]:
        """Parse the search results to match with the windows security events.

        Parameters
        ----------
        search_results : list[dict[str, Any]]
            The search results to parse.
        windows_security_events : list[WindowsSecurityEvent]
            The windows security events list to match with the search results.

        Returns
        -------
        list[ParsedWindowsSecurityEvent]
            The filtered windows security events that contain parsed events.
        """

        def _is_event_matched(
            wse: WindowsSecurityEvent,
            event_id: str | None,
            src_user: str,
            dst_user: str,
            group_name: str,
        ) -> bool:
            """Check if a specific windows security event matches the filters."""

            if wse.get("id") != event_id:
                return False

            if src_user == "-" and dst_user == "-" and group_name == "-":
                return False

            # get filters from wse
            filters = wse.get("filters", {})

            excluded = filters.get("excluded", {})
            excluded_src_users = excluded.get("src_users", [])
            excluded_dst_users = excluded.get("dst_users", [])
            excluded_groups = excluded.get("groups", [])

            included = filters.get("included", {})
            included_src_users = included.get("src_users", [])
            included_dst_users = included.get("dst_users", [])
            included_groups = included.get("groups", [])

            # excluded conditions
            if src_user in excluded_src_users:
                return False
            if dst_user in excluded_dst_users:
                return False
            if group_name in excluded_groups:
                return False

            # included conditions
            if included_src_users and src_user not in included_src_users:
                return False
            if included_dst_users and dst_user not in included_dst_users:
                return False
            if included_groups and group_name not in included_groups:  # noqa: SIM103
                return False

            return True

        for s_result in search_results:
            s_result_message: dict[str, Any] = s_result.get("message", {})
            # get windows security event expected fields from the s_result
            event_id: str | None = s_result_message.get("EventID")
            src_user: str = s_result_message.get("SourceUser") or "-"
            dst_user: str = s_result_message.get("DestinationUser") or "-"
            group_name: str = s_result_message.get("GroupName") or "-"
            log: str = s_result_message.get("message") or "-"

            # match the search result with the windows security event
            matched_wse: WindowsSecurityEvent | None = next(
                (
                    wse
                    for wse in windows_security_events
                    if _is_event_matched(
                        wse=wse,
                        event_id=event_id,
                        src_user=src_user,
                        dst_user=dst_user,
                        group_name=group_name,
                    )
                ),
                None,
            )
            if matched_wse is None:
                continue

            # cast the matched_wse to ParsedWindowsSecurityEvent to access the events and log fields
            parsed_matched_wse: ParsedWindowsSecurityEvent = matched_wse  # type: ignore

            # format the parsed_matched_wse_text with the event text from the windows_security_events list
            parsed_matched_wse_text: str = parsed_matched_wse["text"].format(
                src_user=src_user, dst_user=dst_user, group_name=group_name
            )

            # add the parsed_matched_wse_text to the parsed_matched_wse events list to avoid duplicates
            parsed_matched_wse_list: set[str] = set(
                parsed_matched_wse.get("events", [])
            )
            parsed_matched_wse_list.add(parsed_matched_wse_text)
            parsed_matched_wse["events"] = list(parsed_matched_wse_list)
            # update the parsed_matched_wse log field with the last parsed windows security event's log field
            parsed_matched_wse["log"] = log

        # get the parsed wse from the windows_security_events list that has events
        return [wse for wse in windows_security_events if wse.get("events")]  # type: ignore

    @staticmethod
    def range_minutes_to_seconds(minutes: int) -> int:
        """Convert the given minutes to seconds to use in request params."""

        return minutes * 60
