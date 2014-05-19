# -*- coding: utf-8 -*-
import json, logging, os
import tarfile, StringIO, tempfile, shutil

from requests.exceptions import HTTPError

from nap.url import Url

from po_projects_client import __version__ as client_version
from po_projects_client import logging_handler

class DoesNotExistException(HTTPError):
    pass

class POProjectClient(object):
    """
    THE client
    """
    _connected = False
    _projects_map = {}
    
    client_headers = {
        'client_agent': 'po-projects-client/{0}'.format(client_version),
        'content-type': 'application/json',
    }
    
    endpoint_projects_path = 'projects/'
    endpoint_projectcurrent_path = 'projects/current/'
    
    project_id = None
    project_slug = None
    project_tarball_url = None
    
    def __init__(self, root_url, auth_settings, debug_requests=True):
        self.logger = logging.getLogger('po_projects_client')
        
        self.root_url = root_url
        self.auth_settings = auth_settings
        
        self.debug_requests = debug_requests
    
    def connect(self, dry_run=False):
        """
        Connecting to endpoints
        """
        self.api_base = Url(self.root_url, auth=self.auth_settings)
        
        self.api_endpoint_projects = self.api_base.join(self.endpoint_projects_path)
        self.api_endpoint_projectcurrent = self.api_base.join(self.endpoint_projectcurrent_path)
        
        # Trying to connect to the base to check if the service is reachable
        if not dry_run:
            self.logger.info("Connecting to PO-Projects service on: %s", self.root_url)
            response = self.api_base.get()
            if response.status_code != 200:
                response.raise_for_status()
            #self.map_projects()
            
        self._connected = True
    
    def get_project(self, slug):
        """
        Try to get the project details to see if it exists
        """
        self.project_detail_url = self.api_endpoint_projectcurrent.join('{0}/'.format(slug))
        response = self.project_detail_url.get()#.json()
        if response.status_code == 404:
            raise DoesNotExistException("Project with slug '{0}' does not exist.".format(slug))
        elif response.status_code != 200:
            response.raise_for_status()
        
        datas = response.json()
        self.project_id = datas['id']
        self.project_slug = datas['slug']
        self.project_tarball_url = datas['tarball_url']
 
    def pull(self, slug, destination, commit=True):
        """
        Get the tarball to install updated PO files
        
        @commit arg to effectively install PO files or not
        """
        self.logger.debug("Downloading the tarball")
        # Get project datas
        self.get_project(slug)
        
        tarball_url = Url(self.project_tarball_url, auth=self.auth_settings)
        # Get the tarball
        response = tarball_url.get(stream=True)
                
        # Get a temporary directory
        tmpdir = tempfile.mkdtemp(suffix='_po-projects-client')
        
        self.logger.debug("Opening the tarball")
        # Write the tarball in memory
        fp = StringIO.StringIO()
        for chunk in response.iter_content(1024):
            fp.write(chunk)
        fp.seek(0)
        
        # Extract the file to the temp directory
        tar = tarfile.open(fileobj=fp)
        tar.extractall(path=tmpdir)
        tar.close()
        fp.close()
        
        if commit:
            self.logger.debug("Installing the tarball")
            # Remove the previous locale dir if any
            if os.path.exists(destination):
                shutil.rmtree(destination)
            
            # Put the new locale dir
            shutil.move(os.path.join(tmpdir, 'locale'), destination)
       
        # Remove the temp dir
        os.removedirs(tmpdir)
        
        if commit:
            self.logger.info("Succeed to install the tarball to: %s", destination)
        else:
            self.logger.info("Succeed to download the tarball")
        
        return self.project_id, self.project_slug
 

# Testing
if __name__ == "__main__":
    API_ROOT_URL = 'http://192.168.0.103:8001/po/rest/'

    con = POProjectClient(API_ROOT_URL, ('emencia', 'django324'))
    con.connect()
