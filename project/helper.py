def compareBasis(basisA, basisB):
    # Returns a list of matching basis indices


    indices = [i for i in range(len(basisA)) if basisA[i]==basisB[i]]
    return indices


def compareMeasurements(measA, measB):
    #returns the error rate

    N = len(measA)
    results = [int(measA[i]==measB[i]) for i in range(N)]
    errors = sum(results)

    error_rate = errors/N

    return error_rate