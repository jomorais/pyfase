# Finite State Machine

Simple FSM implemented using ``Event()`` from ``threading``. For a lightweight communication inside the same process and to avoid callback hell.

## Declare States

```python
@MicroService.state
def my_state(self, data):
    pass
```

## Call other state at the end

```python
@MicroService.state
def my_state(self, data):
    pass
    # [...] processing
    self.request_state('another_state', data_to_send_to_next_state)
```
If you don't ``request_state()``, the FSM will go back to ``on_default_state``.

## The ``on_default_state`` state

On the ``execute()`` method you can specify how long the process should sleep before calling ``on_default_state`` again. 
Not specifying means it will be called only once per FSM cycle, and not periodically.

```python
def on_default_state(self):
    pass
    # some periodic or cyclic task
```
<br>

## [Home](./index)