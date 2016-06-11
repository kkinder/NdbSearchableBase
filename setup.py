#!/usr/bin/env python
# Copyright 2016 Ken Kinder. All Rights Reserved.
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

import distribute_setup

distribute_setup.use_setuptools()

import setuptools

# To debug, set DISTUTILS_DEBUG env var to anything.
setuptools.setup(
    name="NdbSearchableBase",
    version="1.1",
    packages=['NdbSearchableBase'],
    author="Ken Kinder",
    author_email="ken@kkinder.com",
    keywords=['google-app-engine', 'ndb', 'full-text', 'search', 'indexing'],
    url="https://github.com/kkinder/NdbSearchableBase",
    license="Apache License 2.0",
    description="Searchable Base Model for NDB",
    zip_safe=True
)
