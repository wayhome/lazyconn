==================================
A lazy connection context manager
==================================
A lazy connection context manager


使用说明
=======================
`LazyConnection` 是一个线程安全的连接管理器，它将会创建一个连接上下文(context)，这个上下文管理一堆在它上面注册的工场函数(factory)。

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

`lg` 是一个线程安全的全局对象，它只在连接上下文中有效，它的 **conn** 属性对应一个连接上下文。

.. note:: 在 context 生命周期外，不能使用此对象。

使用范例::

   from lazyconn.globals import lg

    with LazyConnection() as conn:
        conn.test1.hello('wayhome')
        lg.conn.test1.hello('wayhome2')


`thread_safe` 是一个装饰器, 被装饰的函数将会在一个连接上下文中执行。`lg` 对象可以在被装饰的函数内部使用。

使用范例::

    from lazyconn import thread_safe

    @thread_safe
    def test():
        lg.conn.test1.hello('wayhome3')
