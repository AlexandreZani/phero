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

    with self.assertRaises(phero.UnknownService):
      registry.process(ctx, service_name, args)

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

    with self.assertRaises(phero.MissingRequiredArgument):
      multiply_service(ctx, args)

  def test_unknown_arg(self):
    def multiply(ctx, a, b):
      return a * b
    multiply_service = phero.Service(multiply)

    args = { 'a': 3, 'b': 4, 'c': 3 }
    ctx = {}

    with self.assertRaises(phero.UnknownArgument):
      multiply_service(ctx, args)

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
