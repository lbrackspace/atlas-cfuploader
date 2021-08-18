#!/usr/bin/env python
import os
import threading
import unittest
import mock as mock
from cfuploader import clients, utils

conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "test_conf.json")


class TestClientAuth(unittest.TestCase):

    def setUp(self):
        self.conf = utils.Config(conf_file=conf_file)

    # def setup(self):
    #     self.conf = utils.Config(conf_file=conf_file)
    #     self.auth_url = self.conf.auth_url
    #     self.auth_user = self.conf.auth_user
    #     self.auth_passwd = self.conf.auth_passwd
    #     self.headers = {'content-type': 'application/json',
    #                     'accept': 'application/json',
    #                     'x-auth-token': None}
    #     self.auth = clients.Auth(conf=self.conf)
    #     self.token = None
    #     self.god_token = None
    #     self.auth_lock = threading.Lock()
    #     self.cache_count = 0
    #     self.req_count = 0
    #     self.endpoints = {'token': None}
    #     self.uid = 1
    #     self.admin_users = {
    #         'uid': ''
    #     }

    @mock.patch('threading.Lock')
    @mock.patch('cfuploader.clients.Auth')
    def test_prep_headers(self, mock_lock, mock_auth):
        mock_lock.return_value = threading.Lock()
        clients.Auth.prep_headers(mock_auth)

    @mock.patch('threading.Lock')
    @mock.patch('requests.api.get')
    def test_get_endpoints_by_token(self, mock_lock, mock_get):
        auth = clients.Auth(conf=self.conf)
        mock_lock.return_value = threading.Lock
        mock_get.return_value = {}
        auth.get_endpoints_by_token(auth)

    @mock.patch('threading.Lock')
    @mock.patch('clients.prep_headers')
    @mock.patch('cfuploader.clients.Auth.prep_header')
    def test_get_admin_by_user(self, mock_lock, mock_prep_header):
        auth = clients.Auth(conf=self.conf)
        mock_lock.return_value = threading.Lock
        mock_prep_header.return_value = {'content-type': 'application/json',
                                         'accept': 'application/json',
                                         'x-auth-token': None}
        auth.get_admin_by_user()

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

    def test_get_correct_region_endpoint(self):
        eps = {'endpoints': [{'type': 'object-store',
                              'region': 'region',
                              'publicURL': 'url'}]}
        lb_region = clients.Auth.get_correct_region_endpoint(self.auth, eps)
        self.assertIsNotNone(lb_region)

    @mock.patch('MySQLdb.connect')
    @mock.patch('MySQLdb.Connection')
    @mock.patch('MySQLdb.connections.Connection.cursor')
    def test_get_lb_map(self, mock_connect, mock_connection, mock_cursor):
        db_helper = clients.DbHelper(conf=self.conf)
        # conn = Connection() # DB Connection?
        # cur = conn.cursor()
        rows = {'account_id': 123,
                'id': 1,
                'name': 'abc'}
        # mock_connect.return_value = conn
        # mock_connection.return_value = cur
        mock_cursor.fetchall.return_value = rows
        clients.DbHelper.get_lb_map()

    @mock.patch('cfuploader.clients.DbHelper.get_lb_ids')
    @mock.patch('cfuploader.utils.Config')
    def test_create_fake_zips(self, mock_get_lb_ids, mock_config):
        conf = {'auth_url': 123}
        mock_config.load_json.return_value = conf
        # lbs = [{'aid': 1,
        #         'lid': 11,
        #         'name': 'lb1'},
        #        {'aid': 1,
        #         'lid': 22,
        #         'name': 'lb2'},
        #        {'aid': 1,
        #         'lid': 33,
        #         'name': 'lb3'}]
        # #
        mock_get_lb_ids.values.return_value = [{'abc': 1}]
        cf = utils.Config
        clients.create_fake_zips(cf, 1, 3)

    def test_get_correct_region_endpoint(self):
        r = clients.Auth.get_correct_region_endpoint()

    @mock.patch('cfuploader.clients.os.walk')
    def test_scan_zip_files(self, mock_os_walk):
        clients.scan_zip_files("/test/test")
        mock_os_walk.assert_has_calls([mock.call('/test/test')])
