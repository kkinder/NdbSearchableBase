import unittest
import os
import sys

APPENGINE_PATHS = ['/usr/local/google_appengine']
for path in APPENGINE_PATHS:
    if os.path.exists(path):
        sys.path.append(path)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from google.appengine.ext import ndb, testbed
from google.appengine.datastore import datastore_stub_util

from NdbSearchableBase import SearchableModel


class MammalModel(SearchableModel):
    name = ndb.StringProperty()


class Person(MammalModel):
    address = ndb.TextProperty()


class Dog(MammalModel):
    tricks = ndb.TextProperty()


class EmailSignupTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_urlfetch_stub()

        ctx = ndb.get_context()
        ctx.set_cache_policy(False)
        ctx.set_memcache_policy(False)

    def test_basic_search(self):
        a = Person(name='Pants McEngineering', address='123 Flappy Street')
        a.put()
        a.search_update_index()

        person_results = Person.search('Pants')
        self.failUnlessEqual(person_results.number_found, 1)

        dog_results = Dog.search('Pants')
        self.failUnlessEqual(dog_results.number_found, 0)

        mammal_results = MammalModel.search('Pants')
        self.failUnlessEqual(mammal_results.number_found, 1)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == '__main__':
    unittest.main()
