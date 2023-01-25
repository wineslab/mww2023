#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

import sys
import time
import socket
import multiprocessing as mp

import measurements_pb2 as measpb
from baseconnector import BaseConnector
from common import *

DEF_IP = "127.0.0.1"

class InterfaceConnector(BaseConnector):
    CALL_QUIT = "quit"
    CALL_STATUS = "status"
    RES_READY = "ready"
    RES_NOTREADY = "notready"
    
    def __init__(self, args):
        super().__init__()
        self.server_ip = socket.gethostbyname(args.host)
        self.port = args.port
        if args.nickname:
            self.name = args.nickname
        else:
            self.name = socket.gethostname().split('.',1)[0]
        self.ptype = measpb.SessionMsg.IFACE_CLIENT
        self.sid = 0

    def _dispatch(self, msg, conn):
        self.DISPATCH[msg.type](self, msg, conn)
        
    def handle_init(self, msg, conn):
        self.sid = msg.sid
        self.logger.info("Connected with session id: %d" % self.sid)

    def handle_call(self, msg, conn):
        func = get_function(msg)
        if func in self.CALLS:
            # Handle calls meant for the connector (this class).
            self._send_msg(conn, self.CALLS[func](self, msg))
        elif msg.peertype == self.ptype:
            # Send calls from actual iface client to orchestrator
            msg.sid = self.sid
            self._send_msg(self.sock, msg)
        else:
            # Pass along calls to measurement interface (not used yet).
            self._send_msg(self.pipe, msg)

    def handle_result(self, msg, conn):
        # Pass result up to interface client code.
        # FIX: Need to distinguish outgoing vs incoming (if eventually needed).
        self._send_msg(self.pipe, msg)

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

    def status_call(self, msg):
        rmsg = mk_result(msg.uuid, self.ptype, self.CALL_STATUS)
        rmsg.sid = self.sid
        if self.sid != 0:
            add_attr(rmsg, "result", self.RES_READY)
        else:
            add_attr(rmsg, "result", self.RES_NOTREADY)
        return rmsg

    def stop_connector_call(self, msg):
        self.logger.info("Interface connector process exiting.")
        cmsg = measpb.SessionMsg()
        cmsg.sid = self.sid
        cmsg.type = measpb.SessionMsg.CLOSE
        cmsg.peertype = self.ptype
        self._send_msg(self.sock, cmsg)
        sys.exit(0)

    def run(self, pipe):
        super().setup(pipe)
        try:
            self.send_init()
        except:
            self.logger.error("Failed to connect to orchestrator!")
            self.pipe.close()
            exit(1)
        super().run()
                
    CALLS = {
        CALL_QUIT: stop_connector_call,
        CALL_STATUS: status_call,
    }
                
    DISPATCH = {
        measpb.SessionMsg.INIT: handle_init,
        measpb.SessionMsg.CALL: handle_call,
        measpb.SessionMsg.RESULT: handle_result,
        measpb.SessionMsg.HB: handle_hb,
        measpb.SessionMsg.CLOSE: handle_close,
    }
