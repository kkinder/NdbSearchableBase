import unittest
import os
import sys

if 'APPENGINE_SDK' in os.environ:
    sys.path.append(os.environ['APPENGINE_SDK'])
else:
    APPENGINE_PATHS = ['/usr/local/google_appengine']
    for path in APPENGINE_PATHS:
        if os.path.exists(path):
            sys.path.append(path)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

import dev_appserver
dev_appserver.fix_sys_path()

from google.appengine.ext import ndb, testbed
from google.appengine.ext.ndb.polymodel import PolyModel
from google.appengine.datastore import datastore_stub_util

from NdbSearchableBase import SearchableModel


class MammalModel(SearchableModel, PolyModel):
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
        pants = Person(name='Pants McEngineering Looperson', address='123 Flappy Street')
        pants.put()

        ralph = Dog(name='Ralph McDogface Looperson', tricks='fetching')
        ralph.put()

        person_results = Person.search('Pants')
        self.failUnlessEqual(person_results.number_found, 1)

        dog_results = Dog.search('Pants')
        self.failUnlessEqual(dog_results.number_found, 0)

        mammal_results = MammalModel.search('Pants')
        self.failUnlessEqual(mammal_results.number_found, 1)

        both_reusults = MammalModel.search('Looperson')
        self.failUnlessEqual(both_reusults.number_found, 2)

        dog_results2 = Dog.search('Looperson')
        self.failUnlessEqual(dog_results2.number_found, 1)


    def tearDown(self):
        self.testbed.deactivate()


if __name__ == '__main__':
    unittest.main()
