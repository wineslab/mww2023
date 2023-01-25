#!/usr/bin/env python3

#
# Differnt functions test 
#
from utils import *
    
def main():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((CONN_IP, CONN_PORT))
    msg = measpb.SessionMsg()
    msg.type = measpb.SessionMsg.INIT
    send_msg(conn, msg)
    msg.type = measpb.SessionMsg.CLOSE
    send_msg(conn, msg)
    #time.sleep(1)
    conn.close()
    exit(0)

if __name__ == "__main__":
    #main()
