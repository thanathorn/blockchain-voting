import base64
import hashlib
import json
import pickle
import socket
import threading
import time
from helper import printLog
from blockchain import Blockchain
from transaction import Transaction
from merkle import MerkleTree
from block import Block
from multiprocessing import Process, Manager, Value
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

currentMiningID = None
minerState = "stop"
miningData = {
    "currentBlock": "",
    "prevBlock": ""
}
blockToMine = Block(0, 0)


def proposeBlockToMaster(nonce=None):
    if nonce is not None:
        proposal = {
            "packetType": "nonce",
            "data": {
                "nonce": nonce,
                "from": NodeID
            }
        }
        message = json.dumps(proposal).encode()
        minerClient.sendto(message, ('<broadcast>', 30001))
        time.sleep(1)


def listenMasterRequest():
    global blockToMine
    global miningData
    global currentMiningID
    global minerClient
    global minerState
    minerClient.bind(("192.168.1.15", 30001))
    while True:
        data, addr = minerClient.recvfrom(50000)
        # print("received message: %s" % data)
        try:
            incoming_data = json.loads(data)
            if incoming_data['packetType'] == "command":
                if incoming_data['data']['command'] == "stop":
                    minerState = "stop"
                printLog("listenMasterRequest", "received command")
            if incoming_data['packetType'] == "mine":
                printLog("listenMasterRequest", "received block to mine")
                miningData['currentBlock'] = incoming_data['data']['currentBlock']
                miningData['prevBlock'] = incoming_data['data']['prevBlock']
                blockReceived = pickle.loads(base64.b64decode(miningData['currentBlock'].encode()))
                if currentMiningID != blockReceived.getTimestamp():
                    currentMiningID = blockReceived.getTimestamp()
                    blockToMine = blockReceived
                    printLog("listenMasterRequest", "Received block {}".format(blockToMine.getTimestamp()))
                    # Start mining
                    minerState = "mining"
        except Exception as e:
            printLog("listenMasterRequest", "Exception", "error")
            print(e)


def mine():
    global minerState
    while True:
        if minerState == "mining":
            i = 0
            rootLeaf = blockToMine.merkle.Get_Root_leaf()
            while minerState == "mining":
                if blockToMine.prevBlock is None:
                    if int("0x{}".format(
                            hashlib.sha256(
                                str.encode("{}{}{}{}".format(
                                    blockToMine.timestamp, blockToMine.difficulty,
                                    i, rootLeaf)
                                )
                            ).hexdigest()
                    ), 16) > int(blockToMine.difficulty):
                        i = i + 1
                    else:
                        print(i)
                        proposeBlockToMaster(i)
                        # minerState = "stop"
                else:
                    if int("0x{}".format(
                            hashlib.sha256(
                                str.encode("{}{}{}{}{}".format(blockToMine.prevBlock,
                                                               blockToMine.timestamp, blockToMine.difficulty,
                                                               i, rootLeaf)
                                           )
                            ).hexdigest()
                    ), 16) > int(blockToMine.difficulty):
                        i = i + 1
                    else:
                        print(i)
                        proposeBlockToMaster(i)
                        minerState = "stop"


if __name__ == "__main__":
    global minerClient
    minerClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    minerClient.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    printLog("Starting", "miner....")
    printLog("Starting", "miner command receiver thread....")
    listenMasterRequestThread = threading.Thread(target=listenMasterRequest)
    printLog("Starting", "transaction listener thread....")
    mineThread = threading.Thread(target=mine)
    listenMasterRequestThread.start()
    mineThread.start()
