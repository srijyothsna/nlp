import ConfigParser

import logging
logger = logging.getLogger("nlp_logger")

class ConfigParserHelper:

    cfg = None

    def __init__(self):
        logger.debug("In the __init__ method")
        self.cfg = ConfigParser.ConfigParser()
        self.cfg.read("config.ini")
        #print self.cfg

    def get(self, section, key):
        return self.cfg.get(section, key)
