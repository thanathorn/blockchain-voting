import socket

NodeID = 0x0000000000000001

# Threads:
# 1. Master Listener thread (Port 30001)
# 2. Mining Thread
#
# Tasks:
# 1. Receive request from Master
#   1.1 Mine block request
#   1.2 Stop mining request
# 2. Mining
# 3. Purpose mined block to Master


def requestFullChainFromMaster():
    pass


def proposeBlockToMaster():
    pass


def listenMasterRequest():
    pass


def mine():
    pass
