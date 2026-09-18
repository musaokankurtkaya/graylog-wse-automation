from html import escape as html_escape
from typing import Any

from src.config import (
    load_graylog_conf,
    load_json_file,
    load_smtp_conf,
    update_config_key,
)
from src.services.graylog import Graylog
from src.services.smtp import SMTP, Template
from src.types import (
    GraylogConfig,
    ParsedWindowsSecurityEvent,
    SMTPConfig,
    WindowsSecurityEvent,
)
from src.utils.constants import (
    CONFIG,
    DEFAULT_GRAYLOG_SEARCH_QUERY_INTERVAL,
    DEFAULT_GRAYLOG_SEARCH_QUERY_LIMIT,
    GRAYLOG_MAX_SEARCH_QUERY_INTERVAL,
)
from src.utils.logger import datetime, log_message


def main() -> None:
    # read windows_security_events.json from data/ folder to match with the graylog's windows security events
    wse_json_data: list[WindowsSecurityEvent] = load_json_file(
        f_name="windows_security_events.json"
    )

    # load graylog's config from CONFIG to use in graylog's instance
    graylog_config: GraylogConfig = load_graylog_conf(conf=CONFIG)

    # create graylog's instance to search & parse windows security events
    graylog: Graylog = Graylog(
        url=graylog_config["GRAYLOG_URL"],
        username=graylog_config["GRAYLOG_USERNAME"],
        password=graylog_config["GRAYLOG_PASSWORD"],
    )

    # create the search query to get the windows security events from graylog
    search_query: str = " OR ".join([f"EventID:{wse['id']}" for wse in wse_json_data])

    # get search_query_interval from graylog_config to pass as a parameter in the graylog.get_api_search_universal_relative() method
    search_query_interval_key: str = "GRAYLOG_SEARCH_QUERY_INTERVAL"
    search_query_interval: int = int(
        graylog_config.get(search_query_interval_key)
        or DEFAULT_GRAYLOG_SEARCH_QUERY_INTERVAL
    )

    # get search_query_limit from graylog_config to pass as a parameter in the graylog.get_api_search_universal_relative() method
    search_query_limit_key: str = "GRAYLOG_SEARCH_QUERY_LIMIT"
    search_query_limit: int = int(
        graylog_config.get(search_query_limit_key) or DEFAULT_GRAYLOG_SEARCH_QUERY_LIMIT
    )

    # get the search results with the given search_query, search_query_interval, and search_query_limit to parse
    search_results: list[dict[str, Any]] = graylog.get_api_search_universal_relative(
        query=search_query,
        range=search_query_interval,
        limit=search_query_limit,
    )
    if not search_results:
        # no any search results found, add 15 minutes to the search_query_interval to search in the next run
        search_query_interval += DEFAULT_GRAYLOG_SEARCH_QUERY_INTERVAL
        # check if the search_query_interval is less than GRAYLOG_MAX_SEARCH_QUERY_INTERVAL, if not, set it to DEFAULT_GRAYLOG_SEARCH_QUERY_INTERVAL
        if search_query_interval < GRAYLOG_MAX_SEARCH_QUERY_INTERVAL:
            update_config_key(
                key=search_query_interval_key, value=str(search_query_interval)
            )
            log_message(
                mode="warning",
                msg=f"no any search results found in the last {search_query_interval - DEFAULT_GRAYLOG_SEARCH_QUERY_INTERVAL} minutes",
            )
        else:
            update_config_key(
                key=search_query_interval_key,
                value=str(DEFAULT_GRAYLOG_SEARCH_QUERY_INTERVAL),
            )
            log_message(
                mode="warning",
                msg=f"no any search results found for {GRAYLOG_MAX_SEARCH_QUERY_INTERVAL} minutes, query_interval is set to {DEFAULT_GRAYLOG_SEARCH_QUERY_INTERVAL} minutes",
            )
        return

    # search results found, reset the search_query_interval to the DEFAULT_GRAYLOG_SEARCH_QUERY_INTERVAL
    update_config_key(
        key=search_query_interval_key, value=str(DEFAULT_GRAYLOG_SEARCH_QUERY_INTERVAL)
    )

    # get the parsed wse after matching with the wse_json_data
    parsed_wse: list[ParsedWindowsSecurityEvent] = graylog.parse_search_results(
        search_results=search_results, windows_security_events=wse_json_data
    )
    if not parsed_wse:
        return

    # load smtp config from CONFIG to use in the smtp instance
    smtp_config: SMTPConfig = load_smtp_conf(conf=CONFIG)

    # create smtp instance to send parsed wse via email
    smtp: SMTP = SMTP(
        host=smtp_config["SMTP_HOST"], port=int(smtp_config.get("SMTP_PORT") or 587)
    )

    # check if the smtp user is logged in with the given credentials
    is_logged_in: bool = smtp._login(
        user=smtp_config["SMTP_FROM_EMAIL"],
        password=smtp_config["SMTP_FROM_EMAIL_APP_PASSWORD"],
    )
    if not is_logged_in:
        return

    # process on the parsed wse to send email via smtp
    for p_wse in parsed_wse:
        # load the mail template for the each p_wse
        p_wse_mail_template: Template | None = smtp.load_mail_template()
        if p_wse_mail_template is None:
            continue

        # render the mail template with the p_wse data
        p_wse_rendered_mail_template: str = p_wse_mail_template.render(
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            wse_id=p_wse["id"],
            wse_name=p_wse["name"],
            wse_desc=p_wse["description"],
            wses="".join(p_wse["events"]),
            wse_log=html_escape(s=p_wse["log"]),
        )
        # send the rendered mail template via smtp
        smtp._sendmail(
            subject=f"[GRAYLOG_WSE] {p_wse['name']}",
            message=p_wse_rendered_mail_template,
            to_email=smtp_config["SMTP_TO_EMAILS"],
            cc=smtp_config["SMTP_CC_EMAILS"],
        )

    smtp._quit()
