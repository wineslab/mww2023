#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

#
# Shout orchestrator implementation.
#

import logging
import time
import argparse
import random
import multiprocessing as mp

import daemon

from baseconnector import BaseConnector
import measurements_pb2 as measpb
from common import *

DEF_LOGFILE="/var/tmp/shout_orchestrator.log"

class Client:
    def __init__(self, host, port, sid, name, ctype, conn):
        self.host = host
        self.port = port
        self.sid = sid
        self.name = name
        self.type = ctype
        self.conn = conn
        self.last = time.time()

class Orchestrator(BaseConnector):
    def __init__(self, args):
        super().__init__()
        self.listen = True
        self.port = args.port
        self.clients = {}
        self.callmap = {}
        self.ptype = measpb.SessionMsg.ORCH
        self._setup_logger(args.logfile)
        self.sid = 0

    def _setup_logger(self, logfile):
        fmat = logging.Formatter(fmt=LOGFMAT, datefmt=LOGDATEFMAT)
        shandler = logging.StreamHandler()
        shandler.setFormatter(fmat)
        fhandler = logging.FileHandler(logfile)
        fhandler.setFormatter(fmat)
        self.logger = mp.get_logger()
        self.logger.setLevel(LOGLEVEL)
        self.logger.addHandler(shandler)
        self.logger.addHandler(fhandler)

    def _get_client_with_sid(self, sid):
        for cli in self.clients.values():
            if cli.sid == sid: return cli
        return None

    def _get_client_with_name(self, name):
        for cli in self.clients.values():
            if cli.name == name: return cli
        return None

    def _dispatch(self, msg, conn):
        self.DISPATCH[msg.type](self, msg, conn)

    def _readsock(self, conn, mask):
        peername = repr(conn.getpeername())
        res = super()._readsock(conn, mask)
        if not res:
            if peername in self.clients:
                cli = self.clients[peername]
                self.logger.info("Removing client: %s" % cli.name)
                del self.clients[peername]

    def handle_init(self, msg, conn):
        sid = msg.sid
        if not sid:
            sid = random.getrandbits(31)
        name = get_attr(msg, "clientname")
        peerinfo = conn.getpeername()
        self.logger.info("INIT message from %s:%s" % peerinfo)
        self.clients[repr(peerinfo)] = Client(*peerinfo, sid, name, msg.peertype, conn)
        msg.sid = sid
        self._send_msg(conn, msg)

    def handle_call(self, msg, conn):
        func = get_function(msg)
        clients = msg.clients
        msg.ClearField("clients")
        if func in self.CALLS:
            # Handle calls meant for the connector (this class).
            self._send_msg(conn, self.CALLS[func](self, msg))
        elif clients:
            # Send along calls destined for measurement clients.
            self.callmap[msg.uuid] = msg.sid
            if clients[0] == "all":
                self.logger.info("Sending '%s' call (UUID %s) to all measurement clients" % (func, msg.uuid))
                for cli in filter(lambda c: c.type == measpb.SessionMsg.MEAS_CLIENT, self.clients.values()):
                    self._send_msg(cli.conn, msg)
            else:
                self.logger.info("Sending '%s' call to clients (UUID %s): %s" % (func, msg.uuid, clients))
                for cname in clients:
                    cli = self._get_client_with_name(cname)
                    if not cli:
                        self.logger.error("Client %s is not connected!  Cannot send %s call to it." % (cname, func))
                    else:
                        self._send_msg(cli.conn, msg)
        else:
            self.logger.warning("Unhandled call '%s' from peer %s" % (func, msg.sid))

    def handle_result(self, msg, conn):
        # Pass results back to calling client.
        mcli = self.clients[repr(conn.getpeername())]
        if not msg.uuid in self.callmap:
            self.logger.warning("No call (UUID) mapping for %s! Dropping result." % msg.uuid)
        else:
            ifcli = self._get_client_with_sid(self.callmap[msg.uuid])
            #del self.callmap[msg.uuid]  FIX: Need to clean up callmap.
            if not ifcli:
                self.logger.warning("Destination client for call with uuid %s is not connected! Dropping result." % msg.uuid)
            else:
                self.logger.info("Passing along result from client %s to iface client %s" % (mcli.sid, ifcli.sid))
                self._send_msg(ifcli.conn, msg)

    def handle_hb(self, msg, conn):
        pass

    def handle_close(self, msg, conn):
        peerinfo = conn.getpeername()
        self.logger.info("CLOSE message from %s:%s" % peerinfo)
        self.sel.unregister(conn)
        conn.close()
        if repr(peerinfo) in self.clients:
            del self.clients[repr(peerinfo)]

    def get_clients_call(self, msg):
        rmsg = mk_result(msg.uuid, self.ptype, get_function(msg))
        rmsg.sid = self.sid
        rmsg.clients.extend(
            [cli.name for cli in
             filter(lambda c: c.type == measpb.SessionMsg.MEAS_CLIENT,
                    self.clients.values())
             ])
        return rmsg

    def run(self):
        super().setup()
        super().run()
    
    CALLS = {
        OrchCalls.GETCLIENTS: get_clients_call,
    }

    DISPATCH = {
        measpb.SessionMsg.INIT: handle_init,
        measpb.SessionMsg.CALL: handle_call,
        measpb.SessionMsg.RESULT: handle_result,
        measpb.SessionMsg.HB: handle_hb,
        measpb.SessionMsg.CLOSE: handle_close,
    }

def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--logfile", type=str, default=DEF_LOGFILE)
    parser.add_argument("-p", "--port", help="Orchestrator port", default=SERVICE_PORT, type=int)
    parser.add_argument("-d", "--daemon", help="Run as daemon", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.daemon:
        # Daemonize
        dcxt = daemon.DaemonContext(umask=0o022)
        dcxt.open()
    orch = Orchestrator(args)
    orch.run()
