# -*- coding: utf-8 -*-
"""
    pyfase
    Is a Fast-Asynchronous-microService-Environment based on ZeroMQ.
    :copyright: (c) 2016 by Joaci Morais.
"""

__author__ = 'Joaci Morais'

try:
    import os
    import sys
    import signal
    import inspect
    import zmq
    import time
    from threading import Thread, Event
    from json import loads, dumps
except Exception as requirement_exception:
    print('requirements exception: %s' % requirement_exception)
    exit(0)


class PyFaseException(Exception):
    pass


def isSerializable(d):
    try:
        x = dumps(d)
        return True
    except (TypeError, OverflowError):
        return False


class Fase(object):
    __slots__ = ('ctx', 'receiver', 'sender')

    def __init__(self, sender_endpoint, receiver_endpoint):
        self.ctx = zmq.Context()
        self.receiver = self.ctx.socket(zmq.PULL)
        self.receiver.bind(receiver_endpoint)
        self.sender = self.ctx.socket(zmq.PUB)
        self.sender.bind(sender_endpoint)

    def execute(self):
        try:
            while True:
                self.sender.send_string(self.receiver.recv_string(), zmq.NOBLOCK)
        except Exception and KeyboardInterrupt:
            os.kill(os.getpid(), signal.SIGKILL)


class MicroService(object):
    __slots__ = ('name', 'log', 'actions', 'tasks', 'ctx', 'sender', 'receiver', 'o_pkg', 'action_context',
                 'fsm_states', 'fsm_current_state', 'fsm_data', 'fsm_event', 'fsm_on_default_state_time')

    def __init__(self, service, sender_endpoint, receiver_endpoint):
        if inspect.isclass(type(service)):
            self.name = service.__class__.__name__
            self.actions = {}
            self.tasks = {}
            self.fsm_states = {}
            self.fsm_current_state = 'on_default_state'
            self.fsm_data = None
            self.fsm_event = Event()
            self.fsm_on_default_state_time = None
            self.ctx = zmq.Context()
            self.sender = self.ctx.socket(zmq.PUSH)
            self.sender.connect(receiver_endpoint)
            self.receiver = self.ctx.socket(zmq.SUB)
            self.receiver.connect(sender_endpoint)
            self.o_pkg = {}
            self.action_context = False
            """ filter <r> packages: Notify when a new Micro-Service is available """
            self.receiver.setsockopt_string(zmq.SUBSCRIBE, u'<r>:')
            """ filter <b> packages: Broadcast packages  """
            self.receiver.setsockopt_string(zmq.SUBSCRIBE, u'<b>:')
            """ filter response packages: Notify when receive an response from an action previous requested """
            self.receiver.setsockopt_string(zmq.SUBSCRIBE, u'%s:' % self.name)
            for name, func in service.__class__.__dict__.items():
                if hasattr(func, '__call__'):  # IS A FUNCTION?
                    if '_action_wrapper_' in func.__name__:  # IS AN ACTION?
                        self.actions[name] = func
                        """ filter only actions defined on this Micro-Service """
                        self.receiver.setsockopt_string(zmq.SUBSCRIBE, u'%s:' % name)
                    elif '_task_wrapper_' in func.__name__:  # IS A TASK?
                        self.tasks[name] = func
                    elif '_state_wrapper_' in func.__name__:  # IS A STATE?
                        if name == 'on_default_state':
                            raise PyFaseException("You can't, create a state named 'on_default_state'! use builtin one.")
                        self.fsm_states[name] = func
        else:
            raise PyFaseException('MicroService %s must be a class' % service)

    @staticmethod
    def action(function):
        def _action_wrapper_(*args, **kwargs):
            return function(*args, **kwargs)
        return _action_wrapper_

    @staticmethod
    def task(function):
        def _task_wrapper_(*args, **kwargs):
            return function(*args, **kwargs)
        return _task_wrapper_

    @staticmethod
    def state(function):
        def _state_wrapper_(*args, **kwargs):
            return function(*args, **kwargs)
        return _state_wrapper_

    @staticmethod
    def exit():
        os.kill(os.getpid(), signal.SIGKILL)

    def on_connect(self):
        pass

    def on_broadcast(self, service, data):
        pass

    def on_new_service(self, service, actions):
        pass

    def on_response(self, service, data):
        pass

    def on_default_state(self):
        pass

    def request_state(self, next_state, data=None):
        if type(next_state) != str:
            raise PyFaseException("request_state:: next_state must be a 'str' with the name of the state! not a %s" % 
                                  type(next_state))
        elif next_state == 'on_default_state':
            raise PyFaseException("request_state:: you can't request on_default_state, "
                                  "it runs automatically when there isn't pending states")
        elif next_state in self.fsm_states:
            self.fsm_data = data
            self.fsm_current_state = next_state
            self.fsm_event.set()
        else:
            raise PyFaseException('request_state:: state [ %s ] not found' % next_state)

    def set_new_default_state_time(self, on_default_state_time):
        if type(on_default_state_time) != float and type(on_default_state_time) != int:
            raise PyFaseException("please, assign on_default_state_time only with 'int' or 'float'")
        if on_default_state_time > 0:
            if type(on_default_state_time) is int or type(on_default_state_time) is float:
                self.fsm_on_default_state_time = on_default_state_time
                self.fsm_current_state = 'on_default_state'
        else:
            raise PyFaseException("only greater the zeros values are allowed")

    def start_task(self, task_name, data):
        if type(task_name) != str:
            raise PyFaseException("start_task:: task_name must be a 'str' with the name of the task! not a %s" %
                                  type(task_name))
        if task_name in self.tasks:
            Thread(target=self.tasks[task_name], name=task_name, args=data).start()
        else:
            raise PyFaseException("start_task:: task %s not found" % task_name)

    def send_broadcast(self, data):
        if isSerializable(data) is False:
            raise PyFaseException("request_action:: data must be a serializable JSON content, not a %s" %
                                  type(data))
        self.sender.send_string('<b>:%s' % dumps({'s': self.name, 'd': data}), zmq.NOBLOCK)

    def request_action(self, action, data):
        if type(action) != str:
            raise PyFaseException("request_action:: action must be a 'str' with the name of the action! not a %s" %
                                  type(action))
        if isSerializable(data) is False:
            raise PyFaseException("request_action:: data must be a serializable JSON content, not a %s" %
                                  type(data))
        self.sender.send_string('%s:%s' % (action, dumps({'s': self.name, 'd': data})), zmq.NOBLOCK)

    def response(self, data):
        if isSerializable(data) is False:
            raise PyFaseException("request_action:: data must be a serializable JSON content, not a %s" %
                                  type(data))
        if self.action_context:
            self.sender.send_string('%s:%s' % (self.o_pkg['s'], dumps({'s': self.name, 'd': data})), zmq.NOBLOCK)

    def _fsm(self):
        try:
            self.fsm_event.clear()
            while True:
                if self.fsm_event.wait(self.fsm_on_default_state_time):
                    if self.fsm_current_state in self.fsm_states:
                        self.fsm_event.clear()
                        self.fsm_states[self.fsm_current_state](self, self.fsm_data)
                        if self.fsm_event.is_set() is False:
                            self.fsm_current_state = 'on_default_state'
                            self.on_default_state()
                else:
                    self.on_default_state()
        except Exception as fsm_exception:
            print('fsm exception: %s' % fsm_exception)
            os.kill(os.getpid(), signal.SIGKILL)

    def execute(self, enable_tasks=None, enable_fsm=None, on_default_state_time=None):
        try:
            if enable_tasks:
                for name, task in self.tasks.items():
                    Thread(target=task, name=name, args=(self,)).start()
            if enable_fsm:
                if on_default_state_time:
                    if type(on_default_state_time) is int or type(on_default_state_time) is float:
                        self.fsm_on_default_state_time = on_default_state_time
                    else:
                        raise PyFaseException("please, assign on_default_state_time only with 'int' or 'float'")
                Thread(target=self._fsm, name='fsm').start()
            self.sender.send_string('<r>:%s' % dumps({'s': self.name,
                                                      'a': [action for action in self.actions]}), zmq.NOBLOCK)
            while True:
                pkg = self.receiver.recv_string()
                if '<r>:' in pkg:  # IS A REGISTER PACKAGE!
                    self.o_pkg = loads(pkg[4:])
                    service = self.o_pkg['s']
                    if self.name == service:
                        self.on_connect()
                    else:
                        self.on_new_service(service, self.o_pkg['a'])
                elif '<b>:' in pkg:  # IS A BROADCAST PACKAGE!
                    self.o_pkg = loads(pkg[4:])
                    service = self.o_pkg['s']
                    if self.name != service:
                        self.on_broadcast(service, self.o_pkg['d'])
                elif '%s:' % self.name in pkg:  # IS A RESPONSE PACKAGE!
                    pos = pkg.find(':')
                    self.o_pkg = loads(pkg[pos + 1:])
                    self.on_response(self.o_pkg['s'], self.o_pkg['d'])
                else:  # IS AN ACTION PACKAGE!
                    pos = pkg.find(':')
                    self.o_pkg = loads(pkg[pos + 1:])
                    self.action_context = True
                    self.actions[pkg[:pos]](self, self.o_pkg['s'], self.o_pkg['d'])
                    self.action_context = False
        except Exception and KeyboardInterrupt as execute_exception:
            print('execute exception: %s' % execute_exception)
            os.kill(os.getpid(), signal.SIGKILL)


