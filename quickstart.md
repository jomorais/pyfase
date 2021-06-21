# Quickstart

### Declaring a pyfase compatible class

```python
from pyfase import MicroService

class Class_1(MicroService):
    def __init__(self):
        super(Class_1, self).__init__(self, 
                                    sender_endpoint='ipc:///tmp/sender', 
                                    receiver_endpoint='ipc:///tmp/receiver')

    @MicroService.action
    def do_something_amazing(self, service, data):
        print('doing something amazing!')
        # [...]
        self.request_action('handle_amazingness', {'amazing': '10/10'})

Class_1().execute()
```

Here ``Class_1`` inherits from MicroService, your window of comunication with other processes. That first line in ``__init__`` is what communicates to ``core.py`` that your process exists and interfaces it with other ones.

But it alone won't do any good, it still needs to have it's ``@MicroService.action`` called from another process:

```python
from pyfase import MicroService
from time import sleep

class Class_2(MicroService):
    def __init__(self):
        super(Class_2, self).__init__(self, 
                                    sender_endpoint='ipc:///tmp/sender', 
                                    receiver_endpoint='ipc:///tmp/receiver')

    @MicroService.action
    def handle_amazingness(self, service, data):
        print('amazing response: {}'.format(data['amazing']))

    @MicroService.task
    def request_amazingness():
        while True:
            sleep(10)
            message = dict(how_much_amazing='really amazing')
            self.request_action('do_something_amazing', message)

Class_2().execute(enable_tasks=True)
```

Having done that, all that is left is to run ``core.py``, the script that acts as the broker for those processes.

Once all three processes are running, every 10 seconds ``Class_2`` will request a action called ``do_something_amazing`` and send ``message`` as data parameter. 
Every process that is connected to this broker will listen to this request, and if it has a function by this name and that function is decorated by ``@MicroService.action``, it will then execute the action.

Head over to the [examples folder](https://github.com/jomorais/pyfase/tree/master/examples) if you want to see more.

### Known Limitations

- The ``data`` parameter for sending and receiving messages has to be JSON serializable
- For Windows users the ``ipc`` isn't available. This can be solved by replacing those two parameters in ``__init__`` method, as well as on the ``core.py``:
```python
sender_endpoint='tcp://localhost:8001/'
receiver_endpoint='tcp://localhost:8002/'
```
Or any other ``ip:port`` available for you.

## [Next: Decorators](./decorators)
## [Home](./index)