#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lazyconn
----------------------------------

Tests for `lazyconn` module.
"""

import unittest

from lazyconn import LazyConnection
from lazyconn import thread_safe
from lazyconn.globals import lg


class TService(object):

    def hello(self, name):
        return "hello {0}".format(name)


def create_test_client():
    return TService()


class TestLazyconn(unittest.TestCase):

    def setUp(self):
        LazyConnection.register_factory('test', create_test_client)

    def test_something(self):
        with LazyConnection() as conn:
            print conn.test.hello('wayhome')
            print lg.conn.test.hello('wayhome2')

    def test_decorator(self):
        @thread_safe
        def test():
            print lg.conn.test.hello("wayhome3")
        test()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
