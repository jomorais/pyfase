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

    def test_microservice_name(self):
        self.assertEqual(self.myms.name, 'MyMicroService')

    def test_instance_actions(self):
        self.assertEqual(type(self.myms.actions), dict)
        self.assertEqual('action_1' in self.myms.actions, True)
        self.assertEqual('action_2' in self.myms.actions, True)

    def test_instance_tasks(self):
        self.assertEqual(type(self.myms.tasks), dict)
        self.assertEqual('task_1' in self.myms.tasks, True)
        self.assertEqual('task_2' in self.myms.tasks, True)

    def test_instance_fsm_states(self):
        self.assertEqual(type(self.myms.fsm_states), dict)
        self.assertEqual('state_1' in self.myms.fsm_states, True)
        self.assertEqual('state_2' in self.myms.fsm_states, True)

    def test_instance_fsm_properties(self):
        self.assertEqual(self.myms.fsm_current_state, 'on_default_state')
        self.assertEqual(self.myms.fsm_data, None)
        self.assertEqual(type(self.myms.fsm_event), threading.Event)
        self.assertEqual(self.myms.fsm_on_default_state_time, None)
        self.myms.set_new_default_state_time(0.25)
        self.assertEqual(self.myms.fsm_on_default_state_time, 0.25)
        self.myms.set_new_default_state_time(1)
        self.assertEqual(self.myms.fsm_on_default_state_time, 1)
        with self.assertRaises(PyFaseException):
            self.myms.set_new_default_state_time(0)
        with self.assertRaises(PyFaseException):
            self.myms.set_new_default_state_time(-1)

    def test_instance_zmq_properties(self):
        self.assertEqual(type(self.myms.ctx), zmq.Context)
        self.assertEqual(type(self.myms.sender), zmq.sugar.socket.Socket)
        self.assertEqual(type(self.myms.receiver), zmq.sugar.socket.Socket)

    def test_instance_pyfase_properties(self):
        self.assertEqual(type(self.myms.o_pkg), dict)
        self.assertEqual(self.myms.o_pkg, {})
    
    def test_instance_fase_zmq_properties(self):
        self.assertEqual(type(self.fase.ctx), zmq.Context)
        self.assertEqual(type(self.fase.sender), zmq.sugar.socket.Socket)
        self.assertEqual(type(self.fase.receiver), zmq.sugar.socket.Socket)


if __name__ == '__main__':
    unittest.main()
