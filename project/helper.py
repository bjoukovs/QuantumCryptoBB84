def compareBasis(basisA, basisB):
    # Returns a list of matching basis indices

    print("Basis A: {}; Basis B: {}".format(basisA, basisB))
    indices = [i for i in range(len(basisA)) if basisA[i]==basisB[i]]
    return indices


def compareMeasurements(measA, measB):
    #returns the error rate

    N = len(measA)
    results = [int(measA[i]!=measB[i]) for i in range(N)]
    errors = sum(results)

    error_rate = errors/N

    return error_rate

def createMessageWithTag(tag, data):
    try:
        return [tag, int(data)]
    except TypeError:
        print("Sending data: {} with tag {}".format(data, tag))
        out = data.copy()
        out.insert(0, tag)
        return out

def createMessageWithSender(sender, data):
    tag = -1
    if sender == 'Alice':
        tag = 0
    elif sender == 'Bob':
        tag = 1

    return createMessageWithTag(tag, data)

def parseClassicalMessage(msg):
    message_list = list(msg)
    return (message_list[0], message_list[1:])

def messageFrom(tag):
    if tag == 0:
        return "Alice"
    elif tag == 1:
        return "Bob"
    else:
        return "Unknown"