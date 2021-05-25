import socket
import time
import requests
from transaction import Transaction

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
server.settimeout(0.2)
server.bind(("", 30002))

clear = lambda: print('\n'*100)
choose = []

def createTx(pub,pk):
    i = 0
    tx = []
    for question in temp_var:
        select = choose[i]
        if(question == int (select)-1):
            address = question['answers']['address']
            tx2 = Transaction()
            tx2.setType("transfer")
            tx2.setTxFrom(address=pub, value="2000")
            tx2.setTxTo(address=address, value="2000")
            tx2.setTimestamp(16211767050)
            tx2.signSignature(privateKey=pk)
            tx2.hashTx()
            tx.append(tx2)
        i = i+1
    return tx


def broadcastTx(tx):
    context = zmq.Context()

    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:30002")

    my_pickle_string = pickle.dumps(tx)
    # print(my_pickle_string)

    #  Do 10 requests, waiting each time for a response
    print("Sending request")
    socket.send(my_pickle_string)

    #  Get the reply.
    message = socket.recv()
    print("Received reply [ %s ]" % (message))
    time.sleep(1)

student_id = input("Enter your student ID: ")
private = open("./keys/voter/{}/private.pem".format(student_id,student_id),"r")
public = open("./keys/voter/{}/public.pem".format(student_id,student_id),"r")
pk = private.read()
pub = public.read()


clear()
j = 1

temp = requests.get('http://127.0.0.1:8000/master/voter/question')
temp_var = temp.json()

for question in temp_var:
    i = 0
    print("Question {} : {}".format(j,question['question']['question']))
    for ans in question['answers']:
        print ("{}. {}".format(i+1,ans['answer']))
        i = i+1
    j = j + 1
    while 1:
        checkinput = input("Enter your choice:")
        if(checkinput.isnumeric() and int(checkinput) <= i and int(checkinput) > 0):
            break
    choose.append(checkinput)
    clear()
print('เสร็จแล้วจ้า')
