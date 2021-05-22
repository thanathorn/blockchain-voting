import pickle


class Blockchain:
    def __init__(self):
        self.chain = pickle.load(open("blockchain.bin", 'rb'))

    @property
    def last_block(self):
        return self.chain[-1]


