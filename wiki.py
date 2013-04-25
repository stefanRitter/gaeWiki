
import webapp2

from templates import *
from data import *
from hashing import *

current_location = '/'


class BaseHandler(webapp2.RequestHandler):
    def render(self, file, dict):
        template = jinja_environment.get_template(file)
        self.response.out.write(template.render(dict))

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)

        global current_location
        current_location = self.request.url

        self.user = None
        user_id_cookie = self.request.cookies.get('name', None)
        if user_id_cookie:
            user_id = check_secure_val(user_id_cookie)
            if user_id:
                self.user = User.get_by_id_from_cache(int(user_id))


class HomeHandler(BaseHandler):
    def get(self):
        pages = Page.all_from_cache()
        self.render('home.html', {'user': self.user, 'pages': pages})


class WikiHandler(BaseHandler):
    def get(self, page_name):
        page = Page.get_by_name_from_cache(page_name)
        if page:
            self.render('page.html', {'user': self.user, 'page': page,
                                      'history': page_name, 'edit': page_name})

        else:
            self.redirect('/_edit/%s' % page_name)


class EditHandler(BaseHandler):
    def get(self, page_name):
        # only allow edit if logged in
        if self.user:
            page = Page.get_by_name_from_cache(page_name)
            self.render('edit.html',
                        {'user': self.user, 'view': page_name,
                         'page_name': page_name, 'history': page_name,
                         'content': page.content if page else ''})
        else:
            self.redirect('/login')

    def post(self, page_name):
        if not self.user:
            self.redirect('/login')  # if logged out in the meantime go back

        content = self.request.get('content')
        if not content:
            self.redirect('/_edit/%s' % page_name)
            return

        page = Page.get_by_name_from_cache(page_name)
        if page:
            # if we have a version already then save this one as a new version
            new_version = Page(subject=page_name, content=content, parent=page)
            new_version.put_in_db_and_cache(True)
        else:
            page = Page(subject=page_name, content=content, parent=Page.parent_key())
            page.put_in_db_and_cache()

        self.redirect('/%s' % page_name)


class HistoryHandler(BaseHandler):
    def get(self, page_name):
        page = Page.get_by_name_from_cache(page_name)
        self.render('history.html', {'user': self.user, 'edits': [page, page]})
