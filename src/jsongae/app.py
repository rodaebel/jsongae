from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from json_rpc import JsonRpcHandler, ServiceMethod
import logging
import os


class MyData(db.Model):
    string = db.StringProperty()

    def json(self):
        return "{'string': %s}" % self.string


class MainHandler(webapp.RequestHandler):
    """The main handler."""

    def get(self):
        """Handles GET."""

        MyData.get_or_insert(key_name="foobar", string="Some test data.")

        user = users.get_current_user()

        template_vars = dict(user=users.get_current_user())

        path = os.path.join(
            os.path.dirname(__file__), 'templates', 'index.html')

        self.response.out.write(template.render(path, template_vars))


class RPCHandler(JsonRpcHandler):
    """Handles Remote Procedure Calls.

    No need to define post().
    """

    @ServiceMethod
    def data(self, key_name):
        entity = MyData.get_by_key_name(key_name)
        if entity:
            return entity.json()

    @ServiceMethod
    def notify(self, message, number):
        logging.info("%s (%i)", message, number)

    @ServiceMethod
    def test(self, message):
        return message


app = webapp.WSGIApplication([
    ('/', MainHandler),
    ('/rpc', RPCHandler),
], debug=True)


def main():
    """The main function."""

    webapp.util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
