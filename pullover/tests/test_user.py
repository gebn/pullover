# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import requests

from pullover import User


class TestUser(unittest.TestCase):

    _USER_KEY = 'key'
    _USER = User(_USER_KEY)

    def test_sign(self):
        request = requests.Request(data={})
        self._USER.sign(request)
        self.assertDictEqual(request.data, {'user': self._USER_KEY})

    def test_str(self):
        self.assertEqual(str(self._USER), 'User({0})'.format(self._USER_KEY))
