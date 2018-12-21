def compareBasis(basisA, basisB):
    # Returns a list of matching basis indices

    
    indices = [i for i in range(len(basisA)) if basisA[i]==basisB[i]]
    return indices