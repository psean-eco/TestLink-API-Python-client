#! /usr/bin/python
# -*- coding: UTF-8 -*-

#  Copyright 2013 Luiko Czub, TestLink-API-Python-client developers
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# ------------------------------------------------------------------------

# this test works WITHOUT an online TestLink Server
# no calls are send to a TestLink Server

import unittest
from testlink import TestlinkAPIGeneric, TestLinkHelper
from testlink import testlinkerrors

# scenario_a includes response from a testlink 1.9.8 server
SCENARIO_A = {'repeat' : 'You said: One World',
              'sayHello' : 'Hey Folks!',
              'doesUserExist' : {
                'Big Bird' :  [{'message': '(doesUserExist) - Cannot Find User Login provided (Big Bird).', 
                                'code': 10000}],
                'admin' : True }
              }

class DummyAPIGeneric(TestlinkAPIGeneric):
    """ Dummy for Simulation TestLinkAPIGeneric. 
    Overrides 
    - _callServer() Method to return test scenarios
    - extend positional_arg_names for  method 'DummyMethod'
    """

    __slots__ = ['scenario_data', 'callArgs']
  
    def __init__(self, server_url, devKey):
        super(DummyAPIGeneric, self).__init__(server_url, devKey)
        self._positionalArgNames['DummyMethod'] = ['Uno', 'due', 'tre']
        self.scenario_data = {}
        self.callArgs = None


    def loadScenario(self, a_scenario):
        self.scenario_data = a_scenario

    def _callServer(self, methodAPI, argsAPI=None):
        self.callArgs = argsAPI
        response = None
        if methodAPI in ['DummyMethod']:
            response = [argsAPI]
        else:
            data = self.scenario_data[methodAPI]
            if methodAPI in ['doesUserExist']:
                response = data[argsAPI['user']]
            else:
                response = data
        return response
    
    
class TestLinkAPIGenericOfflineTestCase(unittest.TestCase):
    """ TestCases for TestlinkAPIGeneric - does not interacts with a TestLink Server.
    works with DummyAPIGeneric which returns special test data
    """

    def setUp(self):
        self.api = TestLinkHelper().connect(DummyAPIGeneric)

#    def tearDown(self):
#        pass


    def test_convertPositionalArgs(self):
        response = self.api._convertPostionalArgs('DummyMethod',  [1,2,3])
        self.assertEqual({'Uno' : 1, 'due' :2, 'tre' : 3}, response)
        
    def test__convertPositionalArgs_missingConf(self):
        client = self.api
        def a_func(a_api): a_api._convertPostionalArgs('NoConfigMethod',  [1,2])
        self.assertRaises(testlinkerrors.TLArgError, a_func, client)
        
    def test__convertPositionalArgs_lessValues(self):
        client = self.api
        def a_func(a_api): a_api._convertPostionalArgs('DummyMethod',  [1,2])
        self.assertRaises(testlinkerrors.TLArgError, a_func, client)
        
    def test__convertPositionalArgs_moreValues(self):
        client = self.api
        def a_func(a_api): a_api._convertPostionalArgs('DummyMethod',  [1,2,3,4])
        self.assertRaises(testlinkerrors.TLArgError, a_func, client)

    def test_callServerWithPosArgs_pos(self):
        self.api.callServerWithPosArgs('DummyMethod',  1,2,3)
        self.assertEqual({'Uno' : 1, 'due' :2, 'tre' : 3}, self.api.callArgs)

    def test_callServerWithPosArgs_pos_opt(self):
        self.api.callServerWithPosArgs('DummyMethod',  1,2,3, quad=4)
        self.assertEqual({'Uno' : 1, 'due' :2, 'tre' : 3, 'quad' : 4}, self.api.callArgs)

    def test_callServerWithPosArgs_opt(self):
        self.api.callServerWithPosArgs('DummyMethod',  quad=4)
        self.assertEqual({'quad' : 4}, self.api.callArgs)

    def test_callServerWithPosArgs_none(self):
        self.api.callServerWithPosArgs('DummyMethod')
        self.assertEqual({}, self.api.callArgs)
        
    def test_checkResponse_emptyResponse(self):
        client = self.api
        def a_func(a_api, response): 
            a_api._checkResponse(response, 'DummyMethod',  
                                 {'Uno' : 1, 'due' :2, 'tre' : 3})
        self.assertRaises(testlinkerrors.TLResponseError, a_func, client, '')
        self.assertRaises(testlinkerrors.TLResponseError, a_func, client, [])
        
    def test_checkResponse_errorResponse(self):
        client = self.api
        responseA = [{'message': '(reportTCResult) - TC ID 709 does not exist!', 
                      'code': 5000}]
        def a_func(a_api, response): 
            a_api._checkResponse(response, 'DummyMethod',  
                                 {'Uno' : 1, 'due' :2, 'tre' : 3})
        self.assertRaises(testlinkerrors.TLResponseError, a_func, client, 
                          responseA)

    def test_checkResponse_okResponse(self):
        self.api._checkResponse(
                        [{'message': 'all fine, cause no key with name code'}],
                         'DummyMethod', {'Uno' : 1, 'due' :2, 'tre' : 3})
        self.api._checkResponse(
                        'some API Call juts returns one string without codes',
                         'DummyMethod', {'Uno' : 1, 'due' :2, 'tre' : 3})
        
    def test_checkResponse_booleanResponse(self):
        response = True
        self.api._checkResponse(response, 'DummyMethod', 
                                {'Uno' : 1, 'due' :2, 'tre' : 3})
        
    def test_checkResponse_dictionaryResponse(self):
        response = {'note' : 'uploadAttachment Calls return {..} and not [{..}]'}
        self.api._checkResponse(response, 'DummyMethod', 
                                {'Uno' : 1, 'due' :2, 'tre' : 3})
        
    def test_ping(self):
        self.api.loadScenario(SCENARIO_A)
        response = self.api.ping()
        self.assertEqual('Hey Folks!', response)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()