from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from json_rpc import JsonRpcHandler, ServiceMethod


class MyData(db.Model):
    string = db.StringProperty()

    def json(self):
        return "{'string': %s}" % self.string


class MainHandler(webapp.RequestHandler):
    """The main handler."""

    def get(self):
        MyData(key_name="foobar", string="Some test data.").put()
        user = users.get_current_user()
        self.response.out.write('%s' % user)


class RPCHandler(JsonRpcHandler):
    """Handles Remote Procedure Calls.

    No need to define post().
    """

    @ServiceMethod
    def data(self, key_name):
        entity = MyData.get_by_key_name(key_name)
        if entity:
            return entity.json()


app = webapp.WSGIApplication([
    ('/', MainHandler),
    ('/rpc', RPCHandler),
], debug=True)


def main():
    """The main function."""

    webapp.util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
