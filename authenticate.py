import webapp2
import re  # regular expressions
import datetime

from hashing import *
from templates import *
from data import *
import wiki

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


def valid_name(name):
    return USER_RE.match(name)


def valid_email(email):
    return EMAIL_RE.match(email)


def valid_password(password):
    return PASS_RE.match(password)


class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        cookie = str('name=; Path=/')
        self.response.headers.add_header('Set-Cookie', cookie)
        self.redirect(wiki.current_location)


class LoginHandler(webapp2.RequestHandler):
    def write_form(self, name='', error=''):
        template = jinja_environment.get_template('login.html')
        self.response.out.write(template.render({'name': name, 'error': error}))

    def get(self):
        self.write_form()

    def post(self):
        user_name = self.request.get('username')
        user_password = self.request.get('password')

        if not valid_name(user_name) or not valid_password(user_password):
            error = 'check your spelling, invalid user or password'
            self.write_form(user_name, error)

        else:
            # find user in db
            user = db.GqlQuery("select * from User where name=:1 limit 1", user_name).get()

            if user and valid_pw(user_name, user_password, user.password):
                # correct login
                key = str(user.key().id())
                cookie = str('name=%s; expires=%s; Path=/' % (make_secure_val(key), (datetime.date.today() +
                                                                                     datetime.timedelta(days=30)).strftime('%c')))
                self.response.headers.add_header('Set-Cookie', cookie)

                self.redirect(wiki.current_location)
            else:
                error = "can't find user or used an invalid password"
                self.write_form(user_name, error)


class SignupHandler(webapp2.RequestHandler):
    def write_form(self, name='', email='', name_error='',
                   password_error='', verify_error='', email_error=''):

        template = jinja_environment.get_template('signup.html')
        self.response.out.write(template.render({'name': name, 'email': email,
                                                 'name_error': name_error,
                                                 'password_error': password_error,
                                                 'verify_error': verify_error,
                                                 'email_error': email_error}))

    def get(self):
        self.write_form()

    def post(self):
        user_name = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        user_email = self.request.get('email')

        if user_name and valid_name(user_name):
            # check if user name is already taken
            taken = db.GqlQuery("select * from User where name=:1 limit 1", user_name).get()
            if taken:
                name_error = 'user name is already taken'
            else:
                name_error = ''
        else:
            name_error = "please only use letters and numbers"

        if password and valid_password(password):
            password_error = ''
        else:
            password_error = "not valid"

        if verify and password and password == verify:
            verify_error = ''
        else:
            verify_error = "passwords don't match"

        email_error = ''
        if user_email:
            if not valid_email(user_email):
                email_error = "that's not a valid email"
        else:
            user_email = ''

        if not password_error and not email_error and not name_error and not verify_error:

            # no error so save user in DB, write to cookie and redirect to welcome page
            new_user = User(parent=User.parent_key(), name=user_name, password=make_pw_hash(user_name, password), email=user_email)
            new_user.put()
            key = str(new_user.key().id())  # get id and convert to string
            cookie = str('name=%s; expires=%s; Path=/' % (make_secure_val(key), (datetime.date.today() +
                                                                                 datetime.timedelta(days=30)).strftime('%c')))
            self.response.headers.add_header('Set-Cookie', cookie)

            self.redirect(wiki.current_location)

        else:
            # errors found go back to form and tell user where the problem was
            self.write_form(user_name, user_email, name_error, password_error,
                            verify_error, email_error)
