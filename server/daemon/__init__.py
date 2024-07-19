# read configuration file
from configparser import ConfigParser
from os.path import exists

CONFIG_PATH = 'config.ini'

# if file does not exist, make it
if not exists(CONFIG_PATH):
    open(CONFIG_PATH, 'w').close() # touch it 

config = ConfigParser()
config.read(CONFIG_PATH)

MAINTAIN_PERIOD = int(config['DEFAULT'].get('MAINTAIN_PERIOD', 60))
