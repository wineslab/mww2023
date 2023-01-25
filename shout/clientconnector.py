#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

import time
import socket
import multiprocessing as mp

import measurements_pb2 as measpb
from baseconnector import BaseConnector
from common import *

class ClientConnector(BaseConnector):
    MAX_CONN_TRIES = 12 * 15  # Each try waits CONN_SLEEP seconds before next.
    CONN_SLEEP = 5

    def __init__(self, args):
        super().__init__(self.MAX_CONN_TRIES, self.CONN_SLEEP)
        self.server_ip = socket.gethostbyname(args.host)
        self.port = args.port
        if args.nickname:
            self.name = args.nickname
        else:
            self.name = socket.gethostname().split('.',1)[0]
        self.ptype = measpb.SessionMsg.MEAS_CLIENT
        self.sid = 0

    def _dispatch(self, msg, conn):
        self.DISPATCH[msg.type](self, msg, conn)

    def _readsock(self, conn, mask):
        res = super()._readsock(conn, mask)
        if not res:
            self._connect()
            self.send_init()

    def handle_init(self, msg, conn):
        self.sid = msg.sid
        self.logger.info("Connected with session id: %d" % self.sid)

    def handle_call(self, msg, conn):
        func = get_function(msg)
        if func in self.CALLS:
            # Handle calls meant for the connector (this class).
            self._send_msg(conn, self.CALLS[func](self, msg))
        else:
            # Send along calls destined for the client measurement code
            self._send_msg(self.pipe, msg)

    def handle_result(self, msg, conn):
        # Pass result back to server.
        msg.sid = self.sid
        add_attr(msg, "clientname", self.name)
        self._send_msg(self.sock, msg)

    def handle_hb(self, msg, conn):
        pass

    def handle_close(self, msg, conn):
        pass
    
    def send_init(self):
        msg = measpb.SessionMsg()
        msg.type = measpb.SessionMsg.INIT
        msg.peertype = self.ptype
        msg.sid = self.sid
        add_attr(msg, "clientname", self.name)
        self._send_msg(self.sock, msg)

    def run(self, pipe):
        super().setup(pipe)
        self.send_init()
        super().run()
        
    CALLS = {}
                
    DISPATCH = {
        measpb.SessionMsg.INIT: handle_init,
        measpb.SessionMsg.CALL: handle_call,
        measpb.SessionMsg.RESULT: handle_result,
        measpb.SessionMsg.HB: handle_hb,
        measpb.SessionMsg.CLOSE: handle_close,
    }
