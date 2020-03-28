API
===

Trio CDP replicates the entire API of PyCDP. For example, PyCDP has a ``cdp.dom`` module,
while in Trio CDP, we have ``trio_cdp.dom``. The Trio CDP version has all of the same data
types, commands, and events as the PyCDP version. 

The only difference between the two libraries is that the Trio CDP commands are ``async
def`` functions that can be called from Trio, whereas the PyCDP commands are generators
that must be executed in a special way. This document explains both flavors and how to
use them.

You should consult the `PyCDP documentation
<https://py-cdp.readthedocs.io/en/latest/api.html>`_ for a complete reference of the
data types, commands, and events that are available.

Simplified API
--------------

.. highlight: python

The simplified API allows you to await CDP commands directly. For example, to run a CSS
query to get a blockquote element, the code is:

.. code::

    from trio_cdp import dom
    
    ...other code...
 
    node_id = await dom.query(root, 'blockquote')

As you can see in `the PyCDP documentation
<https://py-cdp.readthedocs.io/en/latest/api/dom.html#cdp.dom.query_selector>`_, the
command takes a ``NodeId`` as its first argument and a string as its second argument.
The arguments in Trio CDP are always the same as in PyCDP.

The return types in Trio CDP are different from PyCDP, however. The PyCDP command is a
generator, where as the Trio CDP command is an ``async def``. The PyCDP command
signature shows ``Generator[Dict[str, Any], Dict[str, Any], NodeId]]``. The generator
contains 3 parts. The first two parts are always the same: ``Dict[str, Any]``. The third
part indicates the real return type, and that is the type that the Trio CDP command will
return. In this case, it returns a ``NodeId``.

If you have code completion in your Python IDE, it will help you see what the return
type is for each Trio CDP command.

.. note::

    In order for this calling style to work, you must be inside a "session
    context", i.e. your code must be nested in (or called from inside of) an ``async with
    conn.open_session()`` block. If you try calling this from outside of a session context,
    you will get an exception.

Low-level API
-------------

The low-level API is a bit more verbose, but you may find it necessary or preferable in
some situations. With this API, you import commands from PyCDP and pass them into the
session ``execute()`` method. Taking the same example as the previous section, here is
how you would execute a CSS query:

.. code::

    from cdp import dom
    
    ...other code...
 
    node_id = await session.execute(dom.query(root, 'blockquote'))

If you compare this example to the example in the previous section, there are two big changes.
First, ``dom`` is imported from PyCDP instead of Trio CDP. This means that is a generator,
not an ``async def``.

Second, in order to run the command on a given session, we have to call that session's
``execute()`` method and pass in the PyCDP generator.

Other than being a little more verbose (calling ``session.execute(...)`` for every CDP
command), the low-level API is otherwise very similar to the simplified API described in
the previous section. It still takes the same arguments and returns the same type (here
a ``NodeId``).
