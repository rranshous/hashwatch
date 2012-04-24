## setup our config
from lib.configsmash import ConfigSmasher
from os.path import abspath

class SimpleConfig(dict):
    def __init__(self, *args, **kwargs):
        super(SimpleConfig, self).__init__(*args, **kwargs)
        self.file_paths = []

    def setup(self, *file_paths):

        # we want to be sure
        file_paths = [abspath(p) for p in file_paths]

        # we can't reset ourself, so we'll clear and
        # update in place
        self.clear()
        self.update(ConfigSmasher(file_paths).smash())

        # and update what we are based on
        self.file_paths = file_paths

config = SimpleConfig()
