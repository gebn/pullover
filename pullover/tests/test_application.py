# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import requests

from pullover import Application


class TestApplication(unittest.TestCase):

    _APP_TOKEN = 'token'
    _APP = Application(_APP_TOKEN)

    def test_sign(self):
        request = requests.Request(data={})
        self._APP.sign(request)
        self.assertDictEqual(request.data, {'token': self._APP_TOKEN})

    def test_str(self):
        self.assertEqual(str(self._APP),
                         'Application({0})'.format(self._APP_TOKEN))
