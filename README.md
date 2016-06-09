[![Build Status](https://travis-ci.org/kkinder/NdbSearchableBase.svg?branch=master)](https://travis-ci.org/kkinder/NdbSearchableBase)

# NdbSearchableBase - Searchable Base Model for NDB
If you're using Google App Engine with [NDB](https://cloud.google.com/appengine/docs/python/ndb/), you've probably found that NDB doesn't natively support [document text indexing](https://cloud.google.com/appengine/docs/python/search/), which is a separate service available under App Engine.

NdbSearchableBase brings together NDB with document indexing. Just base your ndb model off of NdbSearchableBase:
    
    from NdbSearchableBase import SearchableModel
    
    class Contact(SearchableModel):
        name = ndb.StringProperty()
        address = ndb.TextProperty()
    
    def example():
        joe = Contact(name='Joe', address='1234 Fake Street')
        joe.put()
        search_results = Contact.search('Fake')

The code itself is very small, simple, and easy to understand.
