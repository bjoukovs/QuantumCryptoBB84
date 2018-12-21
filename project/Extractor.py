import random

class Extractor():

    def __init__(seed=0)
        self.seed = seed

    
    def encode(self,message)

        key = None

        if len(message)==len(self.seed):
            andlist = [bool(message[i]) and bool(self.seed[i]) for i in range(len(message))]
            key = sum(andlist)%2
        else:
            raise("Error: seed is not the same size as the message")

        return key


    def set_seed(self, seed):
        self.seed = seed

    def get_seed(self):
        return seld.seed
    
    def generate_seed(self, N):
        self.seed = [random.randint(0,1) for i in range(N)]