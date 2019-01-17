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

def compareBasis(basisA, basisB):
    # Returns a list of matching basis indices

    print("Basis A: {}; Basis B: {}".format(basisA, basisB))
    indices = [i for i in range(len(basisA)) if basisA[i] == basisB[i]]
    return indices


def compareMeasurements(measA, measB):
    # returns the error rate

    N = len(measA)
    results = [int(measA[i] != measB[i]) for i in range(N)]
    errors = sum(results)

    error_rate = errors / N

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
