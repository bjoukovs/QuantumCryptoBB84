from math import floor

from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit
import random
from SimulaQron.project import helper
from SimulaQron.project.helper import messageFrom, createMessageWithSender, parseClassicalMessage


def recvClassicalVerified(sender):
    tag, msg = parseClassicalMessage(sender.recvClassical(timout=10))

    if messageFrom(tag) != "Bob":
        raise ValueError("Received unexpected tag {}".format(tag))

    print("Alice received {}".format(msg))
    return msg


def sendClassicalMessage(sender, data):
    msg = createMessageWithSender("Alice", data)
    print("Alice sending msg: {}".format(msg))
    sender.sendClassical("Eve", msg)
    # print("Alice: Did this work?")
    sender.sendClassical("Bob", msg)


def makeQubit(alice, basis, val):
    q = qubit(alice)

    if basis == 0 and val == 1:
        q.X()
    elif basis == 1 and val == 0:
        q.H()
    elif basis == 1 and val == 1:
        q.X()
        q.H()

    return q


def main():
    with CQCConnection("Alice") as Alice:
        # Number of bits for extractor
        n = 2
        # Number of qubits
        N = 4 * n

        sendClassicalMessage(Alice, N)

        # Random basis: 0 = standard, 1=hadamard
        basis = [random.randint(0, 1) for i in range(N)]

        # Qubits eigenvalues (measurement outcome)
        qubitvals = [random.randint(0, 1) for i in range(N)]

        qubits = []

        for i in range(N):
            qubit = makeQubit(Alice, basis[i], qubitvals[i])
            qubits.append(qubit)

            # sending qubit to bob
            Alice.sendQubit(qubit, "Eve")

        # Send basis to bob
        sendClassicalMessage(Alice, basis)

        # Receiving Bob basis
        bobBasis = recvClassicalVerified(Alice)
        # print("Alice received Bob's basis")
        # Comparing basis
        # print("Alice comparing bases")
        matchingBasis = helper.compareBasis(basis, bobBasis)
        print("Alice: Matching basis: {}".format(matchingBasis))

        # Alice chooses a subset of the matching basis
        k = floor(len(matchingBasis) / 2)
        sub_matchingBasis = random.sample(range(len(matchingBasis)), k)
        print("Alice: Sub matching basis: {}".format(sub_matchingBasis))
        # Sending comparing qubits and outcomes
        sendClassicalMessage(Alice, sub_matchingBasis)
        sub_matchingMeasurements = [qubitvals[matchingBasis[ind]] for ind in sub_matchingBasis]
        sendClassicalMessage(Alice, sub_matchingMeasurements)

        # Receiving Bob's measurements
        bob_measurements = recvClassicalVerified(Alice)

        # Comparing results
        error_rate = helper.compareMeasurements(bob_measurements, sub_matchingMeasurements)

        print("Alice calculated an error rate of {}".format(error_rate))


main()
