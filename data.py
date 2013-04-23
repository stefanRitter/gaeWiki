
from google.appengine.ext import db
from google.appengine.api import memcache

key = 'allpages'


class Page(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def all_from_cache(cls, update=False):
        client = memcache.Client()

        pages = client.gets(key)

        if not pages:
            memcache.set(key, 0)  # init memcache
            update = True

        if update:
            pages = cls.all()
            pages = list(pages)

            while True:  # Retry until written
                cache = client.gets(key)
                assert cache is not None, 'Uninitialized cache'
                if client.cas(key, pages):
                    break

        return pages

    @classmethod
    def get_by_name_from_cache(cls, subject):
        pages = Page.all_from_cache()
        for page in pages:
            if page.subject == subject:
                return page

    def put_in_db_and_cache(self, update=False):
        # write to db
        self.put()

        # write to cache
        if update:
            client = memcache.Client()
            while True:
                pages = client.gets(key)
                for p in pages:
                    if p.subject == self.subject:
                        pages.remove(p)
                        break
                pages.append(self)
                assert pages is not None, 'Uninitialized cache'
                if client.cas(key, pages):
                    break

        else:
            client = memcache.Client()
            while True:
                pages = client.gets(key)
                pages.append(self)
                assert pages is not None, 'Uninitialized cache'
                if client.cas(key, pages):
                    break


class User(db.Model):
    name = db.StringProperty(required=True)
    password = db.TextProperty(required=True)
    email = db.StringProperty()
