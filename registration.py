
import time
from transaction import Transaction

while 1 :
    registration_id = input("Enter your registration ID:")
    if(registration_id.isnumeric() and 1<=int(registration_id)<=3):
        break
while 1 :
    student_id = input("Enter your student ID:")
    if(student_id.isnumeric() and len(student_id) == 11):
        break

public_S = open("./keys/voter/{}/public.pem".format(student_id,student_id),"r")
pub_S = public_S.read()

private_R = open("./keys/registration/{}/private.pem".format(registration_id,registration_id),"r")
public_R = open("./keys/registration/{}/public.pem".format(registration_id,registration_id),"r")
pk_R = private_R.read()
pub_R = public_R.read()

def createTx(pk_R,pub_R,pub_S):

    tx = Transaction()
    tx.setType("create")
    tx.setTxFrom(address=pub_R, value="2000")
    tx.setTxTo(address=pub_S, value="2000")
    tx.setTimestamp(16211767050)
    tx.signSignature(privateKey=pk_R)
    tx.hashTx()

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