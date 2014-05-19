# -*- coding: utf-8 -*-
"""
Command line action
"""
import datetime, os

from requests.exceptions import HTTPError, ConnectionError, InvalidSchema

from argh import arg, ArghParser
from argh.exceptions import CommandError

from po_projects_client import logging_handler
from po_projects_client import __version__ as client_version
from po_projects_client.config import POProjectConfig
from po_projects_client.client import DoesNotExistException, POProjectClient

@arg('-u', '--user', default=None, help="Username to connect to the service")
@arg('-p', '--password', default=None, help="Password to connect to the service")
@arg('-o', '--host', default=None, help="Http(s) address to connect to the service")
@arg('-c', '--config', default='po_projects.cfg', help="Path to the client config file")
@arg('--passive', default=False, action='store_true', help="Disable config saving")
@arg('-l', '--loglevel', default='info', choices=['debug','info','warning','error','critical'], help="The minimal verbosity level to limit logs output")
@arg('--logfile', default=None, help="A filepath that if setted, will be used to save logs output")
@arg('-t', '--timer', default=False, action='store_true', help="Display elapsed time at the end of execution")
@arg('--project_slug', default=None, help="Project slug name")
@arg('--locale_path', default=None, help="Path to the locale directory")
@arg('--kind', default='django', help="Kind of message catalog", choices=['django','optimus'])
def pull(args):
    """
    Get the PO tarball
    """
    starttime = datetime.datetime.now()
    # Init, load and builds
    root_logger = logging_handler.init_logging(args.loglevel.upper(), logfile=args.logfile)
    
    # Open config file if exists
    config = POProjectConfig()
    config.open(args.config)
    configdatas = config.get_datas()
    # Merge config in arguments for empty argument only
    for item in POProjectConfig.options:
        if item in configdatas:
            val = getattr(args, item, None) or configdatas[item]
            setattr(args, item, val)
            root_logger.debug("Set config value '%s' to: %s", item, val)
    
    # Validate required argument to connect
    if not args.user or not args.password or not args.host:
        root_logger.error("'user', 'password' and 'hostname' are required arguments to connect to the service")
        raise CommandError('Error exit')
    # Validate required argument to register
    if not args.project_slug:
        root_logger.error("Project 'slug' name is a required argument")
        raise CommandError('Error exit')
    # Validate locale dir path argument
    if args.locale_path and not os.path.exists(args.locale_path):
        root_logger.error("The given locale directory path does not exists : %s"%args.locale_path)
        raise CommandError('Error exit')
    if args.locale_path and not os.path.isdir(args.locale_path):
        root_logger.error("The given locale directory path is not a directory")
        raise CommandError('Error exit')
    
    # Open client
    con = POProjectClient(args.host, (args.user, args.password))
    
    # Connect to the service
    try:
        con.connect()
    except (HTTPError, ConnectionError, InvalidSchema) as e:
        import traceback
        top = traceback.extract_stack()[-1]
        root_logger.error("%s: %s", type(e).__name__, e)
        raise CommandError('Error exit')
    
    # Pull the tarball
    try:
        project_id, project_slug = con.pull(args.project_slug, args.locale_path)
    except DoesNotExistException:
        root_logger.error("Project with slug '{0}' does not exist.".format(args.project_slug))
        raise CommandError('Error exit')
    else:
        args.project_id, args.project_slug = project_id, project_slug
    
    # Save config with current values
    if not args.passive:
        root_logger.debug("Saving config")
        values = {}
        for item in POProjectConfig.options:
            if hasattr(args, item):
                values[item] = getattr(args, item)
        
        config.set_datas(values)
        config.save()
    
    if args.timer:
        endtime = datetime.datetime.now()
        root_logger.info('Done in %s', str(endtime-starttime))


def main():
    """
    Main entrypoint for console_script (commandline script)
    """
    parser = ArghParser()
    parser.add_argument('-v', '--version', action='version', version=client_version)
    enabled_commands = [pull]
    
    parser.add_commands(enabled_commands)
    parser.dispatch()
