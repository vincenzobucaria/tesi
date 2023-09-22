import logging

from rfc5389stunserver.constants import AttrType
from rfc5389stunserver.saslprep import SASLprep
from rfc5389stunserver.stun_attribute import STUNAttribute

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserName(STUNAttribute):
    def __init__(self, value):
        if len(SASLprep.saslprep(value).encode('utf-8')) > 513:
            logger.error('Too long username')
            raise Exception('Too long username')
        self.type = AttrType.USERNAME
        self.value = SASLprep.saslprep(value).encode('utf-8')

    @property
    def len(self):
        return len(self.value)
