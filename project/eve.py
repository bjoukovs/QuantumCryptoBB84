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
from SimulaQron.project.helper import parseClassicalMessage, messageFrom


def main(intercept=False):
    # Initialize the connection
    with CQCConnection("Eve") as Eve:

        if intercept:
            print("Warning: Eve is measuring the qubits (random basis mode)!")

        # Eve eveasdrops on the classical authenticated channel:
        # Intercepted the number of qubits sent by Alice
        tag, msg = parseClassicalMessage(Eve.recvClassical(timout=10))
        print('Eve intercepted the following message (1) : {}', msg)

        if messageFrom(tag) == "Alice":
            N = msg[0]

            # Eavesdropping
            if intercept:
                meas_basis = [random.randint(0, 1) for i in range(N)]
                measurements = []

            # Eve.sendClassical("Bob", createMessageWithTag(tag, N))
            for i in range(0, N):
                # Receive qubit from Alice
                q = Eve.recvQubit()

                # Eve attack: measuring the qubit
                if intercept:
                    if meas_basis[i] == 1:
                        q.H()
                        measurements.append(q.measure(inplace=True))
                        q.H()
                    else:
                        measurements.append(q.measure(inplace=True))

                # Forward the qubit to Bob
                Eve.sendQubit(q, "Bob")

                # Eve eaveasdrops on the classical authenticated channel:
                # Intercepted the confirmation messages from Bob that he received the qubits sent by Alice
                tag, msg = parseClassicalMessage(Eve.recvClassical(timout=10))
                print('Eve intercepted the following message (2) : {}', msg)

        else:
            print("Something went wrong! Alice didn't send qubits!")

        # Eve eveasdrops on the classical authenticated channel:
        # Intercepted the basis for the qubits
        tag, msg = parseClassicalMessage(Eve.recvClassical(timout=10))
        print('Eve intercepted the following message (3) : {}', msg)

        # Intercepted the subset of matching basis
        tag, msg = parseClassicalMessage(Eve.recvClassical(timout=10))
        print('Eve intercepted the following message (4) : {}', msg)

        # Intercepted the matching basis to be compared
        tag, msg = parseClassicalMessage(Eve.recvClassical(timout=10))
        print('Eve intercepted the following message (5) : {}', msg)

        # Intercepted the outcomes for the matching basis to be compared
        tag, msg = parseClassicalMessage(Eve.recvClassical(timout=10))
        print('Eve intercepted the following message (6) : {}', msg)

        tag, msg = parseClassicalMessage(Eve.recvClassical(timout=10))
        print('Eve intercepted the following message (7): {}', msg)

        # Intercepted the seed for the extractor
        tag, msg = parseClassicalMessage(Eve.recvClassical(timout=10))
        print('Eve intercepted the following message (8): {}', msg)


##################################################################################################
main(intercept=False)
