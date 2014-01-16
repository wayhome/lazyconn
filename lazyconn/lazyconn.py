#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LazyConnection是一个线程安全的连接管理器，它将会创建一个连接上下文(context)，这个上下文管理一堆在它上面注册的工场函数(factory)。

- 在context 的生命周期范围内，factory 将会根据使用到的情况按需创建(最多只会被创建一次), 通过以 context 上注册的名字作为属性来访问,
  可得到该 factory 的一个实例。

- 在context 的生命周期结束时，将会自动执行清理工作，factory 的实例会被销毁，如果有 close 方法也将被调用。

使用范例::

    from lazyconn import LazyConnection

    def create_test1_client():
        return snow(host='127.0.0.1', port=1234)

    def create_test2_client1():
        return wish(host='127.0.0.1', port=1235)

    # register
    LazyConnection.register_factory('test', create_test1_client)
    LazyConnection.register_factory('test2', create_test2_client)

    # context life
    with LazyConnection() as conn:
        conn.test1.hello('wayhome')
"""
import weakref
from .globals import _request_ctx_stack
from .local import Local


class Magic(object):

    def __init__(self, instance):
        self.instance = instance

    def __getattr__(self, name):
        if name not in self.instance.lg.connections:
            factory = self.instance._factories[name]
            self.instance.lg.connections[name] = factory()
        return self.instance.lg.connections[name]


class LazyConnection(object):
    _factories = {}

    def __init__(self):
        self.lg = Local()
        self.lg.connections = {}
        self.lg.conn = weakref.proxy(self)

    @classmethod
    def register_factory(cls, name, factory):
        cls._factories[name] = factory

    def __getattr__(self, name):
        if name in self._factories:
            return Magic(self).__getattr__(name)
        return super(LazyConnection, self).__getattr__(name)

    def __enter__(self):
        self.push()
        return self

    def push(self):
        """Binds the request context to the current context."""
        _request_ctx_stack.push(self)

    def pop(self):
        """Pops the request context and unbinds it by doing that.
        """
        _request_ctx_stack.pop()

    def __exit__(self, exc_type, exc_value, tb):
        for conn in self.lg.connections:
            if hasattr(conn, 'close'):
                conn.close()
        del self.lg.connections
        self.lg.__release_local__()


def thread_safe(func):
    def wrapper(*args, **kwargs):
        with LazyConnection():
            return func(*args, **kwargs)
    return wrapper


if __name__ == '__main__':
    class TService(object):

        def hello(self, name):
            return "hello {0}".format(name)

    def create_test_client():
        return TService()

    LazyConnection.register_factory('test', create_test_client)
    with LazyConnection() as conn:
        print conn.test.hello('wayhome')
