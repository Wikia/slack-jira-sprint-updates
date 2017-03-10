import logging
import os

import requests

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']


class Application(object):
    def __init__(self, app_name, repo_name=None):
        logging.basicConfig(level=logging.INFO)
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

        tags = response.json()
        tag_names = [t['name'] for t in tags if t['name'].startswith('release-')]

        return tag_names[0].split('.')[0]

    def get_full_release_name(self):
        return "{app}:{release}".format(app=self.app_name, release=self.get_latest_release())
