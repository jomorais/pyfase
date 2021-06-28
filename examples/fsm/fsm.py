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

    def on_default_state(self):
        print('### state: on_default_state')
    
    @MicroService.state
    def downloading(self, data):
        print('### state: downloading: %s' % data)
        downloaded_data = {'data': '123456'}
        self.request_state('processing', downloaded_data)

    @MicroService.state
    def processing(self, data):
        print('### state: processing data: %s' % data)
        processed_data = '%s%s' % (data['data'], '7')
        self.request_state('sending', processed_data)

    @MicroService.state
    def sending(self, data):
        print('### state: sending data: %s' % data)

    @MicroService.task
    def taskt(self):
        while True:
            time.sleep(8)
            self.request_state(next_state='downloading', data='url.com/file.json')


Fsm().execute(enable_tasks=True, enable_fsm=True, on_default_state_time=1)






