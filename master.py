import base64
import datetime
import json
import pickle
import socket
import threading
import zmq

from blockchain import Blockchain
from transaction import Transaction
from merkle import MerkleTree
from block import Block
from helper import printLog
# Threads:
# 1. Question server thread (Port 80)
# 2. Miner Control thread (Port 30001)
# 3. Transaction receiver thread (Port 30002)
#
# Question server thread tasks:
# 1. Serving question and answer to Voter
# Miner Control thread tasks:
# 1. Send set of transactions to miner
#       - Send same transactions set every 5 minute if no miner purpose block
# 2. Stop mining when miner purpose a valid block (Verify before broadcast stop command)
# Transaction receiver thread tasks
# 1. Collect transactions from voter or registration
import time

minerServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
minerServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# minerServer.settimeout(1)
continueBroadcast = True
nonceListening = False
chain = Blockchain()
nonceCheckQueue = set()
txQueue = {
    "waiting_validate": [],
    "waiting": [],
    "mining": []
}
miningMutex = threading.Lock()
try:
    with open('mempool.bin', 'rb') as f:
        txQueue = pickle.load(f)
        print("[*] mempool: opening mempool file")
except (FileNotFoundError, EOFError):
    print("[*] mempool: creating mempool file")
    txQueue = {
        "waiting": [],
        "mining": []
    }

if len(txQueue['mining']):
    print("[*] mempool: there are tx in mining queue")
if len(txQueue['waiting']):
    print("[*] mempool: there are tx in waiting queue")


def txValidate():
    pass


def selfBroadcast():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(0.2)
    message = json.dumps({"address": socket.gethostbyname(socket.gethostname())}).encode()
    while True:
        server.sendto(message, ('<broadcast>', 30003))
        # print("[*] selfBroadcast: Broadcast complete")
        time.sleep(1)


def transactionListener():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:30002")
    printLog("transactionListener", "bind complete")

    while True:
        printLog("transactionListener", "waiting for tx")
        #  Wait for next request from client
        message = socket.recv()
        printLog("transactionListener", "received tx")
        printLog("transactionListener", message)
        try:
            tx_in = pickle.loads(message)
            txQueue['waiting'].append(tx_in)
            socket.send(b"OK")
            printLog("transactionListener", "received tx added to queue")
            # TODO: Validate tx overspend
        except:
            time.sleep(1)
            socket.send(b"ERROR")
            printLog("transactionListener", "received tx not added to queue", "error")


def txQueueManager():
    global miningMutex
    lastTimestamp = time.time()
    while True:
        if len(txQueue['mining']) != 0:
            printLog("txQueueManager", "{} transaction already in mining queue".format(len(txQueue['mining'])))
            time.sleep(20)
        else:
            if time.time() - lastTimestamp >= 600:
                lastTimestamp = time.time()
                printLog("txQueueManager", "time passed for 10 minute, adding remain txs to queue")
                if len(txQueue['waiting']) > 0:
                    while True:
                        try:
                            miningMutex.acquire()
                            for i in range(0, 10):
                                txQueue['mining'].append(txQueue['waiting'].pop())
                        except IndexError:
                            miningMutex.release()
                            break
                else:
                    printLog("txQueueManager", "no remain txs in queue")
                    printLog("txQueueManager", "adding dummy tx")
                    # TODO: mine dummy tx

            else:
                if len(txQueue['waiting']) >= 10:
                    lastTimestamp = time.time()
                    printLog("txQueueManager", "adding txs to queue")
                    while True:
                        try:
                            for i in range(0, 10):
                                txQueue['mining'].append(txQueue['waiting'].pop())
                        except IndexError:
                            break


def mempoolFileUpdate():
    while True:
        # print("[*] mempoolFileUpdate: updating mempool file storage")
        with open('mempool.bin', 'wb') as f2:
            pickle.dump(txQueue, f2, pickle.HIGHEST_PROTOCOL)
        time.sleep(3)


def minerManager():
    state = "stop"
    global continueBroadcast
    global nonceListening
    global txQueue
    global chain
    global miningMutex
    while True:
        if state == "mining":
            if len(txQueue['mining']):
                miningMutex.acquire()
                # Build Block
                printLog("minerManager", "building merkle tree")
                tree = MerkleTree(txQueue['mining'])
                miningMutex.release()
                tree.create_tree()
                printLog("minerManager", "building block")
                block = Block(time.time(), tree, prevBlockHash=chain.last_block().blockHash())
                printLog("minerManager", "dumping block")
                block_str = pickle.dumps(block)
                miningFile = open("currentBlock.txt", "w")
                miningFile.write(base64.b64encode(block_str).decode('ascii'))
                miningFile.close()
                printLog("minerManager", "building broadcast block")
                continueBroadcast = True
                nonceListening = True
                # Broadcast block ready
                message = json.dumps({
                    "packetType": "mine",
                    "data": {
                        "currentBlock": base64.b64encode(block_str).decode('ascii'),
                        "prevBlock": base64.b64encode(pickle.dumps(chain.last_block())).decode('ascii')
                    }
                }).encode()
                printLog("minerManager", "broadcasting block")
                # broadcast block and wait for nonce
                while continueBroadcast:
                    minerServer.sendto(message, ('<broadcast>', 30001))
                    if len(nonceCheckQueue):
                        block.nonce = nonceCheckQueue.pop()
                        printLog("minerManager", "checking nonce %s" % block.nonce)
                        if block.verifyNonce():
                            printLog("minerManager", "nonce checking complete, Correct")
                            block.calcHeader()
                            continueBroadcast = False
                            nonceListening = False
                            state = "stop"
                            chain.addBlock(block)
                            chain.save()
                            txQueue['mining'] = []
                            nonceCheckQueue.clear()
                        else:
                            printLog("minerManager", "nonce checking complete, Incorrect", "error")
                    time.sleep(1)
        elif state == "stop":
            stopPacket = {
                "packetType": "command",
                "data": {
                    "command": "stop"
                }
            }
            for i in range(0,5):
                minerServer.sendto(json.dumps(stopPacket).encode(), ('<broadcast>', 30001))
                time.sleep(1)
            if len(txQueue['mining']):
                state = "mining"

def nonceListener():
    global nonceCheckQueue
    global minerServer
    global nonceListening
    minerServer.bind(("192.168.1.14", 30001))
    while True:
        data, addr = minerServer.recvfrom(30000)
        if nonceListening:
            print("received message: %s" % data)
            try:
                incoming_data = json.loads(data)
                if incoming_data['packetType'] == "nonce":
                    printLog("nonceListener", "received nonce")
                    # add nonce to queue
                    nonceCheckQueue.add(incoming_data['data']['nonce'])
            except:
                pass

        else:
            time.sleep(0.2)


printLog("Starting", "master server....")
printLog("Starting", "master server address broadcasting thread....")
selfBroadcastThread = threading.Thread(target=selfBroadcast)
printLog("Starting", "transaction listener thread....")
transactionListenerThread = threading.Thread(target=transactionListener)
printLog("Starting", "transaction queue manager thread....")
txQueueManagerThread = threading.Thread(target=txQueueManager)
printLog("Starting", "mempool thread....")
mempoolFileUpdateThread = threading.Thread(target=mempoolFileUpdate)
printLog("Starting", "nonce listener thread....")
nonceListenerThread = threading.Thread(target=nonceListener)
printLog("Starting", "nonce listener thread....")
minerManagerThread = threading.Thread(target=minerManager)

selfBroadcastThread.start()
transactionListenerThread.start()
txQueueManagerThread.start()
mempoolFileUpdateThread.start()
nonceListenerThread.start()
minerManagerThread.start()

