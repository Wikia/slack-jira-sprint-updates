# coding=utf-8
import datetime
import json
import logging
import os

import requests

JIRA_AUTHORIZATION = os.environ['JIRA_AUTHORIZATION']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_BOT_NAME = os.environ['SLACK_BOT_NAME']
JIRA_PROJECT_NAME = os.environ['JIRA_PROJECT_NAME']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']


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

        response = requests.get('https://wikia-inc.atlassian.net/rest/api/2/search',
                                params={
                                    'jql': 'project="' + params['project_name'] + '" AND "Preview branch" ~ "' + params[
                                        'release_version'] + '"'
                                },
                                headers=headers).json()

        logging.info(
            "\nFetching data from last " + params['days_before'] + " days for project " + params['project_name'])

        return response

    def get_params(self, release_version):
        days_count = {
            0: '6', 1: '2', 2: '3', 3: '2', 4: '3', 5: '4', 6: '5'}
        today = datetime.datetime.today().weekday()
        params = {
            'project_name': JIRA_PROJECT_NAME,
            'days_before': days_count[today],
            'release_version': release_version
        }

        return params


class SlackUpdater(object):
    def post_slack_message(self, payload):
        requests.post('https://slack.com/api/chat.postMessage',
                      data={
                          'channel': SLACK_CHANNEL,
                          'token': SLACK_BOT_TOKEN,
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
            result += '*' + release + '*\n'

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
    app_config = json.loads(os.environ['APPS'])
    apps = [Application(**ac) for ac in app_config]

    releases = [a.get_full_release_name() for a in apps]
    logging.info(releases)

    jira = JiraController()
    tickets = {release: jira.get_tickets(release_version=release) for release in releases}

    slack = SlackUpdater()
    update = slack.prepare_slack_update(tickets)
    slack.post_slack_message(update)
