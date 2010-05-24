====================================================
Running GWT Applications On Google App Engine Python
====================================================

This sample application demonstrates how to run a client, written with GWT, on
Google App Engine (Python).


Running the application out of the box
--------------------------------------

Build and run the application::

  $ python bootstrap.py --distribute
  $ ./bin/buildout
  $ ./bin/dev_appserver parts/jsongae

Then access the application using a web browser with the following URL::

  http://localhost:8080/


Running tests
-------------

In order to run all functional tests enter the following command::

  $ bin/nosetests -v --with-gae --gae-application=parts/jsongae


Uploading and managing
----------------------

To upload application files, run::

  $ ./bin/appcfg update parts/jsongae

For a more detailed documentation follow this url::

  http://code.google.com/appengine/docs/python/tools/uploadinganapp.html
