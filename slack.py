import logging

import requests


class SlackUpdater(object):
    def __init__(self, channel, token, bot_name):
        logging.basicConfig(level=logging.INFO)
        self.channel = channel
        self.token = token
        self.bot_name = bot_name

    def post_slack_message(self, payload):
        requests.post('https://slack.com/api/chat.postMessage',
                      data={
                          'channel': self.channel,
                          'token': self.token,
                          'text': payload,
                          'username': self.bot_name
                      })

        logging.info("\nPosting to Slack: done")

    def prepare_slack_update(self, tickets):
        """
        Processes acquired results
        """
        result = ''
        for release, tickets_list in tickets.iteritems():
            if len(tickets_list) != 0:
                result += '*' + release + '*\n```'
                for ticket in tickets_list:
                    result += 'https://wikia-inc.atlassian.net/browse/' + ticket['key'] + ' ' + ticket['desc'] + '\n'
                result += '```\n'

        if len(result) == 0:
            result = 'Nothing user facing'
        return result
