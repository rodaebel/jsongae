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
def test_rpc_call():
    """Testing JSON/RPC"""

    response = app.post(
        '/rpc',
        '{"jsonrpc": "2.0", "id": 42, "method": "test", "params": ["foobar"]}'
    )
    nose.tools.assert_equal(response.status, '200 OK')
    nose.tools.assert_equal(
        response.body, '{"jsonrpc": "2.0", "result": "foobar", "id": 42}')
