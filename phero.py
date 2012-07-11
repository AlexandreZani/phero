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

import inspect


def process_request(registries, request, catch_all=False):
  ctx = {}
  for (registry_name, registry) in registries:
    service_request = request.get(registry_name, {})
    service_name = service_request.get('service', None)
    args = service_request.get('args', {})
    try:
      result = registry.process(ctx, service_name, args)
    except PheroError as err:
      return {
          'error': err.__class__.__name__,
          'details': err.details
      }
    except Exception:
      if (catch_all):
        return { 'error': 'GenericInternalError' }
      raise

    ctx[registry_name] = result
  return { 'result': result }


class ServiceRegistry(object):
  def __init__(self):
    self.services = {}
    self.register_default(lambda ctx: None)

  def register(self, function):
    self.services[function.func_name] = Service(function)

  def register_default(self, function):
    self.services[None] = Service(function)

  def process(self, ctx, service_name, args):
    if args is None:
      args = {}
    try:
      service = self.services[service_name]
    except KeyError:
      raise UnknownService(service=service_name)
    return service(ctx, args)


class Service(object):
  def __init__(self, func):
    self.func = func
    argspec = inspect.getargspec(func)
    self.args = frozenset(argspec.args[1:])

    # Required args are all the args minux the defaults
    default_idx = None
    if argspec.defaults:
      default_idx = len(argspec.defaults) * -1

    self.required_args = argspec.args[1:default_idx]

  def _bind(self, args):
    for required_arg in self.required_args:
      if required_arg not in args:
        raise MissingRequiredArgument(arg=required_arg)

    for arg in args.keys():
      if arg not in self.args:
        raise UnknownArgument(arg=arg)

  def __call__(self, ctx, args):
    self._bind(args)
    return self.func(ctx, **args)


class PheroError(Exception):
  def __init__(self, **kwargs):
    self.details = kwargs


class RegistryError(PheroError): pass
class UnknownService(RegistryError): pass
class ServiceBindError(PheroError): pass
class MissingRequiredArgument(ServiceBindError): pass
class UnknownArgument(ServiceBindError): pass
