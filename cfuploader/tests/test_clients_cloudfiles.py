import json
import os
import unittest

import mock as mock

from cfuploader import clients
from cfuploader import utils
from cfuploader.clients import CloudFiles

conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "test_conf.json")


class TestClientCloudFiles(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        full_path = os.path.expanduser(conf_file)
        test_conf_file = open(full_path, "r")

        with mock.patch('__builtin__.open', create=True) as mock_open:
            mock_open.return_value.__enter__.side_effect = [test_conf_file,
                                                            'foolog']
            cls.conf = utils.Config(conf_file=conf_file)

        cls.auth = clients.Auth(conf=cls.conf)

        cls.test_zf = 'access_log_503335_2021081817.zip'
        cls.zip_container = {'aid': 54321, 'lid': 12345,
                             'hl': '2021081817', 'zip_path': 'tmp/processed',
                             'zip_file': cls.test_zf,
                             'cnt': 'lb_tester1_5806065_202108',
                             'remote_zf': '/tmp/processed/' + cls.test_zf}

    @mock.patch('swiftclient.client.Connection.get_account')
    def test_list_containers(self, mock_get_account):
        tok_endpoint = {'token': 'token',
                        'lb_region_ep': 'ep'}
        account = [{'id': 1,
                    'name': 'acc'},
                   {'id': 2,
                    'name': 'acc2'}]
        mock_get_account.return_value = account
        cf = CloudFiles(tok_endpoint)
        resp = CloudFiles.list_containers(cf)
        self.assertEqual(resp['id'], 2)
        self.assertEqual(resp['name'], 'acc2')

    @mock.patch('swiftclient.client.Connection.get_container')
    def test_list_container(self, mock_get_container):
        tok_endpoint = {'token': 'token',
                        'lb_region_ep': 'ep'}
        mock_get_container.return_value = {'aid': 54321, 'lid': 12345,
                                           'cnt': 'lb_tester1_5806065_202108',
                                           }
        cf = CloudFiles(tok_endpoint)
        name = 'cname'
        resp = CloudFiles.list_container(cf, name)
        self.assertEqual(resp, {'aid': 54321, 'lid': 12345,
                                'cnt': 'lb_tester1_5806065_202108',
                                })

    def test_empty_container(self):
        """This Method is never used"""

    @mock.patch('swiftclient.client.Connection.put_container')
    def test_create_container(self, mock_put_container):
        tok_endpoint = {'token': 'token',
                        'lb_region_ep': 'ep'}
        cf = CloudFiles(tok_endpoint)
        name = 'container'
        CloudFiles.create_container(cf, name)
        mock_put_container.assert_called_with(name, {})

    def test_upload_zip(self):
        """This method is never used"""
