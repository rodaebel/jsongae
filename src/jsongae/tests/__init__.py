"""Testing jsongae."""

import app
import nose.tools
import os
import webtest


app = webtest.TestApp(app.app)


def setup_func():
    """Set up test fixtures."""

    os.environ['USER_EMAIL'] = 'test@example.com'


@nose.tools.with_setup(setup_func)
def test_index():
    """Testing whether our application responds"""

    response = app.get('/')
    nose.tools.assert_equal(response.status, '200 OK')
