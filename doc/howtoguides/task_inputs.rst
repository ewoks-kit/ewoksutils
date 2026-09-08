Task inputs
===========

Use :func:`ewoksutils.task_utils.task_inputs` to create inputs for a task.

By task identifier
------------------

Select a task by its task identifier and provide its inputs:

.. code-block:: python

    from ewoksutils.task_utils import task_inputs

    inputs = task_inputs(
        task_identifier="ewokscore.tests.test_tasks.SumTask",
        inputs={"a": 10, "b": 20},
    )

.. tip::

    ``task_identifier`` can be a full task identifier or a suffix of one.
    For example, ``task_identifier="SumTask"`` matches
    ``"ewokscore.tests.test_tasks.SumTask"``.

By task ID
----------

For a workflow with explicit task IDs, select the task by its ID:

.. code-block:: python

    inputs = task_inputs(
        id="sum_task",
        inputs={"a": 10, "b": 20},
    )

By task label
-------------

A task can also be selected by its label:

.. code-block:: python

    inputs = task_inputs(
        label="sum",
        inputs={"a": 10, "b": 20},
    )

Multiple tasks
--------------

Inputs for multiple tasks can be combined using their task identifiers:

.. code-block:: python

    inputs = [
        *task_inputs(
            task_identifier="LoadData",
            inputs={"filename": "data.h5"},
        ),
        *task_inputs(
            task_identifier="ProcessData",
            inputs={"threshold": 0.5},
        ),
    ]