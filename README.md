IRIDA Uploader
==============


Download / Installation
--------------------

Installation instructions can be found in our documentation.

[ReadTheDocs](todo:link to read the docs needs to go here)

Creating the Windows installer from source code
------------------------------

A new windows installer can be built on linux, so first see the installation instructions for installing on linux in our documentation.

You will also need `nsis` installed to create the windows installer.

    $ sudo apt install nsis

Then run the command:

    $ make windows
    
This will create a new installer in the folder `build/nsis/` with a name similar to `IRIDA_Uploader_1.0.exe`

Running Tests
-------------

#### Unit tests

Running the unittests can be done with the command:

    $ make unittest

#### IRIDA Integration

To run integration tests your will need some additional software.

    $ sudo apt install xvfb

You will also need to download and install chromedriver http://chromedriver.chromium.org/downloads

You will need to allow the IRIDA instance to the mysql database needed for the tests

    $ mysql -e "CREATE USER 'test'@'localhost' IDENTIFIED BY 'test'; GRANT ALL ON irida_uploader_test.* to 'test'@'localhost';"

Running the IRIDA integration tests can be done with the command:

    $ make integrationtests

You can verify PEP8 conformity by running:

    $ ./scripts/verifyPEP8.sh

Note: No output is produced (other than `pip`-related output) if the PEP8 verification succeeds.

Documentation
------------------------------
Documentation is built by `mkdocs`. 

It can be built locally with:

    $ make docs

Or you can install mkdocs to your system:

    $ sudo apt install mkdocs
    $ mkdocs build

HTML docs will be generated to `site/` for local browsing

TODO: Alternatively ReadTheDocs here. (once we have it hosted)
