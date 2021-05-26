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
from helper import printLog
import copy
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
prikey = """-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAobve3e/IvnBc/mqAoNURIF++ZVMNnih3Nf3UkC2QSpQn/vIj
NRZHXb4Vq9lgpnvAezbakbAr/w1CrVPjCA4sjywFC93h4TC8oJKuzVmDBWdJxbs4
BRTwSzeerCtGXv+ZRvsSP9WIKXFX0II5BUo+50uaASMvF+mBzNs75XDqZ9ooeYX6
jwCchSAIa2kpCV/rtuT2ABGVNVY62VmJ+d4WFfXDEilDpUwZ0exPA3sqObJqqYjl
JyQekvlEDpJvLshz6B2wBu7slqmn9s07it83emqC4kP7HPO3Di9ggPly/KLa47Ge
+jpjM+Nq6yiGrqHiTI0ZqLf+ncoKgIRqK3Di3QIDAQABAoIBAQCauGY5PJV3EXj0
7h/FPG9Y4B79QZmqbp20afI6R0xc/CTS8QMbWwfEtv52WsrqGUMG3G/1pWpBYYci
1zg+UYjxIjRlqMrYqc4ZcpmE2xfLSIc7gKHTwrcpzbiejfuRD8WrMK7BoF3U/5f5
YUp5NBC/JgTbB7SalIjW1/gRw5aK55OShqE9ECRqhwIiIsOpTqLkwscGV5r3SAt4
Fll5WJ2TcjivLqApsK5Adv9y2mp/FCaV4M8sursLXkiCtgIOsuiic4Ezz6TdOyH2
OVj8qhoRl0oHxF/Um6Z3whRykKZILdgobyZWmomCH6gfcQL8Rz0pNx7QcPl6imDi
sjbvwHyBAoGBANd1E0ZRjMyKMBp7CiFGD/JFag6JU3Q/23PefLI6/GakDLkPEEID
2Od+2VtJJsvltlzIVOpY1UCE/QCRON/KXD7zVNZVaHqrnvZmYcWgc1wiIKvSyrAK
W0jis8K53/SvyIbdDkd+z4n3eMZKMjF/2+AYjNikSlpqaTi7zvB9jaYhAoGBAMAq
2a0699z0P0Kqf7asVa2JtiUcxxkxaNlDpLha0igx48NUR6CsH9AD7VubSgc53IAK
FDYz781GryjwuGHuMjPp2mXFwiO2QvXMTK0ReScrDoQUiAPaPH7U/CTuVt2J8z0j
W8Nay/XWJ5x8gJP0F47Ee19QE1xgzQxuqoBB7K09AoGAQPm5mlc1kumJoDLC1039
uR5d4YxgcopfcA4EpOtM+tc2TwjP6limrQmAGxtwa8UWvdxcX1/yz8ZLVkR1Vmf8
ca+IQir3mybuhXhSu/qrT3mrSKYFIhm9dbmIZI0RkQUCAEnh6IXBqOXMsl/lyy+3
61j8AMlq8uFsYgOhYL08XoECgYEArfJbxfX5xXUGCleBcZ5/k61zRhbNll1mVjxn
z0TOtPmr/PS+PY9w4H+djG19zhqvIOt+ri3HJJ6WEU4M6QCPSvSk77jZ6i+iXxKG
WabWbwEHi8F1+V7Dod8zOk7QLIshtbba6nO26hnnEzyTutmZtW7fakB2tgkdsuI9
zglertUCgYEA0ltjY4olXDY6eEdL5WvDY39gfT03+6taGYbruB1DDNHaEq92fHUZ
I/7IHd+2fobwNMT1AgnWyDSbNtWYHFqffL+lsOQqf3P6ZEIpE2AubdWh7LnD4sG2
aG+BwzHO0W6PIJH1cxq4kN1Dw4cG1e/cjQDNXAhVcf9lnv8ZLRbDmJE=
-----END RSA PRIVATE KEY-----
"""
miningMutex = threading.Lock()
try:
    with open('mempool.bin', 'rb') as f:
        txQueue = pickle.load(f)
        print("[*] mempool: opening mempool file")
except (FileNotFoundError, EOFError):
    print("[*] mempool: creating mempool file")
    txQueue = {
        "waiting_validate": [],
        "waiting": [],
        "mining": []
    }

if len(txQueue['mining']):
    print("[*] mempool: there are tx in mining queue")
if len(txQueue['waiting']):
    print("[*] mempool: there are tx in waiting queue")


def checkBalanceByOwner(address=None):
    global chain
    balance = 0
    txs = []
    for block in chain.chain:
        for merkleNode in block.merkle.Get_past_transacion():
            if isinstance(merkleNode, Transaction):
                if merkleNode.type == "create":
                    if merkleNode.tx_to.address == address:
                        txs.append(merkleNode)
                        balance += merkleNode.tx_to.value
                elif merkleNode.type == "transfer":
                    if merkleNode.tx_to.address == address:
                        txs.append(merkleNode)
                        balance += merkleNode.tx_from.value
                    elif merkleNode.tx_from.address == address:
                        txs.append(merkleNode)
                        balance -= merkleNode.tx_from.value
    return balance


def txValidate():
    global chain
    while True:
        if len(txQueue['waiting_validate']):
            printLog("txValidate", "Validating Tx")
            lookingTx = txQueue['waiting_validate'].pop(0)
            tempQueue = copy.deepcopy(txQueue)
            txsFromTemp = []
            for tx in tempQueue['mining']:
                txsFromTemp.append(tx)
            for tx in tempQueue['waiting']:
                txsFromTemp.append(tx)
            for tx in tempQueue['waiting_validate']:
                txsFromTemp.append(tx)
            balance = checkBalanceByOwner(lookingTx.tx_from.address)
            for tx in txsFromTemp:
                if tx.type == "create":
                    if tx.tx_to.address == lookingTx.tx_from.address:
                        balance += tx.tx_to.value
                elif tx.type == "transfer":
                    if tx.tx_to.address == lookingTx.tx_from.address:
                        balance += tx.tx_to.value
                    elif tx.tx_from.address == lookingTx.tx_from.address:
                        balance -= tx.tx_to.value
            if lookingTx.type == "transfer":
                if balance - lookingTx.tx_from.value >= 0:
                    txQueue['waiting'].append(lookingTx)
                    printLog("txValidate", "Tx valid, adding to queue")
                else:
                    printLog("txValidate", "Found invalid tx", "error")
            else:
                txQueue['waiting'].append(lookingTx)
                printLog("txValidate", "Tx valid, adding to queue")
        else:
            time.sleep(1)


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
    zSocket = context.socket(zmq.REP)
    zSocket.bind("tcp://*:30002")
    printLog("transactionListener", "bind complete")

    while True:
        printLog("transactionListener", "waiting for tx")
        #  Wait for next request from client
        message = zSocket.recv()
        printLog("transactionListener", "received tx")
        printLog("transactionListener", message)
        try:
            tx_in = pickle.loads(message)
            txQueue['waiting_validate'].append(tx_in)
            zSocket.send(b"OK")
            printLog("transactionListener", "received tx added to queue")
        except:
            time.sleep(1)
            zSocket.send(b"ERROR")
            printLog("transactionListener", "received tx not added to queue", "error")


def txQueueManager():
    global miningMutex
    lastTimestamp = time.time()
    while True:
        if len(txQueue['mining']) != 0:
            printLog("txQueueManager", "{} transaction already in mining queue".format(len(txQueue['mining'])))
            time.sleep(20)
        else:
            if time.time() - lastTimestamp >= 30:
                lastTimestamp = time.time()
                printLog("txQueueManager", "time passed for 10 minute and tx mining queue is blank,"
                                           " adding remain txs to queue")
                if len(txQueue['waiting']) > 0:
                    while True:
                        printLog("txQueueManager", "MUTEX1")
                        miningMutex.acquire()
                        try:
                            printLog("txQueueManager", "MUTEX2")
                            for i in range(0, 10):
                                txQueue['mining'].append(txQueue['waiting'].pop(0))
                            miningMutex.release()
                        except IndexError:
                            miningMutex.release()
                            break
                else:
                    printLog("txQueueManager", "no remain txs in queue")
                    printLog("txQueueManager", "adding dummy tx")
                    dummyTx = Transaction()
                    dummyTx.setType("create")
                    # tx.setTxFrom(address=pubkey, value="2000")
                    dummyTx.setTxTo(address="", value=0)
                    dummyTx.setTimestamp(time.time())
                    dummyTx.signSignature(privateKey=prikey)
                    dummyTx.hashTx()
                    txQueue['waiting'].append(dummyTx)
            else:
                if len(txQueue['waiting']) >= 10:
                    lastTimestamp = time.time()
                    printLog("txQueueManager", "adding txs to queue")
                    while True:
                        added = 0
                        try:
                            miningMutex.acquire()
                            for i in range(0, 10):
                                txQueue['mining'].append(txQueue['waiting'].pop(0))
                                added += 1
                            miningMutex.release()
                        except IndexError:
                            printLog("txQueueManager", "added {} txs to queue".format(added))
                            miningMutex.release()
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
                printLog("minerManager", "{} txs added to block".format(len(txQueue['mining'])))
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
            for i in range(0, 5):
                minerServer.sendto(json.dumps(stopPacket).encode(), ('<broadcast>', 30001))
                time.sleep(1)
            if len(txQueue['mining']):
                state = "mining"


def nonceListener():
    global nonceCheckQueue
    global minerServer
    global nonceListening
    minerServer.bind((socket.gethostbyname(socket.gethostname()), 30001))
    while True:
        data, addr = minerServer.recvfrom(50000)
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
printLog("Starting", "Tx Validator  thread....")
txValidateThread = threading.Thread(target=txValidate)

selfBroadcastThread.start()
transactionListenerThread.start()
txQueueManagerThread.start()
mempoolFileUpdateThread.start()
nonceListenerThread.start()
minerManagerThread.start()
txValidateThread.start()
