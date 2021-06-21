#!/usr/bin/python
__author__ = 'joaci'

try:
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    import time
    from pyfase import MicroService
except Exception as e:
    print('require module exception: %s' % e)
    exit(0)


class Fsm(MicroService):
    def __init__(self):
        super(Fsm, self).__init__(self,
                                  sender_endpoint='ipc:///tmp/sender',
                                  receiver_endpoint='ipc:///tmp/receiver')

    def on_connect(self):
        print('### on_connect ###')

    def on_idle(self):
        print('### state: on_idle')
    
    @MicroService.state
    def downloading(self, data):
        print('### state: downloading')
        downloaded_data = {'data': '123456'}
        time.sleep(0.1)
        self.request_state('processing', downloaded_data)

    @MicroService.state
    def processing(self, data):
        print('### state: processing data: %s' % data)
        time.sleep(0.1)
    
    @MicroService.task
    def taskt(self):
        while True:
            time.sleep(8)
            self.request_state('downloading')


Fsm().execute(enable_tasks=True, enable_fsm=True)






