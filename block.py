class Block:
    def __init__(self, _id, prevBlockHash, timestamp, difficulty, merkle, nonce=None):
        self.id = _id
        self.prevBlock = prevBlockHash
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.nonce = nonce
        self.merkle = merkle

    def mine(self):
        pass
