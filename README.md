# Graylog - Windows Security Event ID Automation

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

`graylog-wse-automation` retrieves Windows Security Events using the [Graylog REST API](https://go2docs.graylog.org/current/setting_up_graylog/rest_api.html), based on Event IDs defined in [windows_security_events.json](https://github.com/musaokankurtkaya/graylog-wse-automation/blob/main/src/data/windows_security_events.json). It dynamically builds query, parses log responses, enriches events with predefined metadata, and dispatches formatted HTML alerts via SMTP. Critical application errors are reported through Microsoft Teams webhooks if configured.

## Table of Contents

- [Workflow / Architecture](#workflow--architecture)
- [Example Alert](#example-alert)
- [Installation](#installation)
- [Execution / Usage](#execution--usage)

## Workflow / Architecture

1. **Fetch & Build:** Reads event IDs from `windows_security_events.json` and dynamically builds query.

2. **Execute:** Executes query searches through the Graylog REST API.

3. **Parse & Match:** Parses Graylog responses and enriches events with predefined metadata.

4. **Notify:** Generates HTML-formatted email alerts via SMTP. Critical application errors are reported through Microsoft Teams webhooks.

## Example Alert

The automation generates HTML-formatted email alerts containing relevant Windows Security Event information and predefined event metadata.

![Example Security Alert](https://github.com/musaokankurtkaya/graylog-wse-automation/blob/main/assets/example_alert.png)

## Installation

### Requirements

Before running the project, install the required Python packages:

```sh
pip install -r requirements.txt
```

### Environment Configuration

Rename `.env.example` to `.env` and set the necessary keys:

- **Graylog settings**: Set `GRAYLOG_URL`, `GRAYLOG_USERNAME`, `GRAYLOG_PASSWORD`, `GRAYLOG_SEARCH_QUERY` and `GRAYLOG_SEARCH_QUERY_INTERVAL` to access and search on the Graylog API. The other fields are optional.

- **SMTP settings**: Set `SMTP_SERVER`, `SMTP_PORT`, `SMTP_FROM_EMAIL`, `SMTP_FROM_EMAIL_APP_PASSWORD` and `SMTP_TO_EMAILS` to send emails via SMTP. The other fields are optional.

> [!NOTE]
> **`SMTP_FROM_EMAIL_APP_PASSWORD` Setup**
>
> For security reasons, do not use your regular email password. You need to create an **App Password** after enabling 2-Step Verification:
>
> - 🔹 **Gmail:** [Google App Passwords Guide](https://support.google.com/accounts/answer/185833)
> - 🔹 **Outlook / Hotmail:** [Microsoft App Passwords Guide](https://support.microsoft.com/en-us/accounts-billing/manage/how-to-get-and-use-app-passwords)

- **Teams workflow settings**: Configure `TEAMS_WEBHOOK_URL` in `.env` to enable critical application error notifications through a Microsoft Teams **workflow that posts to a channel when a webhook is received**. See the [Microsoft Teams Workflows](https://support.microsoft.com/en-us/teams/apps-service/overview-of-workflows-in-microsoft-teams) documentation for more information.

## Execution / Usage

To run the project **locally**, open up a terminal and run the following command:

```sh
cd src/
python3 __main__.py
```

Or schedule it using **Cron** (to run automatically every 15 minutes):

1. Open your system's crontab editor:

```sh
crontab -e
```

2. Add the following line (update /path/to/project with your actual project directory):

```sh
*/15 * * * * cd /path/to/graylog-wse-automation/src && python3 __main__.py
```

Or you can run it using **Docker**:

```sh
docker build -t graylog-wse-automation .
docker run --env-file src/config/.env graylog-wse-automation
```
