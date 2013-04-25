
from google.appengine.ext import db
from google.appengine.api import memcache

# memcache keys
ALLPAGES = 'allpages'
ALLUSERS = 'allusers'


class MemcacheModel(db.Model):
    @classmethod
    def root_key(cls):
        # the root to all entity groups is the plural of their class names
        return db.Key.from_path(cls.__name__, cls.__name__ + 's')

    @classmethod
    def _all_from_cache(cls, key):
        client = memcache.Client()

        models = client.gets(key)

        if not models:
            # init memcache
            memcache.set(key, 0)

            models = cls.all()
            models.ancestor(cls.root_key())
            models = list(models)

            while True:  # Retry until written
                cache = client.gets(key)
                assert cache is not None, 'Uninitialized cache'
                if client.cas(key, models):
                    break

        return models

    def _put_in_db_and_cache(self, key, update=False):
        # write to db
        self.put()

        # write to cache
        if update:
            client = memcache.Client()
            while True:
                models = client.gets(key)
                for m in models:
                    if m.subject == self.subject:
                        models.remove(m)
                        break
                models.append(self)
                assert models is not None, 'Uninitialized cache'
                if client.cas(key, models):
                    break

        else:
            client = memcache.Client()
            while True:
                models = client.gets(key)
                models.append(self)
                assert models is not None, 'Uninitialized cache'
                if client.cas(key, models):
                    break


class Page(MemcacheModel):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def all_from_cache(cls):
        return cls._all_from_cache(ALLPAGES)

    @classmethod
    def get_by_name_from_cache(cls, subject):
        pages = Page.all_from_cache()
        for page in pages:
            if page.subject == subject:
                return page

    def put_in_db_and_cache(self, update=False):
        self._put_in_db_and_cache(ALLPAGES, update)


class User(MemcacheModel):
    name = db.StringProperty(required=True)
    password = db.TextProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def get_by_id_from_cache(cls, uid):
        users = User._all_from_cache(ALLUSERS)

        for u in users:
            if u.key().id() == int(uid):
                return u

    def put_in_db_and_cache(self):
        self._put_in_db_and_cache(ALLUSERS, False)
