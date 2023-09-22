#!/usr/bin/env python3

import logging
import socket
import threading

from rfc5389stunserver.constants import MsgClass, MethodType, AttrType
from rfc5389stunserver.parser import Parser
from rfc5389stunserver.stun_header import STUNHeader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def udp_thread(server: socket, address: tuple, data: bytes):
    '''
    メッセージを受信
    最初の00やmagic cookieの値の正当性を確かめる
    メッセージ長、メソッドとクラスの正当性
    fingerprintを使ってる場合、その正しさ
    エラーがある場合はただ捨てる
    認証チェック
    '''
    # headerの中身をごにょごにょして残りの長さを求める
    header, payload = data[0: 20], data[20:]

    obj = Parser.parse(header, payload, address)
    server.sendto(b''.join(map(lambda x: x.bin, obj)), address)


def create_udp_server(PORT: int):
    server = socket.socket(socket.AF_INET | socket.AF_INET6,
                           socket.SOCK_DGRAM)
    try:
        server.bind((socket.gethostname(), PORT))
    except socket.gaierror:
        server.bind(('', PORT))
    logger.info('UDP server: Start listening')

    while True:
        # Receive data from someone
        (data, address) = server.recvfrom(16384)  # 長さは適当
        th = threading.Thread(
            target=udp_thread, args=([server, address, data]))
        th.start()


def create_udp_server_thread(PORT: int):
    th = threading.Thread(target=create_udp_server, args=([PORT]))
    th.start()
    return th
