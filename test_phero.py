#!/usr/bin/env python

# Copyright 2012 (Alexandre Zani)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import phero
import unittest


class TestRequestProcessor(unittest.TestCase):
  def setUp(self):
    self.logic_registry = phero.ServiceRegistry()
    self.auth_registry = phero.ServiceRegistry()
    self.registries = [
        ('auth', self.auth_registry),
        ('main', self.logic_registry),
    ]

    def simple_auth(ctx, username):
      return username
    self.auth_registry.register(simple_auth)

    def whoami(ctx, all_caps=False):
      if all_caps:
        return ctx['auth'].upper()
      return ctx['auth']
    self.logic_registry.register(whoami)

  def test_basic(self):
    request = {
        'main': {
          'service': 'whoami',
          'args': { 'all_caps': True }
        },
        'auth': {
          'service': 'simple_auth',
          'args': { 'username': 'alex' }
        }
    }
    expected = { 'result': 'ALEX' }

    actual = phero.process_request(self.registries, request)

    self.assertEquals(expected, actual)

  def test_no_args(self):
    def whoami_simple(ctx):
      return ctx['auth']
    self.logic_registry.register(whoami_simple)

    request = {
        'main': {
          'service': 'whoami_simple',
        },
        'auth': {
          'service': 'simple_auth',
          'args': { 'username': 'alex' }
        }
    }
    expected = { 'result': 'alex' }

    actual = phero.process_request(self.registries, request)

    self.assertEquals(expected, actual)

  def test_phero_error(self):
    request = {
        'main': {
          'service': 'does_not_exist'
        }
    }
    expected = {
        'error': 'UnknownService',
        'details': { 'service': 'does_not_exist' }
    }

    actual = phero.process_request(self.registries, request)

    self.assertEquals(expected, actual)

  def test_custom_error(self):
    class AuthError(phero.PheroError): pass
    def bad_auth(ctx):
      raise AuthError(msg='I hate you')
    self.auth_registry.register(bad_auth)

    request = {
        'auth': {
          'service': 'bad_auth'
        }
    }
    expected = {
        'error': 'AuthError',
        'details': { 'msg': 'I hate you' }
    }

    actual = phero.process_request(self.registries, request)

    self.assertEquals(expected, actual)

  def test_generic_error(self):
    def bad_method(ctx):
      raise KeyError
    self.logic_registry.register(bad_method)

    request = {
        'main': {
          'service': 'bad_method'
        }
    }
    
    with self.assertRaises(KeyError):
      phero.process_request(self.registries, request)

    expected = {
        'error': 'GenericInternalError'
    }

    actual = phero.process_request(self.registries, request, catch_all=True)

    self.assertEquals(expected, actual)


class TestServiceRegistry(unittest.TestCase):
  def test_basic(self):
    def multiply(ctx, a, b):
      return a * b

    registry = phero.ServiceRegistry()
    registry.register(multiply)

    args = { 'a': 3, 'b': 4 }
    service_name = 'multiply'
    ctx = {}
    expected = 12

    actual = registry.process(ctx, service_name, args)

    self.assertEquals(expected, actual)

  def test_unknown_service(self):
    registry = phero.ServiceRegistry()

    args = { 'a': 3, 'b': 4 }
    service_name = 'multiply'
    ctx = {}
    expected = 12

    with self.assertRaises(phero.UnknownService) as cmt:
      registry.process(ctx, service_name, args)
    self.assertEquals(cmt.exception.details, { 'service': 'multiply' })

  def test_default_service(self):
    def default(ctx):
      return "Default Service"

    registry = phero.ServiceRegistry()
    registry.register_default(default)

    ctx = {}
    expected = "Default Service"

    actual = registry.process(ctx, None, None)

    self.assertEquals(expected, actual)

  def test_default_default_service(self):
    registry = phero.ServiceRegistry()

    ctx = {}
    expected = None

    actual = registry.process(ctx, None, None)

    self.assertEquals(expected, actual)


class TestService(unittest.TestCase):
  def test_basic(self):
    def multiply(ctx, a, b):
      return a * b
    multiply_service = phero.Service(multiply)

    args = { 'a': 3, 'b': 4 }
    ctx = {}
    expected = 12

    actual = multiply_service(ctx, args)

    self.assertEquals(expected, actual)

  def test_missing_required_arg(self):
    def multiply(ctx, a, b):
      return a * b
    multiply_service = phero.Service(multiply)

    args = { 'a': 3 }
    ctx = {}

    with self.assertRaises(phero.MissingRequiredArgument) as cmt:
      multiply_service(ctx, args)
    self.assertEquals(cmt.exception.details, { 'arg': 'b' })

  def test_unknown_arg(self):
    def multiply(ctx, a, b):
      return a * b
    multiply_service = phero.Service(multiply)

    args = { 'a': 3, 'b': 4, 'c': 3 }
    ctx = {}

    with self.assertRaises(phero.UnknownArgument) as cmt:
      multiply_service(ctx, args)
    self.assertEquals(cmt.exception.details, { 'arg': 'c' })

  def test_default_arg(self):
    def multiply(ctx, a, b=2):
      return a * b

    multiply_service = phero.Service(multiply)

    args = { 'a': 3 }
    ctx = {}
    expected = 6

    actual = multiply_service(ctx, args)

    self.assertEquals(expected, actual)

if __name__ == '__main__':
  unittest.main()
