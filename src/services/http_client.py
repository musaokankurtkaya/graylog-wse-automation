from urllib.parse import urljoin

import urllib3
from requests import HTTPError, RequestException, Response, Session
from urllib3.exceptions import InsecureRequestWarning

from src.utils.logger import log_message


class HttpClient:
    """HTTP client to make requests to a specified URL.

    Instance Attributes
    -------------------
    url : str
        The base URL where requests will be sent.
    session : Session
        Session object to make requests.
    """

    def __init__(
        self, url: str, suppress_warnings: bool = False, **session_kwargs
    ) -> None:
        """Initialize the HTTP client.

        Parameters
        ----------
        url : str
            The base URL where requests will be sent.
        suppress_warnings : bool, optional
            Whether to suppress warnings from urllib3. Defaults to False.
        **session_kwargs
            Request keyword arguments to pass to the session object, such as headers, auth, verify, etc.
        """

        self.url: str = url

        self.session = Session()
        self.session.headers = {
            "content-type": "application/json",
            "accept": "application/json",
        } | session_kwargs.get("headers", {})
        self.session.auth = session_kwargs.get("auth", None)

        verify_ssl: bool = session_kwargs.get("verify", False)
        if not verify_ssl and suppress_warnings:
            urllib3.disable_warnings(category=InsecureRequestWarning)

        self.session.verify = verify_ssl

    def request(
        self,
        method: str,
        url: str | None = None,
        endpoint: str | None = None,
        **request_kwargs,
    ) -> Response | None:
        """Make an HTTP request.

        Parameters
        ----------
        method : str
            HTTP method to use (get, post, put, delete, etc.)
        url : str, optional
            URL to make the request to. If not provided, the base URL will be used.
        endpoint : str, optional
            Endpoint to append to the URL. If not provided, URL will be used as is.
        **request_kwargs
            Additional request keyword arguments to pass to the request method, such as params, json, data, headers, etc.

        Returns
        -------
        Response | None
            HTTP response object if the request is successful, otherwise None.
        """

        base_url: str = url or self.url
        req_url: str = urljoin(base=base_url, url=endpoint) if endpoint else base_url

        try:
            res: Response = self.session.request(
                method=method, url=req_url, **request_kwargs
            )

            res.raise_for_status()

            return res
        except RequestException as e:
            error_msg = f"request error occured ⊱ {e} ⊰ while requesting to {req_url}"

            if isinstance(e, HTTPError) and e.response is not None:
                try:
                    error_detail = e.response.json()
                except ValueError:
                    error_detail = e.response.text or str(e)

                error_msg = f"http error occured ⊱ {error_detail} ⊰ while requesting to {req_url}"

            log_message(mode="error", msg=error_msg)
