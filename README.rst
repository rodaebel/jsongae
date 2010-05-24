======================================================
Running GWT Applications On Google App Engine (Python)
======================================================

This sample application demonstrates how to run a client written with GWT on
Google App Engine (Python). The client communicates with the server interfaces
through JSON/RPC (http://groups.google.com/group/json-rpc/web/json-rpc-2-0).


Copyright and License
---------------------

Copyright 2010 Tobias Rodaebel and Florian Glanzner

This software is released under the Apache License, Version 2.0. You may obtain
a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0


Requirements
------------

Most of the required libraries and programs (GWT, GAE SDK) will be installed by
zc.buildout.  See the buildout.cfg file.

The buildout needs Python and the tools contained in /bin and /usr/bin of a
standard installation of the Linux operating environment. You should ensure
that these directories are on your PATH and following programs can be found:

* Python 2.5.2+ (3.x is not supported!)
* virtualenv
* Java
* Ant


Building and Running the Application
------------------------------------

We recommend to install this buildout into a virtualenv in order to obtain
isolation from any 'system' packages you've got installed in your Python
version.

Install virtualenv::

  $ virtualenv --distribute jsongae-env
  $ cd jsongae-env
  $ git clone http://github.com/rodaebel/jsongae.git

Build and run the application::

  $ cd jsongae
  $ ../bin/python bootstrap.py --distribute
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
