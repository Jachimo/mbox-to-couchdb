mbox-to-couchdb
===============

A quick-and-dirty utility for taking a Unix "mbox" style email archive, and loading it into a CouchDB instance for further processing.

The Python modules `tomli` and `couchdb`, both available via Pip, are required for operation.

The development target was Python 3.10, but it will probably run on versions as far back as 3.5, and hopefully won't break too soon with future versions.

Creating a virtual environment is recommended:

    cd mbox-to-couchdb
    python -m venv venv   # create a new virtual environment
    source venv/bin/activate
    pip install -r requirements.txt  # this should install tomli and couchdb
    python mbox-to-couchdb.py <mboxfile> <couchdbconfig.toml>

The program takes two arguments: the first is a path to a Unix-style MBOX email archive,
and the second is a TOML configuration file with information about the CouchDB instance you want to import the messages to.

An example config file is provided as `testing_db.toml`.  
Note that you will need to change the values in the file based on your CouchDB instance's URL, desired target database, and login credentials.

A DEBUG flag located near l.15 turns a bunch of extra debugging output on or off.
Set it to False if you want a somewhat-quieter mode of operation.


Sample Data
-----------

The files `sample.mbox` and `rfc2047-samples.mbox` are taken from the "qsnake" Git source tree, which is licensed under the GPLv2.
See <https://github.com/qsnake/git/tree/master/t/t5100> for the originals.


Additional Information
----------------------

Various extra, nonessential information is provided in the NOTES file, which may be of interest if you want to modify the program for your own use cases.
