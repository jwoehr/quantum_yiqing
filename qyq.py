# qyq.py
import sys

usage = "Usage: " + sys.argv[0] + """ [-h] [--help] [sim]
... -h or --help give help (long)
... if sim is present, use simulator, otherwise real processor
"""

explanation  = """# Quantum Yi Qing
# Casts the Yi Qing oracle.

# Traditionally done with yarrowstalks in an intricate procedure to guarantee
# that the Tao is governs the cast. In the West with our somewhat dryer notion
# of randomicity, it is case by six 3-coin tosses representing each of 6 lines
# of the hexagram and the 6 lines of the derivative hexagram.
#
# A "heads" toss is a 3. A "tails" is a 2. The 3 coins are summed and the lines,
# Yang (solid) and Yin (broken) of the primary hexagram formed from the sums,
# bottom (line 1) to top (line 6) according to these rules:
#
#	6 - Yin changing
#	7 - Yang unchanging
#	8 - Yin unchanging
#	9 - Yang changing
#
# The derivative hexagram is formed from the identical lines, however any
# "changing" line is the inverse line in the derivative hexagram.
#
# In the program, the lines of the primary hexagram are represented as follows:
#
#	*X* - Yin changing
#	*** - Yang unchanging
#	* * - Yin unchanging
#	*0* - Yang changing
#
# In the derivative hexagram, the "changing" notion is abstracted and the
# hexagram stands as calculated per above.
#
# The quantum program uses 3 qubits and Hadamards them into superposition.
#
# For the purpose of the oracle, a 1-bit counts as 3 and a 0-bit as 2.
#
# The most-measured classical 3-bit value that emerges from 1024 shots is
# the winning 3-coin toss for that line of the hexagram,
#
# As modelled in qasm:
#
# include "qelib1.inc";
# qreg q[5];
# creg c[5];
#
# h q[0];
# h q[1];
# h q[2];
# measure q[0] -> c[0];
# measure q[1] -> c[1];
# measure q[2] -> c[2];
#
# If two classical bit patterns emerge with identical frequency, the conflict
# is resolved as follows:
#
#	identical sum	- don't care
#	6 vs 7			- 7
#	6 vs 8			- 8
#	6 vs 9			- 6
#	7 vs 8			- 8
#	7 vs 9			- 9
#	8 vs 9			- 9


#
# If more than two classical bit patterns emerge with identical frequency, only
# the first and last are considered.
"""

# By default, use the real Q processor.
sim = False

if len(sys.argv) > 1:
	if (sys.argv[1] == "-h") or (sys.argv[1] == "--help"):
		print(usage)
		print(explanation)
		exit()
	elif (sys.argv[1] == "sim"):
		sim = True
	else:
		print("Unknown argument " + sys.argv[1])
		print(usage)
		exit()

print("""QUANTUM YI QING - Cast a Yi Qing Oracle using IBM Q for the cast.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WIHTOUT ANY EXPRESS OR IMPLIED WARRANTIES.
""")

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from pylab import *

# Create a Quantum Register with 3 qubits.
q = QuantumRegister(3, 'q')

# Create a Quantum Circuit acting on the q register
circ = QuantumCircuit(q)

# Add a H gate on qubit 0, putting this qubit in superposition.
circ.h(q[0])
circ.h(q[1])
circ.h(q[2])

print(circ.draw())

# Create a Classical Register with 3 bits.
c = ClassicalRegister(3, 'c')
# Create a Quantum Circuit
meas = QuantumCircuit(q, c)
meas.barrier(q)
# map the quantum measurement to the classical bits
meas.measure(q,c)

# The Qiskit circuit object supports composition using
# the addition operator.
qc = circ+meas

#drawing the circuit
print(qc.draw())

from qiskit import IBMQ
IBMQ.load_accounts()

from qiskit.providers.ibmq import least_busy

large_enough_devices = IBMQ.backends(filters=lambda x: x.configuration().n_qubits > 4 and
                                                      not x.configuration().simulator)

backend = least_busy(large_enough_devices)
print("The best backend is " + backend.name())

from qiskit.tools.monitor import job_monitor
shots = 1024           # Number of shots to run the program (experiment); maximum is 8192 shots.
max_credits = 3        # Maximum number of credits to spend on executions.

import qyqhex as qh
h = qh.QYQHexagram()

for i in range(0,6):
	job_exp = execute(qc, backend=backend, shots=shots, max_credits=max_credits)
	job_monitor(job_exp)

	result_exp = job_exp.result()

	counts_exp = result_exp.get_counts(qc)
	print(counts_exp)
	sorted_keys = sorted(counts_exp.keys())
	sorted_counts = {}
	for i in sorted_keys:
		sorted_counts[i]=counts_exp[i]

	print(sorted_counts)
	h.add(qh.QYQLine.interp(counts_exp))
	h.draw(True) # draw reversed

print('Done!')
# End
