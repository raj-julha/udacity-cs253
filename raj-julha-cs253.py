import webapp2
import cgi
import re
import jinja2
import logging
import urllib
from time import gmtime, strftime, localtime

from google.appengine.ext import db
from model import *
from security import *



template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


form1 = """
<form method="post" action="/">
<textarea name="text" rows="10" cols="50" >%(text)s</textarea>
<br>
<input type="submit">
</form>
"""

form = """
<form method="post" action="/rot13">
<textarea name="text" rows="10" cols="50" >%(text)s</textarea>
<br>
<input type="submit">
</form>
"""


signupform = """
<html>
  <head>
    <title>Sign Upx</title>
    <style type="text/css">      
      .error {color: red}
    </style>

  </head>
<body>
<H1>Signup</H1>
<form method="post" action="/wiki/signup">
<table>
<tr>
<td>Username</td><td><input name="username" value="%(username)s" ></td>
<td class='error'>%(error_username)s</td>
</tr>
<tr>
<td>Password</td><td><input name="password" type="password" value="%(password)s" ></td>
<td class='error'>%(error_password)s</td>
</tr>
<tr>
<td>Verify</td><td><input name="verify" type="password" value="%(verify)s" > </td>
<td class='error'>%(error_verify)s</td>
</tr>
<tr>
<td>Email (optional)</td><td><input name="email" value="%(email)s" > </td>
<td class='error'>%(error_email)s</td>
</tr>
</table>
<br>
<input type="submit">
</form>
</body>
"""

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(webapp2.RequestHandler):
    def write_form(self, error="", text=""):
        self.response.out.write(form1 % {"error": error,
                                        "text": cgi.escape(text, quote = True)})

    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(form)
        self.write_form("","")

    def post(self):
        """Used when form method is post """
        #q = self.request.get("q")
        #self.response.out.write(q)
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(self.request)
        user_text = self.request.get('text')
        #text = self.rot13(user_text)
        text = user_text
        self.write_form("",text)

    def rot13(self, s):
        res = []
        for c in s:
            res.append(self.convert_rot13(c))
        return ''.join(res)

    def convert_rot13(self, s):
        islower = s.islower()
        charcode = ord(s.lower())
        if charcode in range(ord('a'),ord('z')+1):
            newcode = charcode + 13
            if newcode > ord('z'):
                diff = newcode - ord('z')
                # less 1 since we're adding from a and a is included
                # in the sum
                newcode = ord('a') + diff -1
            
            if islower:
                return chr(newcode)
            else:
                return chr(newcode).upper()
        else:
            return s

class Rot13Handler(webapp2.RequestHandler):
    def write_form(self, error="", text=""):
        self.response.out.write(form % {"error": error,
                                        "text": cgi.escape(text, quote = True)})

    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(form)
        self.write_form("","")

    def post(self):
        """Used when form method is post """
        #q = self.request.get("q")
        #self.response.out.write(q)
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(self.request)
        user_text = self.request.get('text')
        text = user_text.encode('rot13')
        self.write_form("",text)

signupformfields = {"error": "",
                    "username": "",
                    "error_username": "",
                    "password": "",
                    "error_password": "",
                    "verify": "",
                    "error_verify": "",
                    "email": "",
                    "error_email": ""
                    }


class SignupHandler(webapp2.RequestHandler):
    def write_form(self, fields):
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(fields)        
        #logging.info(signupformfields)
        #logging.info(signupform % fields)
        self.response.out.write(signupform % fields)

    def init_formfields(self):
        signupformfields['username'] = ''
        signupformfields['error_username'] = ''
        signupformfields['password'] = ''
        signupformfields['error_password'] = ''
        signupformfields['verify'] = ''
        signupformfields['error_verify'] = ''
        signupformfields['email'] = ''
        signupformfields['error_email'] = ''

    def get(self):
        self.init_formfields()
        self.write_form(signupformfields)

    def post(self):
        """Used when form method is post """
        signupformfields['username'] =  cgi.escape(self.request.get('username'), quote = True)
        signupformfields['password'] = cgi.escape(self.request.get('password'), quote = True)
        signupformfields['verify'] = cgi.escape(self.request.get('verify'), quote = True)
        signupformfields['email'] = cgi.escape(self.request.get('email'), quote = True)

        if self.valid_form():
            id = self.save()
            # self.redirect("/welcome?username=%s id=%s" %  (signupformfields['username'], id))
            self.redirect("/blog/welcome")                        
        else:
            self.write_form(signupformfields)
        
    def save(self):
        pwdhash = hash_str(signupformfields['password'])
        user = User(username=signupformfields['username'], 
                    email=signupformfields['email'],
                    passwordhash= pwdhash)
        user.put()
        # and redirect the user to the entry
        id = user.key().id()
        #hw4 = 'HW4=%s|%s; Path=/' % (signupformfields['username'], pwdhash)
        # above raises InvalidResponseError: header values must be str, got 'unicode'
        hw4 = str('HW4=%s|%s; Path=/' % (signupformfields['username'], pwdhash))
        logging.debug(hw4)
        self.response.headers.add_header('Set-Cookie', hw4)

        return id

        
      

    def valid_form(self):
        logging.debug('Testing debug')
        logging.info('Testing info') # This shows in app engine terminal screen

        signupformfields['error_username'] = ''
        signupformfields['error_password'] = ''
        signupformfields['error_verify'] = ''
        signupformfields['error_email'] = ''

        user_is_valid = True
        username = self.valid_username(signupformfields['username'])

        if not username:
            user_is_valid = False
            signupformfields['error_username'] = 'Username is invalid'

        if self.duplicate_user(signupformfields['username']): 
            user_is_valid = False
            signupformfields['error_username'] = 'This user already exists'
        
        password = self.valid_password(self.request.get('password'))
        verify = self.valid_password(self.request.get('verify'))
        password_verify_same = True
        if signupformfields['password'] != signupformfields['verify']:
            signupformfields['error_verify'] = 'Password and verify are not same' 
            password_verify_same = False
        else:
            logging.debug('Password: %s, verify: %s', signupformfields['password'], signupformfields['verify'])

        if not password:
            signupformfields['error_password'] = 'Password is invalid'
            signupformfields['password'] = ''

        if not verify:
            signupformfields['error_verify'] = 'Verify is invalid'
            signupformfields['verify'] = ''
       
        email = self.request.get('email')
        emailisvalid = True
        if email != '':
            email = self.valid_email(self.request.get('email'))
            if not email:
                emailisvalid = False
                signupformfields['error_email'] = 'Email is invalid'
            
        logging.debug('username: %s', signupformfields['username'])
        logging.debug('password: %s', signupformfields['password'])
        logging.debug('verify: %s', signupformfields['verify'])
        logging.debug('email: %s', signupformfields['email'])
        logging.debug('emailisvalid: %s', emailisvalid)
        logging.debug('password_verify_same: %s', password_verify_same)
        logging.debug('user_is_valid: %s', user_is_valid)

        logging.debug('username and password and verify ' 
                      'and emailisvalid and password_verify_same '
                      'and user_is_valid: %s ', username and password and verify and emailisvalid and password_verify_same and user_is_valid)


        if not(username and password and verify and emailisvalid and password_verify_same and user_is_valid):
            # clear password
            signupformfields['password'] = ''
            signupformfields['verify'] = ''
            #self.write_form(signupformfields)
            return False
        else:
            # self.response.out.write("Thanks for registering")
            #self.write_form(signupformfields)
            #self.redirect("/welcome?username=%s" %  signupformfields['username'])
            return True


    def duplicate_user(self, username):
        users = User.gql("WHERE username = :1", username)
        if users.count() > 0:    
            for user in users:
                logging.debug('duplicate_user: %s', user.username)
            return True
        else:
            return False

        
    def valid_username(self,username):
        return USER_RE.match(username)

    def valid_password(self,password):
        return PASSWORD_RE.match(password)

    def valid_email(self,email):
        return EMAIL_RE.match(email)

class LoginHandler(Handler):    
    def render_front(self, username="", password="", error=""):
         #self.render("login.html", title=title, art=art, error=error, arts=arts)
        self.render("login.html", username=username, password=password, error=error)
    def get(self):
        self.render_front()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        user = self.validate_user(username, password)
        if username and password and user:
            
            s = "Welcome %s!" % user.username
            write_authentication_cookie(self.response, user.username, user.passwordhash)
            self.response.write(s)
            
        else:
            error = "Invalid user"
            #self.render("front.html", error = error)
            self.render_front(username, password, error)

    def validate_user(self, username, password):
        pwdhash = ''
        users = User.gql("WHERE username = :1", username)
        if users.count() > 0:    
            user = users[0]
            pwdhash = user.passwordhash
            tocheck = '%s|%s' % (password, pwdhash)
            if check_secure_val(tocheck):
                return user
            logging.debug('user: %s password|hash: %s', user.username, tocheck)
        else:
            return None

class LogoutHandler(Handler):    
    def get(self):
        delete_authentication_cookie(self.response)
        self.redirect("/wiki/signup")        

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        # username = self.request.get("username")
        # self.request.cookies.get(name)
        hw4_cookie = self.request.cookies.get('HW4')
        if hw4_cookie:
            # username = hw4_cookie
            username = hw4_cookie.split('|')[0]
            self.response.write("Welcome, %(username)s !" % {'username': username })
        else:
            self.redirect("/wiki/signup")    
            # self.response.write("Welcome, you're not autheticated")

class TestHandler(webapp2.RequestHandler):
    
    def get(self):
        """Used when form method is get """
        q = self.request.get("q")
        self.response.out.write(q)
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(self.request)
    def post(self):
        """Used when form method is post """
        #q = self.request.get("q")
        #self.response.out.write(q)
        #self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(self.request)

application = webapp2.WSGIApplication(
                                     [('/blog', MainPage),
                                      ('/rot13', Rot13Handler),
                                      ('/blog/signup', SignupHandler),
                                      ('/blog/welcome', WelcomeHandler),
                                      ('/blog/login', LoginHandler),
                                      ('/blog/logout', LogoutHandler),
                                      ('/testform', TestHandler),
                                      ('/wiki/signup', SignupHandler),
                                      ('/wiki/welcome', WelcomeHandler),
                                      ('/wiki/login', LoginHandler),
                                      ('/wiki/logout', LogoutHandler)
                                      ],                                      
                                     debug=True)

