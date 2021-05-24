import base64
import json
import pickle
import socket
import threading
import zmq

from blockchain import Blockchain
from transaction import Transaction
from merkle import MerkleTree
from block import Block
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

nonceCheckQueue = []
txQueue = {
    "waiting": [],
    "mining": []
}

try:
    with open('mempool.bin', 'rb') as f:
        txQueue = pickle.load(f)
except (FileNotFoundError, EOFError):
    txQueue = {
        "waiting": [],
        "mining": []
    }


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
    print("[*] transactionListener: bind complete")

    while True:
        print("[*] transactionListener: waiting for tx")
        #  Wait for next request from client
        message = socket.recv()
        print("[*] transactionListener: received tx")
        print("[*] transactionListener:  %s" % message)
        try:
            tx_in = pickle.loads(message)
            txQueue['waiting'].append(tx_in)
            socket.send(b"OK")
            print("[*] transactionListener: received tx added to queue")
            # TODO: Validate tx overspend
        except:
            time.sleep(1)
            socket.send(b"ERROR")
            print("[!] transactionListener: received tx not added to queue")


def txQueueManager():
    lastTimestamp = time.time()
    while True:
        if len(txQueue['mining']) != 0:
            print("[*] txQueueManager: transaction already in mining queue")
            time.sleep(20)
        else:
            if time.time() - lastTimestamp >= 600:
                print("[*] txQueueManager: time passed for 10 minute, adding txs to queue")
                if len(txQueue['waiting']) >= 0:
                    while True:
                        try:
                            for i in range(0, 10):
                                txQueue['mining'].append(txQueue['waiting'].pop())
                        except IndexError:
                            break
            else:
                if len(txQueue['waiting']) >= 10:
                    print("[*] txQueueManager: adding txs to queue")
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
    state = "mining"
    global continueBroadcast
    global nonceListening
    global txQueue
    while True:
        print("[*] minerManager: state is %s" % state)
        if state == "mining":
            if len(txQueue['mining']):
                # Build Block
                print("[*] minerManager: building merkle tree")
                tree = MerkleTree(txQueue['mining'])
                tree.create_tree()
                print("[*] minerManager: building block")
                block = Block(time.time(), tree)
                print("[*] minerManager: dumping block")
                block_str = pickle.dumps(block)
                miningFile = open("currentBlock.txt", "w")
                miningFile.write(base64.b64encode(block_str).decode('ascii'))
                miningFile.close()
                print("[*] minerManager: broadcasting block")
                continueBroadcast = True
                nonceListening = True
                # Broadcast block ready
                chain = Blockchain()
                message = json.dumps({
                    "packetType": "mine",
                    "data": {
                        "currentBlock": base64.b64encode(block_str).decode('ascii'),
                        "prevBlock": base64.b64encode(pickle.dumps(chain.last_block())).decode('ascii')
                    }
                }).encode()
                print("[*] minerManager: broadcasting block")
                # broadcast block and wait for nonce
                while continueBroadcast:
                    minerServer.sendto(message, ('<broadcast>', 30001))
                    if len(nonceCheckQueue):
                        block.nonce = nonceCheckQueue.pop()
                        print("[*] minerManager: checking nonce %s" % block.nonce)
                        if block.verifyNonce():
                            print("[*] minerManager: nonce checking complete, Correct")
                            continueBroadcast = False
                            nonceListening = False
                            state = "stop"
                            # TODO: Add to chain
                        else:
                            print("[!] minerManager: nonce checking complete, Incorrect")
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


def nonceListener():
    global nonceCheckQueue
    global minerServer
    global nonceListening
    minerServer.bind(("", 30001))
    while True:
        if nonceListening:
            data, addr = minerServer.recvfrom(4096)
            print("[*] nonceListener: received nonce")
            print("received message: %s" % data)
            # add nonce to queue
            nonceCheckQueue.append(data)
        else:
            time.sleep(0.2)


print("[*] Starting master server....")
print("[*] Starting master server address broadcasting thread....")
selfBroadcastThread = threading.Thread(target=selfBroadcast)
print("[*] Starting transaction listener thread....")
transactionListenerThread = threading.Thread(target=transactionListener)
print("[*] Starting transaction queue manager thread....")
txQueueManagerThread = threading.Thread(target=txQueueManager)
print("[*] Starting mempool thread....")
mempoolFileUpdateThread = threading.Thread(target=mempoolFileUpdate)
print("[*] Starting nonce listener thread....")
nonceListenerThread = threading.Thread(target=nonceListener)

selfBroadcastThread.start()
transactionListenerThread.start()
txQueueManagerThread.start()
mempoolFileUpdateThread.start()
nonceListenerThread.start()

