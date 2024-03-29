import os
import cgi
import webapp2
import jinja2
import logging
import urllib
import json # check if webapp2 exposes any json functionality
from time import gmtime, strftime, localtime, time


# The entries below must be added to the app.yaml file
#libraries:
#- name: jinja2
#  version: "2.6"



template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

