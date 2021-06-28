import unittest
import inspect
import zmq
import threading
from pyfase import MicroService, Fase, PyFaseException
import time


class MyMicroService(MicroService):
    def __init__(self, sender, receiver):
        super(MyMicroService, self).__init__(self,
                                             sender_endpoint=sender,
                                             receiver_endpoint=receiver)
        self.stop_task = threading.Event()

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
        while not self.stop_task.isSet():
            time.sleep(0.01)

    @MicroService.task
    def task_2(self):
        pass

class PyfaseInstanceTestCase(unittest.TestCase):
    def setUp(self):
        common_sender = 'ipc:///tmp/sender'
        common_receiver = 'ipc:///tmp/receiver'
        self.myms = MyMicroService(common_sender, common_receiver)
        self.fase = Fase(sender_endpoint=common_sender, receiver_endpoint=common_receiver)

    def tearDown(self):
        del self.myms
        del self.fase

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
        def running_threads():
            return [thread.name for thread in threading.enumerate()]
        
        with self.assertRaises(PyFaseException):
            self.myms.start_task('non_existent_task', {})
        self.assertFalse('task_1' in running_threads())
        self.myms.start_task('task_1', [self.myms])
        self.assertTrue('task_1' in running_threads())
        self.myms.stop_task.set()
        time_init = time.time()
        while 'task_1' in running_threads() and time.time() - time_init < 3:
            time.sleep(0.01)
        self.assertFalse('task_1' in running_threads())
    
    def test_send_broadcast(self):
        pass

    def test_request_action(self):
        pass

    def test_response(self):
        pass
    

if __name__ == '__main__':
    unittest.main()
