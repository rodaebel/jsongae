# -*- coding: utf-8 -*-
#
# Copyright 2010, 2011 Florian Glanzner (fgl), Tobias Rodäbel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Unit tests for the JSON-RPC request handles and helper functions."""
 
from jsongae.json_rpc import *
from google.appengine.ext.webapp import Request, Response
import google.appengine.ext.webapp
import logging
import simplejson
import unittest
import webob

LOG_FORMAT = '%(levelname)-8s %(asctime)s %(filename)s:%(lineno)s] %(message)s'

logging.basicConfig(format=LOG_FORMAT, level=logging.CRITICAL)


class JSONRPCHandlerFunctionalTest(unittest.TestCase):
    """Testcase for the JSON-RPC handler module.

    This testcase tests all the exmaples given in the JSON-RPC 2.0 specs
    in section: 7 Examples.
    """
    class MyTestHandler(JsonRpcHandler):
        """Minimal example rpc handler."""
        @ServiceMethod
        def subtract(self, minuend, subtrahend):
            return minuend - subtrahend
        @ServiceMethod
        def notify_hello(self, num):
            pass
        def noServiceMethod():
            pass
            
    def exec_handler(self, body = None):
        """Used by each test to execute the minimal Testhandler."""
        h = self.MyTestHandler()
        h.request = Request.blank('/test_rpc/')
        h.response = Response()
        h.request.body = body
        h.post()
        return (h.response._Response__status[0], h.response.out.getvalue())

    def test_positional_params(self):
        """Test rpc call with positional parameters."""
        req  = '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}'
        resp = '{"jsonrpc": "2.0", "result": 19, "id": 1}'
        status = 200
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(r_resp, resp)

        req  = '{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}'
        resp = '{"jsonrpc": "2.0", "result": -19, "id": 2}'
        status = 200
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(r_resp, resp)

    def test_named_params(self):
        """Test rpc call with named parameters."""
        req = '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}'
        resp = '{"jsonrpc": "2.0", "result": 19, "id": 3}'
        status = 200
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(r_resp, resp)

        req = '{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}'
        resp = '{"jsonrpc": "2.0", "result": 19, "id": 4}'
        status = 200
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(r_resp, resp)

    def test_notification(self):
        """Test a Notification."""
        req = '{"jsonrpc": "2.0", "method": "update", "params": [1,2,3,4,5]}'
        resp = ''
        status = 204
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(r_resp, resp)

    def test_method_not_found(self):
        """Test rpc call of non-existent method."""
        req = '{"jsonrpc": "2.0", "method": "foobar", "id": "1"}'
        resp = '{"jsonrpc": "2.0", "error": {"code": -32601, "message": "MethodNotFoundError: Method foobar not found"}, "id": "1"}'
        status = 404
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(simplejson.loads(r_resp), simplejson.loads(resp))

    def test_invalid_json(self):
        """Test rpc call with invalid JSON."""
        req = '{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]'
        resp = '{"jsonrpc": "2.0", "error": {"code": -32700, "message": "ParseError: Parse error"}, "id": null}'
        status = 500
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(simplejson.loads(r_resp), simplejson.loads(resp))

    def test_invalid_request(self):
        """Test JSON-RPC with invalid request."""
        req = '{"jsonrpc": "2.0", "method": 1, "params": "bar"}'
        resp = '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "InvalidRequestError: Method must be a string"}, "id": null}'
        status = 400
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(simplejson.loads(r_resp), simplejson.loads(resp))

    def test_invalid_params(self):
        """Test JSON-RPC with invalid params."""
        req = '{"jsonrpc": "2.0", "method": "subtract", "params": 1}'
        resp = '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "InvalidRequestError: \'params\' must be an array or object"}, "id": null}'
        status = 400
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(simplejson.loads(r_resp), simplejson.loads(resp))

    def test_wrong_json_rpc(self):
        """Test JSON-RPC with wrong version."""
        req = '{"jsonrpc": "1.0", "method": 1, "params": "bar"}'
        resp = '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "InvalidRequestError: Server supports JSON-RPC 2.0 only"}, "id": null}'
        status = 400
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(simplejson.loads(r_resp), simplejson.loads(resp))

    def test_missing_method(self):
        """Test JSON-RPC without a method."""
        req = '{"jsonrpc": "2.0", "params": "bar"}'
        resp = '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "InvalidRequestError: No method specified"}, "id": null}'
        status = 400
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(simplejson.loads(r_resp), simplejson.loads(resp))

    def test_invalid_json_batch(self):
        """Test JSON-RPC batch with invalid JSON."""
        req = '[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},{"jsonrpc": "2.0", "method"]'
        resp = '{"jsonrpc": "2.0", "error": {"code": -32700, "message": "ParseError: Parse error"}, "id": null}'
        status = 500
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(simplejson.loads(r_resp), simplejson.loads(resp))

    def test_empty_array(self):
        """Test rpc call with an empty Array."""
        req = '[]'
        resp = '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "InvalidRequestError: Recieved an empty batch message"}, "id": null}'
        status = 400
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(simplejson.loads(r_resp), simplejson.loads(resp))

    def test_invalid_batch(self):
        """Test rpc call with invalid batch."""
        req = '[1,2,3]'
        resp = '''[
                {"jsonrpc": "2.0", "error": {"code": -32600, "message": "InvalidRequestError: Invalid JSON-RPC Message; must be an object"}, "id": null},
                {"jsonrpc": "2.0", "error": {"code": -32600, "message": "InvalidRequestError: Invalid JSON-RPC Message; must be an object"}, "id": null},
                {"jsonrpc": "2.0", "error": {"code": -32600, "message": "InvalidRequestError: Invalid JSON-RPC Message; must be an object"}, "id": null}
                ]'''
        status = 200
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(simplejson.loads(r_resp), simplejson.loads(resp))

    def test_batch(self):
        """Test rpc call with batch."""
        req = '''[{"foo": "boo"},
                  {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
                  {"jsonrpc": "2.0", "method": "subtract", "params": [42,23], "id": "2"},
                  {"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"}
                 ]'''

        resp = '''[{"jsonrpc": "2.0", "error": {"code": -32600, "message": "InvalidRequestError: Invalid members in request object"}, "id": null},
                   {"jsonrpc": "2.0", "result": 19, "id": "2"},
                   {"jsonrpc": "2.0", "id": "5", "error": {"message": "MethodNotFoundError: Method foo.get not found", "code": -32601}}
                  ]'''

        status = 200
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(simplejson.loads(r_resp), simplejson.loads(resp))

    def test_notification_batch(self):
        """Test rpc call Batch (all notifications)."""
        req = '''[{"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
                  {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]}
                 ]'''
        resp = ''
        status = 204
        r_status, r_resp = self.exec_handler(req)
        self.assertEqual(r_status, status)
        self.assertEqual(r_resp, resp)

class JsonRpcHandlerTestCase(unittest.TestCase):
    """Some additional test for the json_rpc handler module."""
    class MyTestHandler(JsonRpcHandler):
        @ServiceMethod
        def myMethod(self, a, b):
            return a + b
        def noServiceMethod():
            pass
        @ServiceMethod
        def brokenMethod(self):
            raise ValueError
        @ServiceMethod
        def noParamsMethod(self):
            return 'nice'
        @ServiceMethod
        def variableParamsMethod(self, *args):
            pass

    def setUp(self):
        """Set up the test with a simple TestHandler."""
        h = self.MyTestHandler()
        h.request = Request.blank('/rpc/')
        h.response = Response()
        self.handler = h
    
    def getHandler(self):
        self.handler.response.clear()
        return self.handler

    def testGetResponses(self):
        # Regular processed message
        m1 = JsonRpcMessage()
        m1.result = 'Result'
        
        #Msg with an error
        m2 = JsonRpcMessage()
        m2.error = ServerError('Something went wrong')
        
        #notification
        m3 = JsonRpcMessage()
        m3.result = 'Notification result'
        m3.notification = True
        
        msgs = [m1, m2, m3]
        
        h = self.getHandler()
        exspect = [(200, {'jsonrpc': '2.0', 'result': 'Result', 'id': None}),
            (500, {'jsonrpc': '2.0', 'id': None, 'error': 
                {'message': 'ServerError: Something went wrong',
                 'code': -32000}})]

        self.assertEqual(h.get_responses(msgs), exspect)

    def testParams(self):
        """Test Wrong parameters for the given 'method'."""
        h = self.getHandler()
        rq  = '{"jsonrpc":"2.0", "method":"myMethod", "params":["A","B", "BAD"], "id":"1"}'
        
        messages, dummy = h.parse_body(rq)
        msg = messages[0]
        h.handle_message(msg)
        self.assertTrue(isinstance(msg.error, InvalidParamsError))

    def testNoParams(self):
        """Test ommiting member 'params' in json message."""
        h = self.getHandler()
        rq  = '''{"jsonrpc":"2.0", "method":"noParamsMethod", "id":"1"}'''
        messages, dummy = h.parse_body(rq)
        msg = messages[0]
        h.handle_message(msg)
        self.assertEqual(msg.result, 'nice')

    def testWronNumberOfParams(self):
        """Test invalid number of params."""
        h = self.getHandler()
        rq  = '''{"jsonrpc":"2.0", "method":"myMethod", "id":"1"}'''
        messages, dummy = h.parse_body(rq)
        msg = messages[0]
        h.handle_message(msg)
        self.assertEqual(msg.result, None)

    def testVariableParams(self):
        """Service method definitions must not have variable parameters."""
        h = self.getHandler()
        rq  = '''{"jsonrpc":"2.0", "method":"variableParamsMethod", "params":["A","B"], "id":"1"}'''
        messages, dummy = h.parse_body(rq)
        msg = messages[0]
        h.handle_message(msg)
        self.assertTrue(isinstance(msg.error, InvalidParamsError))

    def testInvalidParams(self):
        """Service methods expect the complete set of parameters."""
        h = self.getHandler()
        rq  = '''{"jsonrpc":"2.0", "method":"myMethod", "params":{"foo": 1}, "id":"1"}'''
        messages, dummy = h.parse_body(rq)
        msg = messages[0]
        h.handle_message(msg)
        self.assertTrue(isinstance(msg.error, InvalidParamsError))

    def testBrokenMethod(self):
        """Test a method that raises an error."""
        h = self.getHandler()
        rq  = '''{"jsonrpc":"2.0", "method":"brokenMethod", "id":"1"}'''
        messages, dummy = h.parse_body(rq)
        msg = messages[0]
        h.handle_message(msg)
        self.assertEqual(str(msg.error), "Error executing service method")
        self.assertEqual(
            repr(msg.error), 'InternalError("Error executing service method")')
        self.assertTrue(isinstance(msg.error, InternalError))
