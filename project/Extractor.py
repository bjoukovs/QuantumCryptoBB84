import random

class Extractor():

    def __init__(seed=None)
        self.seed = seed

    
    def extract(self, bits)

        key = None

        if len(bits)==len(self.seed):
            andlist = [bool(bits[i]) and bool(self.seed[i]) for i in range(len(bits))]
            key = sum(andlist)%2
        else:
            raise("Error: seed is not the same size as the bit string")

        return key


    def set_seed(self, seed):
        self.seed = seed

    def get_seed(self):
        return self.seed
    
    def generate_seed(self, N):
        self.seed = [random.randint(0,1) for i in range(N)]