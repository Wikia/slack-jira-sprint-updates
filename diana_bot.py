# coding=utf-8
import datetime
import getopt
import json
import logging
import sys

import requests

from credentials import JIRA_AUTHORIZATION, \
    JIRA_API_URL, \
    SLACK_CHANNEL_ID, \
    SLACK_BOT_TOKEN, \
    SLACK_BOT_NAME, \
    JIRA_PROJECT_NAME, \
    GITHUB_TOKEN

days_count = {
    0: '6',
    1: '2',
    2: '3',
    3: '2',
    4: '3',
    5: '4',
    6: '5'
}


class JiraController():
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    def get_tickets(self, release_version):
        """
        Gets the finished tickets statistics
        """
        response = []
        params = self.get_params(release_version)

        finished_tickets = self.make_jira_request(params)

        for ticket in finished_tickets['issues']:
            response.append({
                "key": ticket['key'],
                "desc": ticket['fields']['summary']
            })

        return response

    def make_jira_request(self, params):
        headers = {
            'contentType': 'application/json',
            'Authorization': JIRA_AUTHORIZATION
        }

        response = requests.get(JIRA_API_URL,
                                params={
                                    'jql': 'project="' + params['project_name'] + '" AND "Preview branch" ~ "' + params[
                                        'release_version'] + '"'
                                },
                                headers=headers).json()

        logging.info(
            "\nFetching data from last " + params['days_before'] + " days for project " + params['project_name'])

        return response

    def get_params(self, release_version):
        today = datetime.datetime.today().weekday()
        params = {
            'project_name': JIRA_PROJECT_NAME,
            'days_before': days_count[today],
            'release_version': release_version
        }

        optlist, args = getopt.getopt(sys.argv[1:], "p:d:", ["project=", "days="])
        print optlist

        for option, arg in optlist:
            if option in ("-p", "--project") and arg != '--days':
                params['project_name'] = arg
            if option in ("-d", "--days") and arg.isdigit():
                params['days_before'] = arg

        return params


class SlackUpdater(object):
    SLACK_API_URL = 'https://slack.com/api/chat.postMessage'

    def __init__(self, slack_bot_token=None, slack_bot_channel=SLACK_CHANNEL_ID):
        assert slack_bot_token is not None
        assert slack_bot_channel is not None

        self.slack_bot_token = slack_bot_token
        self.slack_bot_channel = slack_bot_channel

    def post_slack_message(self, payload):
        requests.post(self.SLACK_API_URL,
                      data={
                          'channel': self.slack_bot_channel,
                          'token': self.slack_bot_token,
                          'text': payload,
                          'username': SLACK_BOT_NAME
                      })

        logging.info("\nPosting to Slack: done")

    def prepare_slack_update(self, tickets):
        """
        Processes acquired results
        """
        result = ''
        print tickets
        for release, tickets_list in tickets.iteritems():
            result += '*' + release + ':*\n'

            if len(tickets_list) == 0:
                result += 'Nothing user facing\n'
            else:
                result += '```'
                for ticket in tickets_list:
                    result += 'https://wikia-inc.atlassian.net/browse/' + ticket['key'] + ' ' + ticket['desc'] + '\n'
                result += '```\n'
            result += '\n'
        return result


class Application(object):
    def __init__(self, app_name, repo_name=None):
        self.app_name = app_name
        self.repo_name = repo_name if repo_name else app_name
        self.github_api_url = "https://api.github.com/repos/Wikia/{name}/tags".format(name=self.repo_name)
        self.headers = {
            'Authorization': 'token {}'.format(GITHUB_TOKEN)
        }

    def get_latest_release(self):
        response = requests.get(self.github_api_url, headers=self.headers)

        if response.status_code != 200:
            logging.warning("Failed to fetch data from github for {}".format(self.repo_name))

        tags = json.loads(response.text)
        tag_names = [t['name'] for t in tags if t['name'].startswith('release-')]

        return tag_names[0].split('.')[0]

    def get_full_release_name(self):
        return "{app}:{release}".format(app=self.app_name, release=self.get_latest_release())


if __name__ == "__main__":
    apps = [
        Application('wikia', 'app'),
        Application('mercury'),
        Application('mobile-wiki'),
    ]

    # releases = [a.get_full_release_name() for a in apps]
    releases = ['wikia:release-490', 'mercury:release-322', 'mobile-wiki:release-5']
    logging.info(releases)

    jira = JiraController()
    tickets = {release: jira.get_tickets(release_version=release) for release in releases}

    slack = SlackUpdater(slack_bot_token=SLACK_BOT_TOKEN)
    update = slack.prepare_slack_update(tickets)
    slack.post_slack_message(update)


