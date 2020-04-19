========
Advanced
========

Adding Custom Client
--------------------

The module is written to be as easily portable as possible. Therefore, any custom
client should be easily written to this library. The :class:`yippi.AbstractYippi.AbstractYippi`
class should be enough for you to inherit. And what you need to do is override the abstract functions.

For example, here's a snippet from AsyncYippiClient.

.. literalinclude:: ../yippi/AsyncYippi.py
    :language: python
