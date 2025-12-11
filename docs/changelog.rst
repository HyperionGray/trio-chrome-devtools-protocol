Changelog
=========

Unreleased
----------

* Add ``find_chrome_debugger_url()`` function for programmatic discovery of Chrome's WebSocket URL.
* ``open_cdp()`` now accepts HTTP URLs (e.g., ``http://localhost:9222``) which are automatically resolved to WebSocket URLs.

0.6.0
-----

* Simplified calling convention for CDP commands.

0.5.0
-----

* **Backwards Compability Break:** Rename `open_cdp_connection()` to `open_cdp()`.
* Fix `ConnectionClosed` bug.

0.4.0
-----

* Add support for passing in a nursery. (Supports usage in Jupyter notebook.)

0.3.0
-----

* New APIs for enabling DOM events and Page events.

0.2.0
-----

* Restructure event listeners.

0.1.0
-----

* Initial version
