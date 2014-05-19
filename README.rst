.. _Emencia: http://www.emencia.com

REST client to retrieve and push datas on a PO-Projects service.

This is in early stage development.

The purpose of this client is to install PO files from a PO-Projects translation project in your Django project (or Optimus), or to send updated POT files to update translation project on the service.

DONE:

* Base structure;
* Command line frontend;
* Command to retrieve a project and get its tarball;

TODO:

* Command to send update for the POT file;

Install
=======

Require
*******

* `nap`_ >= 1.0.0;
* pkginfo >= 1.2b1;
* argparse == 1.2.1;
* argcomplete == 0.8.0;
* argh == 0.24.1;

Usage
=====

Before starting to use it, you must create a new translation project on you PO-Projects service. Note its ``slug`` name.

And so execute the action:

    po_projects [ACTION]

By example to update your PO files from the current project tarball :

    po_projects pull

But if it's your first usage, you should need to give some arguments to commandline, check those require ones with the help :

    po_projects help pull

After the first successful connect on the service, a 'po_projects.cfg' config file will be writed at the current directory, it will contains all required stuff needed to connect to the service and get the project datas without to specify them again in command arguments.

Also you can write the config file before the first usage to avoid to give command arguments. Just write this in a "po_projects.cfg" file at the root of your project (or everywhere you want to use the client command):

    [PO_Project]
    host = http://192.168.0.103:8001/po/rest/
    password = mypassword
    user = myusername
    locale_path = project/locale
    project_slug = myslug
    project_id = 42
    kind = django

* ``locale_path`` can be every relative path to the project locale directory which will contains the message catalogs structure with the PO files;
* ``kind`` can be ``django`` or ``optimus``;
* ``project_id`` is actually not used, so it is optional, the client will retrieve itself on the first usage and will write it in the config file;
