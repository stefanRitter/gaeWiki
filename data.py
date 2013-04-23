
from google.appengine.ext import db
from google.appengine.api import memcache


class Page(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def all_from_cache(cls, update=False):
        key = 'allpages'
        client = memcache.Client()

        pages = client.gets(key)

        if pages is None or update:
            pages = cls.all()
            pages = list(pages)

            while pages:  # Retry loop
                if client.cas(key, pages):
                    break

        return pages


class User(db.Model):
    name = db.StringProperty(required=True)
    password = db.TextProperty(required=True)
    email = db.StringProperty()
