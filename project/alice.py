from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit
import random
from SimulaQron.project import helper


def makeQubit(alice, basis, val):

    qubit = qubit(alice)

    if basis==0 and val==1:
        qubit.X()
    elif basis==1 and val==0:
        qubit.H()
    elif basis==1 and val==1:
        qubit.X()
        qubit.H()
    
    return qubit


def main():
    with CQCConnection("Alice") as alice:
        

        #Number of bits for extractor
        n = 10
        #Number of qubits
        N = 4*n

        alice.sendClassical("Eve", N, timout=10)

        #Random basis: 0 = standard, 1=hadamard
        basis = [random.randint(0,1) for i in range(N)]

        #Qubits eigenvalues (measurement outcome)
        qubitvals = [random.randint(0,1) for i in range(N)]

        qubits = []


        for i in range(N):

            qubit = makeQubit(alice, basis[i], qubitvals[i])
            qubits.append(qubit)

            #sending qubit to bob
            alice.sendQubit(qubit, "Eve")



        # Send basis to bob
        alice.sendClassical("Eve", basis, 10)

        #Receiving Bob basis
        bobBasis = alice.recvClassical(timout=10)

        #Comparing basis
        matchingBasis = helper.compareBasis(basis, bobBasis)


        #Alice chooses a subset of the matching basis
        k = floor(len(matchingBasis/2))
        sub_matchingBasis = random.sample(range(len(matchingBasis)), k)

        #Sending comparing qubits and outcomes
        alice.sendClassical("Eve", sub_matchingBasis)
        alice.sendClassical("Eve", [qubitvals[ind] for ind in sub_matchingBasis])

        #Receiving Bob's measurements
        bob_measurements = alice.recvClassical(timout=10)


        #Comparing results
        error_rate = helper.compareMeasurements(bob_measurements, [qubitvals[ind] for ind in sub_matchingBasis])









        

main()