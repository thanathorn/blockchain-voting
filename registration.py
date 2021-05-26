import json
import pickle
import socket
import time
import requests
import zmq

from helper import printLog
from transaction import Transaction

masterIP = "127.0.0.1"
clear = lambda: print('\n' * 100)
registration_id = 0


def masterAddressListener():
    global masterIP
    masterServerAddrSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    masterServerAddrSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    masterServerAddrSocket.bind((socket.gethostbyname(socket.gethostname()), 30003))
    while True:
        data, addr = masterServerAddrSocket.recvfrom(50000)
        try:
            incoming_data = json.loads(data)
            masterIP = incoming_data['address']
            break
        except:
            pass


def createTx(pk_R, pub_R, pub_S):
    questions = requests.get('http://127.0.0.1:8000/master/voter/question')
    questions = questions.json()
    totalGiveaway = 0
    for question in questions:
        totalGiveaway += question['question']['vote_accepted']
    tx = Transaction()
    tx.setType("transfer")
    tx.setTxFrom(address=pub_R, value=totalGiveaway)
    tx.setTxTo(address=pub_S, value=totalGiveaway)
    tx.setTimestamp(time.time())
    tx.signSignature(privateKey=pk_R)
    tx.hashTx()
    return tx


def broadcastTx(tx):
    wait = 0
    while masterIP == "127.0.0.1":
        wait += 1
        time.sleep(1)
        if wait == 30:
            printLog("Registration", "Failed to register", "error")
            return False

    context = zmq.Context()
    #  Socket to talk to server
    print("Connecting to master server…")
    connSocket = context.socket(zmq.REQ)
    connSocket.connect("tcp://{}:30002".format(masterIP))

    txString = pickle.dumps(tx)

    printLog("Registration", "Sending a registration request to master server")
    connSocket.send(txString)

    #  Get the reply.
    message = connSocket.recv()
    connSocket.close()
    if "OK".encode() in message:
        printLog("Registration", "Successfully registered!")
    else:
        printLog("Registration", "Registration fail!", "error")


def main():
    global registration_id
    while True:
        student_id = input("Enter your student ID:")
        if student_id.isnumeric() and len(student_id) == 11:
            break

    url = "http://{}:8000/master/registration/student".format(masterIP)
    payload = {'student_id': student_id}
    files = []
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    if not response.json()['already_get_credit']:
        public_S = open("./keys/voter/{}/public.pem".format(student_id, student_id), "r")
        pub_S = public_S.read()

        private_R = open("./keys/registration/{}/private.pem".format(registration_id, registration_id), "r")
        public_R = open("./keys/registration/{}/public.pem".format(registration_id, registration_id), "r")
        pk_R = private_R.read()
        pub_R = public_R.read()

        printLog("Registration", "Verifying...")
        tx = createTx(pk_R, pub_R, pub_S)
        broadcastTx(tx)
        time.sleep(1)
        print("Success Registration, your account will be ready to vote soon!")
    else:
        print("You're already complete with this process before")

    time.sleep(5)


if __name__ == '__main__':
    printLog("Registration", "Starting...")
    masterAddressListener()
    while True:
        registration_id = input("Enter your registration ID:")
        if registration_id.isnumeric() and 1 <= int(registration_id) <= 3:
            break
    while True:
        clear()
        main()
