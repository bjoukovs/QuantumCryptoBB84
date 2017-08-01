#
# Copyright (c) 2017, Stephanie Wehner
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


import sys, os
sys.path.insert(0, os.environ.get('NETSIM'))

from twisted.spread import pb
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredList, Deferred

from SimulaQron.virtNode.basics import *
from SimulaQron.virtNode.quantum import *
from SimulaQron.general.hostConfig import *
from SimulaQron.virtNode.crudeSimulator import *

from SimulaQron.local.setup import *


#####################################################################################################
#
# runClientNode
#
# This will be run on the local node if all communication links are set up (to the virtual node
# quantum backend, as well as the nodes in the classical communication network), and the local classical
# communication server is running (if applicable).
#
#@inlineCallbacks
def runClientNode(qReg, virtRoot, myName, classicalNet):
	"""
	Code to execute for the local client node. Called if all connections are established.

	Arguments
	qReg		quantum register (twisted object supporting remote method calls)
	virtRoot	virtual quantum ndoe (twisted object supporting remote method calls)
	myName		name of this node (string)
	classicalNet	servers in the classical communication network (dictionary of hosts)
	"""

	logging.debug("LOCAL %s: Runing client side program.",myName)



#####################################################################################################
#
# localNode
#
# This will be run if the local node acts as a server on the classical communication network,
# accepting remote method calls from the other nodes.

class localNode(pb.Root):

	def __init__(self, node, classicalNet):

		self.node = node
		self.classicalNet = classicalNet

		self.virtRoot = None
		self.qReg = None
		self.qC = None #Maybe not the indented way

	def set_virtual_node(self, virtRoot):
		self.virtRoot = virtRoot

	def set_virtual_reg(self, qReg):
		self.qReg = qReg

	def remote_test(self):
		return "Tested!"

	# This can be called by Alice (or other clients on the classical network) to inform Bob
	# of an event.
	@inlineCallbacks
	def remote_receive_qubit(self, virtualNum,sender):

		if sender=="Bob":

			logging.debug("LOCAL %s: Getting reference to qubit number %d.",self.node.name, virtualNum)

			# Get ref of qubit
			self.qC=yield self.virtRoot.callRemote("get_virtual_ref",virtualNum)
			qC=self.qC

			#Create new qubit
			qD=yield self.virtRoot.callRemote("new_qubit_inreg",self.qReg)

			#Expand graph state
			yield qD.callRemote("apply_H")
			yield qC.callRemote("cphase_onto",qD)

			#Perform part of tau at C
			yield qC.callRemote("apply_rotation",[1,0,0],np.pi/2)
			yield qD.callRemote("apply_rotation",[0,0,1],-np.pi/2)

			# tmp=yield self.virtRoot.callRemote("get_register",qC)
			# np.save("data_R",tmp[0])
			# np.save("data_I",tmp[1])

			#send qubit D to David
			#instruct virtual node to transfer qubit
			remoteNum = yield self.virtRoot.callRemote("send_qubit",qD,"David")
			logging.debug("LOCAL %s: Remote qubit is %d.","Charlie",remoteNum)

			#Tell number of virtual qubit to Charlie and receive measurement outcome parity
			david=self.classicalNet.hostDict["David"]
			parity = yield david.root.callRemote("receive_qubit",remoteNum)

			#Measure qubit (X-basis)
			yield qC.callRemote("apply_H")
			outcome=yield qC.callRemote("measure")
			print("Charlie outcome was:", outcome)

			return (parity+outcome)%2

		elif sender=="David":

			logging.debug("LOCAL %s: Getting reference to qubit number %d.",self.node.name, virtualNum)

			# Get ref of qubit
			qE=yield self.virtRoot.callRemote("get_virtual_ref",virtualNum)
			qC=self.qC #HOW TO GET THIS REF!!!!!!!!!!!!!!!!!!!!!!!!!!!!

			# Expand graph state
			yield qE.callRemote("cphase_onto",qC)

			#Do local part of tau
			yield qE.callRemote("apply_rotation",[1,0,0],np.pi/2)
			yield qC.callRemote("apply_rotation",[0,0,1],-np.pi/2)

			#Measure extra qubit (Z-basis)
			m=yield qE.callRemote("measure")
			if m==1:
				yield qC.callRemote("apply_Z")
			return m


#####################################################################################################
#
# main
#
# This can stay the same for any example you run
#

def main():

	# In this example, we are YOURNAME
	myName = "Charlie"


	# This file defines the network of virtual quantum nodes
	virtualFile = os.environ.get('NETSIM') + "/config/virtualNodes.cfg"

	# This file defines the nodes acting as servers in the classical communication network
	classicalFile = os.path.join(os.path.dirname(__file__), 'classicalNet.cfg')

	# Read configuration files for the virtual quantum, as well as the classical network
	virtualNet = networkConfig(virtualFile)
	classicalNet = networkConfig(classicalFile)

	# Check if we should run a local classical server. If so, initialize the code
	# to handle remote connections on the classical communication network
	if myName in classicalNet.hostDict:
		lNode = localNode(classicalNet.hostDict[myName], classicalNet)
	else:
		lNode = None

	# Set up the local classical server if applicable, and connect to the virtual
	# node and other classical servers. Once all connections are set up, this will
	# execute the function runClientNode
	setup_local(myName, virtualNet, classicalNet, lNode, runClientNode)

##################################################################################################
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
main()

