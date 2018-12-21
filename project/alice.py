from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit
import random


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
        
        #Number of qubits
        N = 10

        alice.sendClassical("Eve", N, close_after=True, timeout=10)

        #Random basis: 0 = standard, 1=hadamard
        basis = [random.randint(0,1) for i in range(N)]

        #Qubits eigenvalues (measurement outcome)
        qubitvals = [random.randint(0,1) for i in range(N)]

        #Qubits
        qubits = []

        for i in range(N):

            qubit = makeQubit(alice, basis[i], qubitvals[i])







        

main()