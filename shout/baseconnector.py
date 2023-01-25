#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

#
# Measurement server networking stuff
#

import logging
import time
import socket
import selectors
import struct
import select
import ipaddress
import multiprocessing as mp
import multiprocessing.connection

import measurements_pb2 as measpb
from common import *

BACKLOG = 10

class BaseConnector:
    MAX_CONN_TRIES = 1  # Each try waits CONN_SLEEP seconds before next.
    CONN_SLEEP = 0

    def __init__(self, maxconntries = MAX_CONN_TRIES, connsleep = CONN_SLEEP):
        self.listen = False  # Set to True in child to listen...
        self.listen_ip = LISTEN_IP
        self.port = SERVICE_PORT
        self.logger = mp.get_logger()
        self.pipe = None
        self.server_ip = None
        self.maxconntries = maxconntries
        self.connsleep = connsleep
        self.sel = selectors.DefaultSelector()
        self.ipranges = []
        for ipr in IPRANGES:
            self.ipranges.append(ipaddress.IPv4Network(ipr))

    def _setuplistener(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((self.listen_ip, self.port))
        lsock.listen(BACKLOG)
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, self._accept)
        self.logger.info("Listener started on port %d." % self.port)

    def _accept(self, sock, mask):
        (conn, addr) = sock.accept()
        (ip, port) = conn.getpeername()
        ipobj = ipaddress.IPv4Address(ip)
        validip = False
        for iprange in self.ipranges:
            if ipobj in iprange:
                validip = True
                break
        if not validip:
            self.logger.info("Rejected connection from %s" % ip)
            conn.close()
            return
        self.logger.info("Accepted connection: %s:%s" % (ip, port))
        # Causes issues with non-local iface client connections.
        # TODO: Look into potential issues later.
        #conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self._readsock)

    def _connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sel.register(self.sock, selectors.EVENT_READ, self._readsock)
        tries = 0
        while True:
            try:
                self.sock.connect((self.server_ip, self.port))
                break
            except (ConnectionRefusedError,) as e:
                self.logger.warning("Failed to connect to %s:%s: %s" %
                                    (self.server_ip, self.port, e))
                tries += 1
                if tries > self.MAX_CONN_TRIES:
                    self.logger.error("Too many connection attempts! Exiting.")
                    raise Exception("Too many connection attempts! Exiting.")
                time.sleep(self.CONN_SLEEP)
        
    # Must implement in child classes
    def _dispatch(self, msg, conn):
        pass

    def _get_msg_from_sock(self, conn):
        smsg = None
        peername = conn.getpeername()
        try:
            ldata = conn.recv(4)
        except (ConnectionResetError,) as e:
            self.logger.error("Client connection reset unexpectedly: %s:%s" %
                              peername)
            return None
        if ldata:
            mlen = struct.unpack(">L", ldata)[0]
            mbuf = bytearray()
            while len(mbuf) < mlen:
                rd, wt, xt = select.select([conn], [], [], 1)
                if not rd:
                    self.logger.warning("No data ready for read from socket.")
                try:
                    mbuf += conn.recv(mlen - len(mbuf))
                #except (ConnectionResetError,) as e:
                except:
                    self.logger.error("Client connection reset unexpectedly: %s:%s" % peername)
                    return None
            self.logger.debug("Received %d, indicated size %d." % (len(mbuf), mlen))
            smsg = measpb.SessionMsg()
            # FIX: Add exception handler
            smsg.ParseFromString(mbuf)
        return smsg
    
    def _readsock(self, conn, mask):
        rval = True
        msg = self._get_msg_from_sock(conn)
        if msg:
            self._dispatch(msg, conn)
        else:
            peerinfo = conn.getpeername()
            self.logger.warning("Connection to %s:%s closed unexpectedly." %
                                peerinfo)
            self.sel.unregister(conn)
            conn.close()
            rval = False
        return rval

    def _readpipe(self, pipe, mask):
            msg = measpb.SessionMsg()
            msg.ParseFromString(pipe.recv())
            self._dispatch(msg, pipe)

    def _send_msg(self, conn, msg):
        smsg = msg.SerializeToString()
        if isinstance(conn, mp.connection.Connection):
            conn.send(smsg)
        else:
            packed_len = struct.pack(">L", len(smsg))
            conn.sendall(packed_len + smsg)

    def setup(self, pipe = None):
        if pipe:
            self.pipe = pipe
            self.sel.register(self.pipe, selectors.EVENT_READ, self._readpipe)
        if self.listen:
            self._setuplistener()
        else:
            self._connect()

    def run(self):
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
