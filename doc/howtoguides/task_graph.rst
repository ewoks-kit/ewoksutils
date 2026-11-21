Workflow with one task
======================

Use :func:`ewoksutils.task_utils.task_graph` to create a workflow that executes one task:

.. code-block:: python

    from ewoksutils.task_utils import task_graph
    from ewoksutils.task_utils import task_inputs

    graph = task_graph("ewokscore.tests.examples.tasks.sumtask.SumTask")
    inputs = task_inputs(
        task_identifier="ewokscore.tests.examples.tasks.sumtask.SumTask",
        inputs={"a": 10, "b": 20},
    )

The task type is guessed from the task identifier.
Use ``task_type`` to set it:

.. code-block:: python

    graph = task_graph("mymodule.MyFunction", task_type="method")

On the command line, use ``--task``:

.. code-block:: bash

    ewoks execute ewokscore.tests.examples.tasks.sumtask.SumTask --task -pa a=10 -pa b=20
