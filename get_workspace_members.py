#!/usr/bin/env python3

import logging
from datetime import datetime
from pathlib import Path
import configparser
import requests
import pandas as pd


logger = logging.getLogger('workspace_member_tracker')


ORGANIZATION_CODE = 'garrett-motion'
WORKSPACE_ID = '04-040723682'
API_PROFILE = 'prod-garrett'


class Api:
    """
    Class for basic access to the Rescale API.
    """

    def __init__(self, api_key, base_url='https://platform.rescale.com'):
        """
        :param api_key: str: Rescale API key
        :param base_url: str: Rescale API base URL
        """
        self.api_key = api_key
        self.authorization = f'Token {self.api_key}'
        self.base_url = base_url

    def get_request(self, url, params=None):
        """
        Send a GET request.
        :param url: str: URL for GET request.
        :param params: dict: parameters for GET request
        """
        response = requests.get(
            url,
            params=params,
            headers={'Authorization': self.authorization}
        )
        return response

    def get_workspace_members(self, organization_code, workspace_id):
        """
        Return all members of a workspace.
        :param str organization_code: organization code, e.g 'demo-company'
        :param str workspace_id: Workspace ID, eg. '04-040723682'
        :rtype: list
        """

        response = self.get_request(
            url=f'{self.base_url}/api/v2/organizations/{organization_code}/workspaces/{workspace_id}/members/'
        )
        response.raise_for_status()
        return response.json()


def setup_logging():
    """
    Set basic configuration for the logging system.
    """
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s %(levelname)s: %(message)s')


def main():
    """
    Main function
    """
    setup_logging()

    config = configparser.ConfigParser()
    config.read(Path.home().joinpath('.config', 'rescale', 'apiconfig'))
    api_key = config[API_PROFILE].get('apikey')
    api_baseurl = config[API_PROFILE].get('apibaseurl')
    api = Api(api_key=api_key, base_url=api_baseurl)

    logger.info(f'Requesting workspace members for workspace {WORKSPACE_ID}.')

    workspace_members = api.get_workspace_members(
        organization_code=ORGANIZATION_CODE,
        workspace_id=WORKSPACE_ID
    )

    df = pd.DataFrame(workspace_members)

    columns_to_export = [c for c in df.columns if c != 'workspace']  # exclude column 'workpsace' from Excel file
    outfile_name = f'members_{ORGANIZATION_CODE}_{WORKSPACE_ID}_{datetime.now().strftime("%Y-%m-%dT%H_%M_%S")}.xlsx'
    df.to_excel(
        outfile_name,
        columns=columns_to_export,
        index=False
    )

    logger.info(f'Found {len(workspace_members)} members in workspace {WORKSPACE_ID}.')
    logger.info(f'Output written to {outfile_name}')


if __name__ == '__main__':
    main()
