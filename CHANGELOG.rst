
Changelog
=========

0.2.0 (2021-06-19)
------------------
* **Drop Python 3.6 support.** The library now requires Python 3.7 or higher.
* **Bring back rate limit.** It is now compliant to e621's docs rate limiting, that is 2 requests per second.
* **Add ability to login with API key.**
* **Add ability to search pools.**
* **Post.rating is now an Enum.**
* Better type annotations. Thank you `Deer-Spangle <https://github.com/Deer-Spangle>`_ for the help!
* Handle 204 response properly from server by returning None.
* Handle errors properly by looking up if either message or response key exists in response.
* Add ability to use custom requests session on YippiSync client.
* All classes now have reference to the client. This is important for interaction abilities.
* Add __repr__ to classes.
* Add ability to favorite, unfavorite, and vote Post.
    Note: There are other functions, but those are not tested and should not be used as of now.

0.1.0 (2020-04-19)
------------------

* Initial release.
