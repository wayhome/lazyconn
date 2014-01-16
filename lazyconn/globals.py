#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import partial
from .local import LocalStack, LocalProxy


def _lookup_object(name):
    top = _request_ctx_stack.top
    if top is None:
        raise RuntimeError('working outside of request context')
    return getattr(top, name)

# context locals
_request_ctx_stack = LocalStack()
lg = LocalProxy(partial(_lookup_object, 'lg'))
