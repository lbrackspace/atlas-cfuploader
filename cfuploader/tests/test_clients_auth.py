#!/usr/bin/env python
import json
import os
import threading
import unittest
import mock as mock
from cfuploader import clients
from cfuploader import utils
from MySQLdb import cursors
from requests import api

conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "test_conf.json")


class TestClientAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        full_path = os.path.expanduser(conf_file)
        test_conf_file = open(full_path, "r")

        with mock.patch('__builtin__.open', create=True) as mock_open:
            mock_open.return_value.__enter__.side_effect = [test_conf_file,
                                                            'foolog']
            cls.conf = utils.Config(conf_file=conf_file)

        cls.auth = clients.Auth(conf=cls.conf)
        cls.db_helper = clients.DbHelper(conf=cls.conf)

        cls.test_zf = 'access_log_503335_2021081817.zip'
        cls.zip_container = {'aid': 54321, 'lid': 12345,
                             'hl': '2021081817', 'zip_path': 'tmp/processed',
                             'zip_file': cls.test_zf,
                             'cnt': 'lb_tester1_5806065_202108',
                             'remote_zf': '/tmp/processed/' + cls.test_zf}

    @mock.patch('threading.Lock')
    def test_prep_headers(self, mock_lock):
        mock_lock.return_value = threading.Lock()
        headers = {'content-type': 'application/json',
                   'accept': 'application/json',
                   'x-auth-token': None}
        response = clients.Auth.prep_headers(self.auth)
        self.assertEqual(response, headers)

    @mock.patch('requests.api.get')
    @mock.patch('json.loads')
    def test_get_endpoints_by_token(self, mock_get, mock_json_loads):
        mock_get.return_value = mock_get.return_value = {
            'token': {'id': 'd74f592f986e4d6e995853ccf0123456',
                      'expires': '"2021-08-20 20:00:00.000"'}}
        resp = clients.Auth.get_endpoints_by_token(self.auth, 'd74f592f986e4d6e995853ccf0123456')
        self.assertEqual(resp, {'token': {'expires': '"2021-08-20 20:00:00.000"',
                                          'id': 'd74f592f986e4d6e995853ccf0123456'}})

    @mock.patch('requests.api.get')
    @mock.patch('json.loads')
    def test_get_admin_by_user(self, mock_get, mock_json_loads):
        mock_get.return_value = {'users':
            [
                {'id': 123,
                 'username': 'user1',
                 'RAX-AUTH:defaultRegion': 'SYD'},
                {'id': 234,
                 'username': 'user2',
                 'RAX-AUTH:defaultRegion': 'DFW'}
            ]
        }
        resp = clients.Auth.get_admin_by_user(self.auth, 111)
        self.assertEqual(resp, {'users': [{'RAX-AUTH:defaultRegion': 'SYD', 'id': 123, 'username': 'user1'},
                                          {'RAX-AUTH:defaultRegion': 'DFW', 'id': 234, 'username': 'user2'}]})

    @mock.patch('requests.api.post')
    @mock.patch('json.loads')
    def test_get_admin_token(self, mock_post, mock_json_loads):
        mock_post.return_value = {'access':
            {
                'token': {'id': 123,
                          'expires': '"2021-08-20 20:00:00.000"'}
            }
        }

        resp = clients.Auth.get_admin_token(self.auth)
        self.assertEqual(resp, {'expires': '"2021-08-20 20:00:00.000"', 'token': 123})

    @mock.patch('requests.api.get')
    @mock.patch('json.loads')
    def test_get_all_users(self, mock_get, mock_json_loads):
        mock_get.return_value = {'users':
            [
                {'id': 123,
                 'username': 'user1',
                 'RAX-AUTH:defaultRegion': 'SYD'},
                {'id': 234,
                 'username': 'user2',
                 'RAX-AUTH:defaultRegion': 'DFW'}
            ]
        }
        resp = clients.Auth.get_all_users(self.auth, '12345')
        self.assertEqual(resp, {'users': [{'RAX-AUTH:defaultRegion': 'SYD', 'id': 123, 'username': 'user1'},
                                          {'RAX-AUTH:defaultRegion': 'DFW', 'id': 234, 'username': 'user2'}]})

    @mock.patch('requests.api.get')
    @mock.patch('json.loads')
    def test_get_endpoints(self, mock_get, mock_json_loads):
        mock_get.return_value = {
            "region": "DFW",
            "tenantId": "123456",
            "publicURL": "https://global.cdn.api.rackspacecloud.com/v1.0/123456",
            "internalURL": "https://global.cdn.api.rackspacecloud.com/v1.0/123456"
        }
        resp = clients.Auth.get_endpoints(self.auth, '12345')
        self.assertEqual(resp, {
            "region": "DFW",
            "tenantId": "123456",
            "publicURL": "https://global.cdn.api.rackspacecloud.com/v1.0/123456",
            "internalURL": "https://global.cdn.api.rackspacecloud.com/v1.0/123456"
        })

    @mock.patch('requests.api.post')
    @mock.patch('json.loads')
    def test_impersonate_user(self, mock_post, mock_json_loads):
        mock_post.return_value = {'access':
            {
                'token': {'id': 123,
                          'expires': '"2021-08-20 20:00:00.000"'}
            }
        }
        resp = clients.Auth.impersonate_user(self.auth, 'testuser')
        self.assertEqual(resp, 123)

    @mock.patch('json.loads')
    def test_get_correct_region_endpoint(self, mock_json_loads):
        eps = {'endpoints': [{'type': 'object-store',
                              'region': 'SYD',
                              'publicURL': 'https://compute.north.public.com/v1'}]}
        self.conf.lb_region = 'SYD'
        lb_region = clients.Auth.get_correct_region_endpoint(self.auth, eps)
        self.assertEqual(lb_region, 'https://compute.north.public.com/v1')

    # @mock.patch('requests.api.get')
    # @mock.patch('requests.api.get')
    # @mock.patch('requests.api.post')
    # @mock.patch('requests.api.get')
    # @mock.patch('json.loads')
    # def test_get_token_and_endpoint(self, mock_get_users, mock_get_admin_users,
    #                                 mock_impersonate_user, mock_get_endpoints_by_token,
    #                                 mock_json_loads):
    #     mock_get_users.return_value = {'users':
    #         [
    #             {'id': 123,
    #              'username': 'user1',
    #              'RAX-AUTH:defaultRegion': 'SYD'},
    #             {'id': 234,
    #              'username': 'user2',
    #              'RAX-AUTH:defaultRegion': 'DFW'}
    #         ]
    #     }
    #
    #     mock_get_admin_users.return_value = {'users':
    #         [
    #             {'id': 123,
    #              'username': 'user1',
    #              'RAX-AUTH:defaultRegion': 'SYD'},
    #             {'id': 234,
    #              'username': 'user2',
    #              'RAX-AUTH:defaultRegion': 'DFW'}
    #         ]
    #     }
    #
    #     mock_impersonate_user.return_value = {'access':
    #         {
    #             'token': {'id': 123,
    #                       'expires': '"2021-08-20 20:00:00.000"'}
    #         }
    #     }
    #
    #     mock_get_endpoints_by_token.return_value = {
    #         'token': {'id': 'd74f592f986e4d6e995853ccf0123456',
    #                   'expires': '"2021-08-20 20:00:00.000"'}}
    #
    #     # mock_get_correct_region_endpoint.return_value = 'https://compute.north.public.com/v1'
    #     resp = clients.Auth.get_token_and_endpoint(self.auth, '12345')
    #     self.assertEqual(resp, {'token': 'token',
    #            'lb_region_ep': 'lb_region_ep',
    #            'domain_id': 'domain_id'})

    @mock.patch('threading.Lock')
    def test_get_counts(self, mock_lock):
        mock_lock.return_value = threading.Lock()
        count = {"cache": 0, "reqs": 0,
                 "total": 0}
        response = clients.Auth.get_counts(self.auth)
        self.assertEqual(response, {'cache': 0, 'reqs': 0, 'total': 0})

    # @mock.patch('cfuploader.clients.os.walk')
    # def test_scan_zip_files(self, mock_os_walk):
    #     clients.scan_zip_files("/test/test")
    #     mock_os_walk.assert_has_calls([mock.call('/test/test')])

    @mock.patch('MySQLdb.connect')
    @mock.patch('MySQLdb.Connection')
    @mock.patch('MySQLdb.cursors.DictCursor')
    def test_get_lb_map(self, mock_connect, mock_connection, mock_cursors):
        rows = {'account_id': 123,
                'id': 1,
                'name': 'abc'}
        mock_cursors.fetchall.return_value = rows
        resp = clients.DbHelper.get_lb_map(self.db_helper)
        self.assertEqual(resp, {})
