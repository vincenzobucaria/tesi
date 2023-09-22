import logging

from rfc5389stunserver.constants import AttrType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class STUNAttribute:
    def __init__(self):
        self.type = 1  # tmp 2byte
        self.length = 3  # tmp 2byte
        self.value = (5).to_bytes(self.length, 'big')  # tmp 4byte * n

    @property
    def padding_length(self):
        return (4 - self.length % 4) % 4

    @property
    def bin(self):
        return (self.type.to_bytes(2, 'big') + self.length.to_bytes(2, 'big') +
                self.value + (0).to_bytes(self.padding_length, 'big'))
