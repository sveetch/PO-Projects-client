import os, ConfigParser

class POProjectConfig(object):
    """
    PO-Project config object know how to get, set and save data from/to the config file
    """
    main_section_name = 'PO_Project'
    options = ['user', 'password', 'host', 'locale_path', 'kind', 'project_id', 'project_slug']
    integers = ['project_id']
    booleans = []
    
    def __init__(self):
        self._datas = None
        self._filepath = None
        self.parser = ConfigParser.SafeConfigParser()
        self.parser.optionxform = str
    
    def open(self, filepath):
        """
        Open the given filepath as a config file, does not raise exception if 
        the given filepath does not exist
        """
        self._filepath = filepath
        self.parser.read([filepath])
        if not self.parser.has_section(self.main_section_name):
            self.parser.add_section(self.main_section_name)
    
    def set_datas(self, datas):
        """
        Update datas from a dict
        """
        if self._datas is None:
            self._datas = {}
        self._datas.update(datas)
        for k,v in datas.items():
            # Don't try to save None values
            if v is None:
                continue
            # Format number values to string
            if k in self.integers:
                v = str(v)
            # Format boolean values to string
            if k in self.booleans:
                v = str(v).lower()
            self.parser.set(self.main_section_name, k, v)
        return self._datas
    
    def get_datas(self):
        """
        Get all valid datas from the readed config file
        """
        if self._datas is None:
            self._datas = {}
        q = [item for item in self.parser.options(self.main_section_name) if item in self.options]
        for item in q:
            val = self.parser.get(self.main_section_name, item)
            # Re apply format for non string value
            if item in self.integers:
                val = int(val)
            if item in self.booleans:
                val = (val == 'true')
            self._datas[item] = val
        return self._datas
    
    def save(self):
        """
        Saving changes to the config file
        """
        if not self._filepath:
            return None
            
        with open(self._filepath, 'wb') as configfile:
            self.parser.write(configfile)
            
        return self._filepath
    

# Testing
if __name__ == "__main__":
    conf = POProjectConfig()
    conf.open('po_projects.conf')
    conf.set_datas({
        'user': "foo",
        'hello': 'world',
        'yum': '42',
    })
    conf.save()
    
    conf.set_datas({
        'user': "bar",
        'hello': 'coco',
        'yum': '42',
    })
    conf.save()
    
