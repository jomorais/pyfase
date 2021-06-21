# execute()

Parameters passed when calling ``execute()`` method inherited from pyfase.

## - enable_tasks (default: None)
If your Class has a ``MicroService.task`` within it, you should pass ``enable_tasks=True`` here to execute them.
Not passing anything means your tasks will not be executed.

## - enable_fsm (default: None)
If you have declared ``MicroService.state``s, passing ``True`` here will execute your FSM starting from the ``default`` state.
More information about FSM's in the next section.

## - on_default_state_time (default: None)
Delay (in seconds) between executions of the ``default`` state of your FSM. 
Passing nothing means your ``default`` state will only execute once and wait for ``request_state()`` to trigger subsequent states. 

## [Next: Finite State Machine](./fsm)
## [Home](./index)