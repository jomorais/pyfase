# Decorators

## - @MicroService.action
Used before functions that you want to make available to other processes.
```python
@MicroService.action
def my_function(self, service, data):
    # data: contains any parameters passed by the caller
    pass # your logic here
```
<br>
## - @MicroService.task
Used in functions that will run forever. Behind the curtains, this function is stantiated with the ``threading`` package, and you must use the following pattern for a endless execution:

```python
@MicroService.task
def my_task(self):
    while True:
        pass # your logic here
        time.sleep(sometime) # or else your processor is going to fry up
```
<br>
## - @MicroService.state
Used in Finite State Machines. Use before a function that is equivalent to state.

```python
@MicroService.state
def my_state(self, data):
    pass # your logic here
    self.request_state('another_state', data_to_send)
    # if your don't request a state at the end, your FSM will go to on_default_state state by default
```

## [Next: execute()](./calling)
## [Home](./index)
