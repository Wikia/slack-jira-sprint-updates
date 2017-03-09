import logging

import requests


class JiraController(object):
    def __init__(self, jira_auth, jira_project):
        logging.basicConfig(level=logging.INFO)

        self.jira_auth = jira_auth
        self.jira_project = jira_project

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
            'Authorization': self.jira_auth
        }

        response = requests.get('https://wikia-inc.atlassian.net/rest/api/2/search',
                                params={
                                    'jql': 'project="{project}" AND "Preview branch" ~ "{release}"'.format(
                                        project=params['project_name'], release=params['release_version'])
                                },
                                headers=headers
                                ).json()

        logging.info(
            "\nFetching data for {project} for {release}".format(project=params['project_name'],
                                                                 release=params['release_version'])
        )

        return response

    def get_params(self, release_version):
        params = {
            'project_name': self.jira_project,
            'release_version': release_version
        }

        return params
