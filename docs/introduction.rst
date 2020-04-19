============
Introduction
============

Installation
------------

Yippi does not require many dependency,It only asks for the client as its dependency.

Currently there are two clients available:

- :obj:`aiohttp` (Async)
- :obj:`requests` (Sync)

To install, you can use ``pip``.::

    pip install yippi

And you should be ready to go.

Calling the API
---------------

Currenly, only GET routes are available for now. To initialize the client,
you have to supply your project name, version, and your username on e621.::

    from yippi import YippiClient, AsyncYippiClient

    client = YippiClient("MyProject", "1.0", "MyUsername")
    client = AsyncYippiClient("MyProject", "1.0", "MyUsername")

The only core functions are as follows.::

    client.posts()      # Searches e621
    client.post()       # Fetch for a post
    client.notes()      # Searches for notes
    client.flags()      # Searches for flags
    client.pools()      # Searches for pools

If you're using the async client, you only need to prepend the ``await`` statement.::

    await client.posts()
    await client.post()
    await client.notes()
    await client.flags()
    await client.pools()

An example is available on the Overview page.
