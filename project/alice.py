from math import floor

from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit
import random
from SimulaQron.project import helper
from SimulaQron.project.helper import messageFrom, createMessageWithSender, parseClassicalMessage

from SimulaQron.project import extractor

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

    if val == 1:
        q.X()
    if basis == 1:
        q.H()

    return q


def main():
    with CQCConnection("Alice") as Alice:
        # Number of bits for extractor
        n = 10
        # Number of qubits
        N = 4 * n

        #if N>32:
        #    print("Warning: N>32 exceeds the quantum messages buffer. Qubit transmission enters acknowledgement mode to prevent this issue.")
        Alice.name
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

            #If N>32, waits for bob acknoledgment to avoid exceeding the qubit buffer limit of 32 at Eve's side
            #if N>32:
            ack = recvClassicalVerified(Alice)

        # Send basis to bob
        sendClassicalMessage(Alice, basis)

        # Receiving Bob basis
        bob_basis = recvClassicalVerified(Alice)
        # print("Alice received Bob's basis")
        # Comparing basis and storing indices of the same basis
        # print("Alice comparing bases")
        matching_basis = helper.compareBasis(basis, bob_basis)
        print("Alice: Matching basis: {}".format(matching_basis))

        # Alice chooses a subset of the matching basis and stores their indices
        k = floor(len(matching_basis) / 2)
        sub_matching_basis = random.sample(range(len(matching_basis)), k)
        print("Alice: Sub matching basis: {}".format(sub_matching_basis))
        # Sending comparing qubits and outcomes
        sendClassicalMessage(Alice, sub_matching_basis)
        sub_matching_measurements = [qubitvals[matching_basis[ind]] for ind in sub_matching_basis]
        sendClassicalMessage(Alice, sub_matching_measurements)

        # Receiving Bob's measurements
        bob_measurements = recvClassicalVerified(Alice)

        # Comparing results
        error_rate = helper.compareMeasurements(bob_measurements, sub_matching_measurements)

        print("Alice calculated an error rate of {}".format(error_rate))

        # Since we assume a noise-free channel, error rate > 0 == Eve is present
        if error_rate > 0:
            print("Alice: Error rate above 0; Abort!")
            return

        # Alice picks an extractor for one bit of key using the subset of the matching basis
        alice_extractor = extractor.Extractor()
        alice_extractor.generate_seed(len(sub_matching_basis))
        key = alice_extractor.extract(sub_matching_basis)

        # Send the extracted seed to Bob
        sendClassicalMessage(Alice, alice_extractor.get_seed())
        print("Alice extracted one bit of key: {} and sent its seed to Bob".format(key))

main()
