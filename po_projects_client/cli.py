# -*- coding: utf-8 -*-
"""
Command line action

NOTE: Django does not generate a *.POT file when extracting translation strings, POT file seem a specific format from Babel, but PO-Project need it, so we use 'django_default_locale' argument to gives a default locale to use to generate the POT file. This locale should be a locale that is not really translated, like the 'en' locale for a webapp using 'en' locale to writes the translation strings sources.
"""
import datetime, os

from requests.exceptions import HTTPError, ConnectionError, InvalidSchema

from argh import arg, ArghParser
from argh.exceptions import CommandError

from po_projects_client import logging_handler
from po_projects_client import __version__ as client_version
from po_projects_client.config import POProjectConfig
from po_projects_client.client import ProjectDoesNotExistException, PotDoesNotExistException, POProjectClient


# Available common options for all commands
cmd_user_opt = arg('-u', '--user', default=None, help="Username to connect to the service")
cmd_password_opt = arg('-p', '--password', default=None, help="Password to connect to the service")
cmd_host_opt = arg('-o', '--host', default=None, help="Http(s) address to connect to the service")
cmd_config_opt = arg('-c', '--config', default='po_projects.cfg', help="Path to the client config file")
cmd_passive_opt = arg('--passive', default=False, action='store_true', help="Disable config saving")
cmd_loglevel_opt = arg('-l', '--loglevel', default='info', choices=['debug','info','warning','error','critical'], help="The minimal verbosity level to limit logs output")
cmd_logfile_opt = arg('--logfile', default=None, help="A filepath that if setted, will be used to save logs output")
cmd_timer_opt = arg('-t', '--timer', default=False, action='store_true', help="Display elapsed time at the end of execution")
cmd_projectslug_opt = arg('--project_slug', default=None, help="Project slug name")
cmd_localepath_opt = arg('--locale_path', default=None, help="Path to the locale directory")
cmd_kind_opt = arg('--kind', default='django', help="Kind of message catalog", choices=['django','messages'])
cmd_djangodefaultlocale_opt = arg('--django_default_locale', default=None, help="Default locale used to generate a temporary POT file")


class CliInterfaceBase(object):
    """
    The common base CLI interface to use within a command function
    
    It takes care of the logging, timer, config and service connection, also embed some common args validate
    """
    def __init__(self, args):
        self.args = args
        
        self.config = None
        self.con = None
        
        self.starttime = datetime.datetime.now()
        # Init, load and builds
        self.root_logger = logging_handler.init_logging(self.args.loglevel.upper(), logfile=self.args.logfile)
    
    def open_config(self):
        # Open config file if exists
        self.config = POProjectConfig()
        self.config.open(self.args.config)
        configdatas = self.config.get_datas()
        # Merge config in arguments for empty argument only
        for item in POProjectConfig.options:
            if item in configdatas:
                val = getattr(self.args, item, None) or configdatas[item]
                setattr(self.args, item, val)
                self.root_logger.debug("Set config value '%s' to: %s", item, val)
    
    def save_config(self):
        # Save config with current values
        if self.config and not self.args.passive:
            self.root_logger.debug("Saving config")
            values = {}
            for item in POProjectConfig.options:
                if hasattr(self.args, item):
                    values[item] = getattr(self.args, item)
            
            self.config.set_datas(values)
            self.config.save()
    
    def connect(self):
        """
        Connect to the PO Project API service
        """
        # Open client
        self.con = POProjectClient(self.args.host, (self.args.user, self.args.password))
        
        # Connect to the service
        try:
            self.con.connect()
        except (HTTPError, ConnectionError, InvalidSchema) as e:
            import traceback
            top = traceback.extract_stack()[-1]
            self.root_logger.error("%s: %s", type(e).__name__, e)
            raise CommandError('Error exit')
    
    def close(self):
        if self.args.timer:
            endtime = datetime.datetime.now()
            self.root_logger.info('Done in %s', str(endtime-self.starttime))
    
    def validate_authentication_args(self):
        # Validate required arguments to connect
        if not self.args.user or not self.args.password or not self.args.host:
            self.root_logger.error("'user', 'password' and 'hostname' are required arguments to connect to the service")
            raise CommandError('Error exit')
    
    def validate_slug_args(self):
        # Validate required argument to reach the project
        if not self.args.project_slug:
            self.root_logger.error("Project 'slug' name is a required argument")
            raise CommandError('Error exit')
    
    def validate_locale_path_args(self):
        # Validate locale dir path argument
        if self.args.locale_path and not os.path.exists(self.args.locale_path):
            self.root_logger.error("The given locale directory path does not exists : %s"%self.args.locale_path)
            raise CommandError('Error exit')
        if self.args.locale_path and not os.path.isdir(self.args.locale_path):
            self.root_logger.error("The given locale directory path is not a directory")
            raise CommandError('Error exit')
        # Validate the required argument when kind is 'django', needed to do a trick for a POT file
        if self.args.kind == 'django':
            if not self.args.django_default_locale:
                self.root_logger.error("For 'django' kind you have to give a default locale directory name (relative to 'locale_path') with '--django_default_locale'")
                raise CommandError('Error exit')
            default_locale_path = os.path.join(self.args.locale_path, self.args.django_default_locale)
            if not os.path.exists(default_locale_path) or not os.path.isdir(default_locale_path):
                self.root_logger.error("The default locale path does not exists or is not a directory: %s"%default_locale_path)
                raise CommandError('Error exit')


@cmd_user_opt
@cmd_password_opt
@cmd_host_opt
@cmd_config_opt
@cmd_passive_opt
@cmd_loglevel_opt
@cmd_logfile_opt
@cmd_timer_opt
@cmd_projectslug_opt
@cmd_localepath_opt
@cmd_kind_opt
def pull(args):
    """
    Get the PO tarball
    
    TODO: need to use the 'kind' argument to request the right tarball for django or optimus (changing name for catalog files)
    """
    interface = CliInterfaceBase(args)
    
    interface.open_config()
    
    interface.validate_authentication_args()
    interface.validate_slug_args()
    interface.validate_locale_path_args()
    
    interface.connect()
    
    # Pull the tarball
    try:
        project_id, project_slug = interface.con.pull(args.project_slug, args.locale_path, args.kind)
    except ProjectDoesNotExistException as e:
        interface.root_logger.error(e)
        raise CommandError('Error exit')
    else:
        interface.args.project_id, interface.args.project_slug = project_id, project_slug
    
    interface.save_config()
    interface.close()


@cmd_user_opt
@cmd_password_opt
@cmd_host_opt
@cmd_config_opt
@cmd_passive_opt
@cmd_loglevel_opt
@cmd_logfile_opt
@cmd_timer_opt
@cmd_projectslug_opt
@cmd_localepath_opt
@cmd_djangodefaultlocale_opt
def push(args):
    """
    Send the current local POT file
    """
    interface = CliInterfaceBase(args)
    
    interface.open_config()
    
    interface.validate_authentication_args()
    interface.validate_slug_args()
    interface.validate_locale_path_args()
    
    interface.connect()
    
    # Push the POT
    try:
        interface.con.push(args.project_slug, args.locale_path, args.kind, args.django_default_locale)
    except (ProjectDoesNotExistException, PotDoesNotExistException) as e:
        interface.root_logger.error(e)
        raise CommandError('Error exit')
    
    interface.save_config()
    interface.close()


def main():
    """
    Main entrypoint for console_script (commandline script)
    """
    parser = ArghParser()
    parser.add_argument('-v', '--version', action='version', version=client_version)
    enabled_commands = [pull, push]
    
    parser.add_commands(enabled_commands)
    parser.dispatch()
