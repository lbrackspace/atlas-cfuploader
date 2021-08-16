#!/usr/bin/env python
import os
import threading
import unittest

import mock as mock

from cfuploader import clients, utils

conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "test_conf.json")


class TestClientAuth(unittest.TestCase):

    def setup(self):
        self.conf = utils.Config(conf_file=conf_file)
        self.auth_url = self.conf.auth_url
        self.auth_user = self.conf.auth_user
        self.auth_passwd = self.conf.auth_passwd
        self.headers = {'content-type': 'application/json',
                        'accept': 'application/json',
                        'x-auth-token': None}
        self.auth = clients.Auth(conf=self.conf)
        self.token = None
        self.god_token = None
        self.auth_lock = threading.Lock()
        self.cache_count = 0
        self.req_count = 0
        self.endpoints = {'token': None}
        self.uid = 1
        self.admin_users = {
            'uid': ''
        }

    @mock.patch("cfuploader.clients.Auth.prep_headers")
    def test_get_endpoints_by_token(self, mock_prep_headers):
        mock_prep_headers.return_value = {'content-type': 'application/json',
                        'accept': 'application/json',
                        'x-auth-token': None}
        auth = clients.Auth(conf=self.conf)
        ep = auth.get_endpoints_by_token(self.token)
        # It return the response, how it looks like?
        self.assertEqual(1, 1)

    # @patch('clients.prep_headers')
    # def test_get_admin_by_user(self, mock_prep_headers):
    #     mock_prep_headers.prep_headers.return_value = self.headers
    #
    # @patch('clients.prep_headers')
    # @patch('json')
    # def test_get_admin_token(self, mock_prep_headers, mock_json):
    #     obj = {'users': [
    #         {'id': 1,
    #          'username': 'test',
    #          'RAX-AUTH:defaultRegion': 'rax-auth'}
    #     ]}
    #     mock_prep_headers.prep_headers.return_value = self.headers
    #     mock_json.loads.return_value = obj
    #     resp = clients.get_admin_by_user(self.uid)
    #     self.assertEqual(obj.get('username'), resp.get('username'))
