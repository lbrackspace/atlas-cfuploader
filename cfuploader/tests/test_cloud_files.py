import os
import unittest

import mock as mock
from mock import mock_open

from cfuploader import utils
from cfuploader.clients import CloudFiles
from swiftclient.client import Connection

conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "test_conf.json")


class TestClientCloudFiles(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     conf = utils.Config(conf_file=conf_file)

    def setUp(self):
        self.conf = utils.Config(conf_file=conf_file)

        read_data = self.conf.log_file
        mock_open = mock.mock_open(read_data=read_data)
        with mock.patch("__builtin__.open", mock_open) as mock_file:
            assert open(read_data).read() == "/home/crc/cfuploader.log"
            mock_file.assert_called_with("/home/crc/cfuploader.log")

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
        mock_get_container.return_value = 'container1'
        cf = CloudFiles(tok_endpoint)
        name = 'cname'
        resp = CloudFiles.list_container(cf, name)
        self.assertEqual(resp, 'container1')

    @mock.patch('swiftclient.client.Connection.delete_object')
    def test_delete_object(self, mock_delete_object):
        tok_endpoint = {'token': 'token',
                        'lb_region_ep': 'ep'}
        container = {'obj1': {'name': 'test1'},
                     'obj2': {'name': 'test2'}
                     }
        mock_delete_object.return_value = None
        cf = CloudFiles(tok_endpoint)
        resp = CloudFiles.x(cf, container, 'obj1')
        self.assertIsNone(resp)

    # @mock.patch('swiftclient.client.Connection.get_container')
    # @mock.patch('swiftclient.client.Connection.put_container')
    # def test_empty_container(self, mock_get_container, mock_delete_object):
    #     tok_endpoint = {'token': 'token',
    #                     'lb_region_ep': 'ep'}
    #     container = {'obj1': {'name': 'test1'},
    #                  'obj2': {'name': 'test2'}
    #                  }
    #     container = {'info': [{'cname': 'cntr1'}],
    #                  'objs': [{'name': 'obj1'}]}
    #     # mock_get_container.return_value = container
    #     cf = CloudFiles(tok_endpoint)
    #     CloudFiles.empty_container(cf, container)
    #     # mock_delete_object.assert_called_with(container, 'test1')

    @mock.patch('swiftclient.client.Connection.put_container')
    def test_create_container(self, mock_put_container):
        tok_endpoint = {'token': 'token',
                        'lb_region_ep': 'ep'}
        cf = CloudFiles(tok_endpoint)
        name = 'container'
        CloudFiles.create_container(cf, name)
        mock_put_container.assert_called_with(name, {})

    # @mock.patch('swiftclient.client.Connection.put_object')
    # @mock.patch('os.path.expanduser')
    # def test_create_container(self, mock_put_object, mock_expanduser):
    #     tok_endpoint = {'token': 'token',
    #                     'lb_region_ep': 'ep'}
    #     cf = CloudFiles(tok_endpoint)
    #     cnt_name = 'container'
    #     remote_name = 'rmt'
    #     fp = 'fp'
    #     mock_expanduser.return_value = fp
    #     CloudFiles.upload_file(cf, "cnt_name", "remote_name", fp)

    @mock.patch('swiftclient.client.Connection.upload_zip')
    def test_create_container(self, mock_upload_zip):
        tok_endpoint = {'token': 'token',
                        'lb_region_ep': 'ep'}
        cf = CloudFiles(tok_endpoint)
        name = 'container'
        CloudFiles.create_container(cf, name)
        mock_upload_file.assert_called_with('local_name', 'cnt', 'remote')
