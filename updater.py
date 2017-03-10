# coding=utf-8
import json
import logging
import os

from jira import JiraController
from slack import SlackUpdater
from wikia import Application

JIRA_AUTHORIZATION = os.environ['JIRA_AUTHORIZATION']
JIRA_PROJECT_NAME = os.environ['JIRA_PROJECT_NAME']
SLACK_BOT_NAME = os.environ['SLACK_BOT_NAME']
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']

if __name__ == "__main__":
    app_config = json.loads(os.environ['APPS'])
    apps = [Application(**ac) for ac in app_config]

    releases = [a.get_full_release_name() for a in apps]
    logging.info(releases)

    jira = JiraController(jira_auth=JIRA_AUTHORIZATION, jira_project=JIRA_PROJECT_NAME)
    tickets = {release: jira.get_tickets(release_version=release) for release in releases}

    slack = SlackUpdater(channel=SLACK_CHANNEL, token=SLACK_BOT_TOKEN, bot_name=SLACK_BOT_NAME)
    update = slack.prepare_slack_update(tickets)
    slack.post_slack_message(update)
