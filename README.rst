.. _nap: https://github.com/kimmobrunfeldt/nap
.. _argh: http://argh.readthedocs.org/

REST client to retrieve and push datas on a PO-Projects service.

The purpose of this client is to install PO files from a PO-Projects translation project in your Django project (or Optimus), or to send updated POT files to update translation project on the service.

Install
=======

Require
*******

* `nap`_ >= 1.0.0;
* pkginfo >= 1.2b1;
* argparse == 1.2.1;
* argcomplete == 0.8.0;
* `argh`_ == 0.24.1;

Usage
=====

Before starting to use it, you must create a new translation project on you PO-Projects service. Note its ``slug`` name.

And so execute the action: ::

    po_projects [ACTION]

But if it's your first usage, you should need to give some arguments to commandline, check those require ones with the help : ::

    po_projects help [ACTION]

After the first successful connect on the service, a 'po_projects.cfg' config file will be writed at the current directory, it will contains all required stuff needed to connect to the service and get the project datas without to specify them again in command arguments.

Also you can write the config file before the first usage to avoid to give command arguments. Just write this in a "po_projects.cfg" file at the root of your project (or everywhere you want to use the client command): ::

    [PO_Project]
    host = http://192.168.0.103:8001/po/rest/
    password = mypassword
    user = myusername
    locale_path = project/locale
    project_slug = myslug
    kind = django
    django_default_locale = en_US

* ``user`` and ``password`` is from an User account registered on the service API, it needs to be an admin account (``is_staff`` = True);
* ``host`` is the full URL to use to connect to the service API;
* ``locale_path`` can be every relative path  or an absolute path to the project locales directory which will contains the message catalogs structure with the PO files;
* ``kind`` can be ``django`` or ``optimus``;

Actually you cannot create and register a new project on the service from the client, you have to create it before on the service, then note the slug name to use it with the client.

Pull
****

This is the command to get the current project translations tarball : ::

    po_projects pull

It will install or update your locales directory (``locale_path``) from the current existing project on a PO-Project service. Note that the previous locales directory will be replaced with the new one, you should backup it before if you care.


Push
****

This is the command to update a project translation on the service : ::

    po_projects push

It will send your current local translation catalog to the service so it will merge the translation strings on the project from extracted strings.

When using ``django`` kind, it requires an extra argument ``django_default_locale``, this is the directory name (relative to ``locale_path``) of the locale catalog to send to the service to update a project. ``optimus`` kind doesn't need it because it directly use the POT file that don't exists within a Django project;
