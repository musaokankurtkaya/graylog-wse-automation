from src.utils.constants import IS_PROD, TEAMS_WORKFLOW_CONFIG

from ..http_client import HttpClient, log_message


class MsTeams:
    """Microsoft Teams class to interact with Teams' workflows.

    For more details, see [Microsoft Teams' Workflows](https://support.microsoft.com/en-us/teams/apps-service/overview-of-workflows-in-microsoft-teams)

    Class Attributes
    ----------------
    workflow_url: str | None
        URL of the Microsoft Teams workflow.
    http_client : HttpClient
        HTTP client to make requests.
    """

    workflow_url: str | None = TEAMS_WORKFLOW_CONFIG["url"]
    http_client: HttpClient = HttpClient(url=workflow_url, verify=True)  # pyright: ignore[reportArgumentType]

    @classmethod
    def send_message(
        cls,
        msg: str,
        title: str | None = TEAMS_WORKFLOW_CONFIG["title"],
        send_on_dev: bool = False,
    ) -> None:
        """Send a message to Microsoft Teams with the given message and title using the workflow URL.

        Parameters
        ----------
        msg : str
            Message to send.
        title : str, optional
            Title of the message, by default TEAMS_WORKFLOW_CONFIG["title"]
        send_on_dev : bool, optional
            Flag to send the message on development, by default False.
        """

        if not IS_PROD and not send_on_dev:
            return

        if not cls.workflow_url:
            log_message(
                mode="error",
                msg="TEAMS_WORKFLOW_URL not found in the .env file, message will not be sent to teams",
            )
            return

        json_body = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "msTeams": {"width": "full"},
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": title,
                                "size": "large",
                                "weight": "bolder",
                            },
                            {
                                "type": "TextBlock",
                                "text": msg,
                                "wrap": True,
                            },
                        ],
                    },
                }
            ],
        }

        cls.http_client.request(method="post", json=json_body)
