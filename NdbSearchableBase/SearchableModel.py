"""
Includes BaseModel, which can be used as an ndb mixin that's fully searchable.
"""
import string

from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.ext.ndb.polymodel import PolyModel

SEARCHABLE_PROPERTY_TYPES = {
    ndb.TextProperty: search.TextField,
    ndb.IntegerProperty: search.NumberField,
    ndb.FloatProperty: search.NumberField,
    ndb.DateProperty: search.DateField,
    ndb.KeyProperty: search.AtomField
}

alphabet = string.digits + string.letters


class SearchableModel(object):
    """
    Mix this class into your ndb models to make them searchable.
    """
    searching_enabled = True
    searchable_fields = None  # defaults to all fields
    search_index = 'general-index'

    @classmethod
    def search_get_index(cls):
        """
        Returns index to be used. You may override this.

        :return: instance of search.Index
        """
        return search.Index(name=cls.search_index)

    @staticmethod
    def search_get_document_id(key):
        """
        Returns an index document id from a key. Defaults to just using the key's urlsafe string.

        :param key: ndb.Key instance
        :return: String for document index
        """
        return key.urlsafe()

    @classmethod
    def search(cls,
               query_string,
               options=None,
               enable_facet_discovery=False,
               return_facets=None,
               facet_options=None,
               facet_refinements=None,
               deadline=None,
               **kwargs):
        """
        Searches the index. Conveniently searches only for documents that belong to instances of this class.

        :param query_string: The query to match against documents in the index. See search.Query() for details.
        :param options: A QueryOptions describing post-processing of search results.
        :param enable_facet_discovery: discovery top relevent facets to this search query and return them.
        :param return_facets: An iterable of FacetRequest or basestring as facet name to
                return specific facet with the result.
        :param facet_options: A FacetOption describing processing of facets.
        :param facet_refinements: An iterable of FacetRefinement objects or refinement
                        token strings used to filter out search results based on a facet value.
                        refinements for different facets will be conjunction and refinements for
                        the same facet will be disjunction.
        :param deadline: Deadline for RPC call in seconds; if None use the default.
        :param kwargs: A SearchResults containing a list of documents matched, number returned
              and number matched by the query.
        :return: A SearchResults containing a list of documents matched, number returned
              and number matched by the query.
        :raises: QueryError: If the query string is not parseable.
              TypeError: If any of the parameters have invalid types, or an unknown
                attribute is passed.
              ValueError: If any of the parameters have invalid values (e.g., a
                negative deadline).
        """
        search_class = cls.search_get_class_names()[-1]
        query_string += ' ' + 'class_name:%s' % (search_class,)

        q = search.Query(
            query_string=query_string,
            options=options,
            enable_facet_discovery=enable_facet_discovery,
            return_facets=return_facets,
            facet_options=facet_options,
            facet_refinements=facet_refinements
            )
        index = cls.search_get_index()
        return index.search(q, deadline=deadline, **kwargs)

    def search_update_index(self):
        """
        Updates the search index for this instance.

        This happens automatically on put.
        """
        doc_id = self.search_get_document_id(self.key)

        fields = [search.AtomField('class_name', name) for name in self.search_get_class_names()]

        index = self.search_get_index()

        if self.searchable_fields is None:
            searchable_fields = []

            for field, prop in self._properties.items():
                if field == 'class':
                    continue
                for class_, field_type in SEARCHABLE_PROPERTY_TYPES.items():
                    if isinstance(prop, class_):
                        searchable_fields.append(field)
        else:
            searchable_fields = self.searchable_fields

        for f in set(searchable_fields):
            prop = self._properties[f]
            value = getattr(self, f)
            field = None
            field_found = False
            for class_, field_type in SEARCHABLE_PROPERTY_TYPES.items():
                if isinstance(prop, class_):
                    field_found = True
                    if value is not None:
                        if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
                            for v in value:
                                field = field_type(name=f, value=v)
                        elif isinstance(value, ndb.Key):
                            field = field_type(name=f, value=value.urlsafe())
                        else:
                            field = field_type(name=f, value=value)
            if not field_found:
                raise ValueError('Cannot find field type for %r on %r' % (prop, self.__class__))

            if field is not None:
                fields.append(field)

        document = search.Document(doc_id, fields=fields)
        index.put(document)

    @classmethod
    def search_get_class_names(cls):
        """
        Returns class names for use in document indexing.
        """
        if hasattr(cls, '_class_key'):
            class_names = []
            for n in cls._class_key():
                class_names.append(n)
            return class_names
        else:
            return [cls.__name__]

    @classmethod
    def from_urlsafe(cls, urlsafe):
        """
        Returns an instance of the model from a urlsafe string.

        :param urlsafe: urlsafe key
        :return: Instance of cls
        """
        try:
            key = ndb.Key(urlsafe=urlsafe)
        except:
            return None
        obj = key.get()
        if obj and isinstance(obj, cls):
            return obj

    @classmethod
    def get_from_search_doc(cls, doc_id):
        """
        Returns an instance of the model from a search document id.

        :param doc_id: Search document id
        :return: Instance of cls
        """
        # If the document was passed instead of the doc_id, get the document.
        if hasattr(doc_id, 'doc_id'):
            doc_id = doc_id.doc_id
        return cls.from_urlsafe(doc_id)

    @classmethod
    def _pre_delete_hook(cls, key):
        """
        Removes instance from index.
        """
        if cls.searching_enabled:
            doc_id = cls.search_get_document_id(key)
            index = cls.search_get_index()
            index.delete(doc_id)

    def _post_put_hook(self, future):
        """
        Updates or creates instance in index.
        """
        if self.searching_enabled:
            self.search_update_index()
