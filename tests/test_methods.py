import unittest
import inspect
import zmq
import threading
from pyfase import MicroService, Fase, PyFaseException


class MyMicroService(MicroService):
    def __init__(self):
        super(MyMicroService, self).__init__(self,
                                             sender_endpoint='ipc:///tmp/sender',
                                             receiver_endpoint='ipc:///tmp/receiver')

    @MicroService.action
    def action_1(self, service, data):
        pass

    @MicroService.action
    def action_2(self, service, data):
        pass

    @MicroService.state
    def state_1(self, service, data):
        pass

    @MicroService.state
    def state_2(self, service, data):
        pass

    @MicroService.task
    def task_1(self):
        pass

    @MicroService.task
    def task_2(self):
        pass


class PyfaseInstanceTestCase(unittest.TestCase):

    def setUp(self):
        self.myms = MyMicroService()
        self.fase = Fase(sender_endpoint='ipc:///tmp/sender', receiver_endpoint='ipc:///tmp/receiver')

    def tearDown(self):
        pass

    def test_request_state(self):
        self.assertEqual(self.myms.fsm_data, None)
        self.assertEqual(self.myms.fsm_current_state, 'on_default_state')
        self.assertEqual(self.myms.fsm_event.is_set(), False)
        
        with self.assertRaises(PyFaseException):
            self.myms.request_state('on_default_state')
            self.assertEqual(self.myms.fsm_data, None)
            self.assertEqual(self.myms.fsm_event.is_set(), False)
        
        with self.assertRaises(PyFaseException):
            self.myms.request_state('state_3', {'data': 'any data as a dict'})
            self.assertEqual(self.myms.fsm_data, None)
            self.assertEqual(self.myms.fsm_event.is_set(), False)

        self.myms.request_state('state_1')
        self.assertEqual(self.myms.fsm_data, None)
        self.assertEqual(self.myms.fsm_current_state, 'state_1')
        self.assertEqual(self.myms.fsm_event.is_set(), True)
        
        self.myms.request_state('state_2', 'a string data data')
        self.assertEqual(self.myms.fsm_data, 'a string data data')
        self.assertEqual(self.myms.fsm_current_state, 'state_2')
        self.assertEqual(self.myms.fsm_event.is_set(), True)
        
        self.myms.request_state('state_1', {'data': 'any data as a dict'})
        self.assertEqual(self.myms.fsm_data, {'data': 'any data as a dict'})
        self.assertEqual(self.myms.fsm_current_state, 'state_1')
        self.assertEqual(self.myms.fsm_event.is_set(), True)
    
    def test_set_new_default_state_time(self):
        self.assertEqual(self.myms.fsm_on_default_state_time, None)
        self.myms.set_new_default_state_time(1)
        self.assertEqual(self.myms.fsm_on_default_state_time, 1)
        self.myms.set_new_default_state_time(0.1)
        self.assertEqual(self.myms.fsm_on_default_state_time, 0.1)
        self.myms.set_new_default_state_time(5544778855.25)
        self.assertEqual(self.myms.fsm_on_default_state_time, 5544778855.25)
        with self.assertRaises(PyFaseException):
            self.myms.set_new_default_state_time(-1)
        with self.assertRaises(PyFaseException):
            self.myms.set_new_default_state_time(0)
        
    def test_start_task(self):
        pass
    
    def test_send_broadcast(self):
        pass

    def test_request_action(self):
        pass

    def test_response(self):
        pass
    

if __name__ == '__main__':
    unittest.main()
