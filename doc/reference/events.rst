Ewoks workflow event schema
===========================

Events are emitted when executing a workflow. They are dictionaries with the following fields:

.. py:data:: host_name
    :type: str

    Host name where the workflow is running.

.. py:data:: process_id
    :type: int

    Process id of the workflow execution.

.. py:data:: user_name
    :type: str

    Name of the user under which the workflow is running.

.. py:data:: job_id
    :type: int

    Job id. Random uuid by default.

.. py:data:: engine
    :type: str | None

    Execution engine. 
    
    ``None`` unless an execution engine is used.

.. py:data:: context
    :type: str
    :value: "job" | "workflow" | "node"

    Event context. Can only take the values above.

.. py:data:: node_id
    :type: str | None
    
    Id of the node to which the event belongs. 
    
    Only defined if ``context == "node"``.
    
.. py:data:: task_id
    :type: str | None

    Identifier of the node task.  
    
    Only defined if ``context == "node"``.

.. py:data:: type
    :type: str
    :value: "start" | "end" | "progress"

    Event type. Can only take the values above. 
    
    Certain event fields are ``None`` unless the type has a specific value (see below).

.. py:data:: time
    :type: str

    Time of event creation. The time is given in ISO 8601 format in local timezone.

.. py:data:: error
    :type: bool | None

    Flag that tells if an error occurred. 
    
    Only defined if ``type == "end"``.

.. py:data:: error_message
    :type: str | None

    Message of the error if one occurred. 
    
    Only defined if ``type == "end"``.

.. py:data:: error_traceback
    :type: str | None

    Traceback of the error if one occurred. 
    
    Only defined if ``type == "end"``.

.. py:data:: progress
    :type: int | None

    Number between 0 and 100 representing the progress if provided by the task. 
    
    Can only be defined if ``type == "progress"``.

.. py:data:: task_uri
    :type: str | None

    URI where the task outputs are stored (one URI for all task outputs).
    
    Only defined if persistence is enabled.

.. py:data:: input_uris
    :type: list[dict] | None

    URIs where inputs are stored (one URI per input variable). 
    
    Only defined if ``event == "start"``  and persistence is enabled.

.. py:data:: output_uris
    :type: list[dict] | None

    URIs where the outputs are stored (one URI per output variable). 
    
    Only defined if ``event == "start"`` and persistence is enabled.
