#
# Copyright (c) 2017, Stephanie Wehner and Axel Dahlberg
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
from time import sleep

from SimulaQron.cqc.pythonLib.cqc import CQCConnection
from SimulaQron.project import helper
import random
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

        # print("Bob receiving Alice's basis")
        alice_basis = recvClassicalVerified(Bob)
        matchingBasis = helper.compareBasis(alice_basis, basis)
        print("Bob: Matching basis: {}".format(matchingBasis))

        print("Bob: Sending measurements to Alice")
        sendClassicalMessage(Bob, basis)

        sub_matchingBasis_indices = recvClassicalVerified(Bob)

        alice_measurements = recvClassicalVerified(Bob)

        sub_matchingBasis = [matchingBasis[ind] for ind in sub_matchingBasis_indices]
        if set(sub_matchingBasis).issubset(set(matchingBasis)):
            sub_matchingMeasurements = [measurements[matchingIndex] for matchingIndex in sub_matchingBasis]
            sendClassicalMessage(Bob, sub_matchingMeasurements)
            error_rate = helper.compareMeasurements(sub_matchingMeasurements, alice_measurements)

            print("Bob calculated an error rate of {}".format(error_rate))
        else:
            print(
                "Bases Alice sent is not a subset of valid bases!\n Received basis: {};\nSet of valid bases:{}\n".format(
                    sub_matchingBasis, matchingBasis))


##################################################################################################
main()
