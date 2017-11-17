'''
Created on 16.11.2017

@author: jtymoszuk
'''
import logging
message_format="%(asctime)s, %(levelname)s, %(module)s:%(lineno)d: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=message_format)
logger = logging.getLogger(__name__)