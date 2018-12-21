# coding=utf-8
# Copyright 2018 The TensorFlow Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utils functions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import hashlib
import io
import os
import threading

import enum
from six.moves import urllib

import tensorflow as tf


class GenerateMode(enum.Enum):
  """`Enum` for how to treat pre-existing downloads and data.

  The default mode is `REUSE_DATASET_IF_EXISTS`, which will reuse both
  raw downloads and the prepared dataset if they exist.

  The generations modes:

  |                                    | Downloads | Dataset |
  | -----------------------------------|-----------|---------|
  | `REUSE_DATASET_IF_EXISTS` (default)| Reuse     | Reuse   |
  | `REUSE_CACHE_IF_EXISTS`            | Reuse     | Fresh   |
  | `FORCE_REDOWNLOAD`                 | Fresh     | Fresh   |
  """

  REUSE_DATASET_IF_EXISTS = 'reuse_dataset_if_exists'
  REUSE_CACHE_IF_EXISTS = 'reuse_cache_if_exists'
  FORCE_REDOWNLOAD = 'force_redownload'


# TODO(epot): Move some of those functions into core.py_utils


def build_synchronize_decorator():
  """Returns a decorator which prevents concurrent calls to functions.

  Usage:
    synchronized = build_synchronize_decorator()

    @synchronized
    def read_value():
      ...

    @synchronized
    def write_value(x):
      ...

  Returns:
    make_threadsafe (fct): The decorator which lock all functions to which it
      is applied under a same lock
  """
  lock = threading.Lock()

  def lock_decorator(fn):

    @functools.wraps(fn)
    def lock_decorated(*args, **kwargs):
      with lock:
        return fn(*args, **kwargs)

    return lock_decorated

  return lock_decorator


def get_file_name(url):
  """Returns file name of file at given url."""
  return os.path.basename(urllib.parse.urlparse(url).path) or 'unknown_name'


def read_checksum_digest(path, checksum_cls=hashlib.sha256):
  """Given a hash constructor, returns checksum digest and size of file."""
  checksum = checksum_cls()
  size = 0
  with tf.gfile.Open(path, 'rb') as f:
    while True:
      block = f.read(io.DEFAULT_BUFFER_SIZE)
      size += len(block)
      if not block:
        break
      checksum.update(block)
  return checksum.hexdigest(), size
