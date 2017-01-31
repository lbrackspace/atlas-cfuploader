#!/usr/bin/env python

import unittest
from cfuploader import utils
from cfuploader import clients
import sys
import os

conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "test_conf.json")

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.conf = utils.Config(conf_file=conf_file)


    def test_region_selector(self):
        eps = {'endpoints':[{'type':'object-store','region':'ord',
                             'publicURL':'someORDURL'},
                            {'type': 'object-store','region':'dfw',
                             'publicURL': 'someDFWURL'}]}
        auth = clients.Auth(conf=self.conf)
        ep = auth.get_correct_region_endpoint(eps)
        self.assertEqual(ep, "someORDURL")
        self.assertNotEqual(ep,"someDFWURL")


