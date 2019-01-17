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

from SimulaQron.cqc.pythonLib.cqc import CQCConnection
from SimulaQron.project import extractor
from SimulaQron.project import helper
#####################################################################################################
#
# main
#
from SimulaQron.project.helper import parseClassicalMessage, messageFrom, createMessageWithSender


def recvClassicalVerified(sender):
    tag, msg = parseClassicalMessage(sender.recvClassical(timout=10))

    if messageFrom(tag) != "Alice":
        raise ValueError("Received unexpected tag {}".format(tag))

    print("Bob received {}".format(msg))
    return msg


def sendClassicalMessage(sender, data):
    msg = createMessageWithSender("Bob", data)
    sender.sendClassical("Eve", msg)
    # print("Bob: Did this work?")
    sender.sendClassical("Alice", msg)


def main():
    # Initialize the connection
    with CQCConnection("Bob") as Bob:
        N = recvClassicalVerified(Bob)[0]

        # Random basis: 0 = standard, 1=hadamard
        basis = [random.randint(0, 1) for i in range(N)]

        # Qubits eigenvalues (measurement outcome)
        measurements = []

        for i in range(0, N):
            # Receive qubit from Alice (via Eve)
            q = Bob.recvQubit()

            if basis[i] == 1:
                # Apply Hadamard to put it into standard basis for measurement
                q.H()

            # Retreive key
            measurements.append(q.measure())

            # Send acknowledgement to Alice
            sendClassicalMessage(Bob, 1)

        # print("Bob receiving Alice's basis")
        alice_basis = recvClassicalVerified(Bob)
        matching_basis = helper.compareBasis(alice_basis, basis)
        print("Bob: Matching basis: {}".format(matching_basis))

        print("Bob: Sending measurements to Alice")
        sendClassicalMessage(Bob, basis)

        sub_matching_basis_indices = recvClassicalVerified(Bob)

        alice_measurements = recvClassicalVerified(Bob)

        sub_matching_basis = [matching_basis[ind] for ind in sub_matching_basis_indices]
        if set(sub_matching_basis).issubset(set(matching_basis)):
            sub_matching_measurements = [measurements[matchingIndex] for matchingIndex in sub_matching_basis]
            sendClassicalMessage(Bob, sub_matching_measurements)
            error_rate = helper.compareMeasurements(sub_matching_measurements, alice_measurements)

            print("Bob calculated an error rate of {}".format(error_rate))

            # Since we assume a noise-free channel, error rate > 0 == Eve is present
            if error_rate > 0:
                print("Bob: Error rate above 0; Abort!")
                return

            alice_seed = recvClassicalVerified(Bob)
            print("Bob received the seed {} from Alice".format(alice_seed))

            # Bob uses the seed sent by Alice and an extractor to generate one bit of key as well
            bob_extractor = extractor.Extractor()
            bob_extractor.set_seed(alice_seed)
            key = bob_extractor.extract(sub_matching_basis)

            print("Bob generated the key {}".format(key))
        else:
            print(
                "Bases Alice sent is not a subset of valid bases!\n Received basis: {};\nSet of valid bases:{}\n".format(
                    sub_matching_basis, matching_basis))


##################################################################################################
main()
