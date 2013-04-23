
import webapp2

from templates import *
from data import *


class BaseHandler(webapp2.RequestHandler):
    def render(self, file, dict):
        template = jinja_environment.get_template(file)
        self.response.out.write(template.render(dict))


class HomeHandler(BaseHandler):
    def get(self):
        pages = Page.all_from_cache()
        self.render('home.html', {'pages': pages})


class WikiHandler(BaseHandler):
    def get(self, page_name):
        page = Page.get_by_name_from_cache(page_name)
        if page:
            self.render('page.html', {'page': page})
        else:
            self.redirect('/_edit/%s' % page_name)


class EditHandler(BaseHandler):
    def get(self, page_name):
        page = Page.get_by_name_from_cache(page_name)
        self.render('edit.html',
                    {'name': page_name,
                     'content': page.content if page else ''})

    def post(self, page_name):
        content = self.request.get('content')
        if not content:
            self.redirect('/_edit/%s' % page_name)
            return

        page = Page.get_by_name_from_cache(page_name)
        if page:
            page.content = content
            page.put_in_db_and_cache(update=True)
        else:
            page = Page(subject=page_name, content=content)
            page.put_in_db_and_cache()

        self.redirect('/%s' % page_name)
