import pickle
from transaction import Transaction
from merkle import MerkleTree
from block import Block

with open('../data.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    data = pickle.load(f)
    print(data.merkle.Get_Root_leaf())