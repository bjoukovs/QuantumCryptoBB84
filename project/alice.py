#
# Copyright (c) 2017, Stephanie Wehner and Axel Dahlberg
#           (c) 2019, Andrew Jiang, Boris Joukovsky, Olivier Maas, Antal Szava
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. All advertising materials mentioning features or use of this software
#    must display the following acknowledgement:
#    This product includes software developed by Stephanie Wehner, QuTech.
# 4. Neither the name of the QuTech organization nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import random
from math import floor

from SimulaQron.cqc.pythonLib.cqc import CQCConnection, qubit
from SimulaQron.project import extractor
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

        # Send out how many qubits will be used
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

            # Wait for Bob to send an acknowledgement before proceeding
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
