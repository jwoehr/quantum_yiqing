# qyq.py ... Main script. Run and render.
# QUANTUM YI QING - Cast a Yi Qing Oracle using IBM Q for the cast.
# Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
# BSD-3 license -- See LICENSE which you should have received with this code.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

import qyqhex as qh
from qiskit.tools.monitor import job_monitor
from qiskit import execute
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import numpy as np
import argparse
import sys
explanation = """QUANTUM YI QING - Cast a Yi Qing Oracle using IBM Q for the cast.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
"""

long_explanation = """QUANTUM YI QING - Cast a Yi Qing Oracle using IBM Q for the cast.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

Default is to run on genuine IBM Q quantum processor.

Default is to assume the user has stored an IBM Q account identity token
which can be retrieved by qiskit.IBMQ.load_accounts(). Alternatively, the
token can be provided via the -i --identity switch. Additionally, the
--url switch can provide a specific url.

Type -h or --help for important options information.

Traditionally done with yarrowstalks in an intricate procedure to guarantee
that the Tao is governs the cast. In the West with our somewhat dryer notion
of randomicity, it is case by six 3-coin tosses representing each of 6 lines
of the hexagram and the 6 lines of the derivative hexagram.

A "heads" toss is a 3. A "tails" is a 2. The 3 coins are summed and the lines,
Yang (solid) and Yin (broken) of the primary hexagram formed from the sums,
bottom (line 1) to top (line 6) according to these rules:

    6 - Yin changing
    7 - Yang unchanging
    8 - Yin unchanging
    9 - Yang changing

The derivative hexagram is formed from the identical lines, however any
"changing" line is the inverse line in the derivative hexagram.

In the program, the lines of the primary hexagram are represented as follows:
    ***XXX*** - Yin changing
    ********* - Yang unchanging
    ***   *** - Yin unchanging
    ***000*** - Yang changing

In the derivative hexagram, the "changing" notion is abstracted and the
hexagram stands as calculated per above.

The quantum program uses 6 qubits and puts them by pairs in a Bell state, e.g.,
h q[0];
cx q[0],q[1];
x q[0];

It measures the entangled bits q[1], q[3], q[5].

For the purpose of the oracle, a 1-bit counts as 3 and a 0-bit as 2.

The most-measured classical 3-bit value that emerges from 1024 shots is
the winning 3-coin toss for that line of the hexagram,

The quantum computation in qasm (see the --qasm switch):

OPENQASM 2.0;
include "qelib1.inc";
qreg q[6];
creg c[3];
h q[0];
h q[2];
h q[4];
cx q[0],q[1];
cx q[2],q[3];
cx q[4],q[5];
x q[0];
x q[2];
x q[4];
barrier q[0],q[1],q[2],q[3],q[4],q[5];
measure q[1] -> c[0];
measure q[3] -> c[1];
measure q[5] -> c[2];

If two classical bit patterns emerge with identical frequency, the conflict
is resolved as follows:

    identical sum    - don't care
    6 vs 7            - 7
    6 vs 8            - 8
    6 vs 9            - 6
    7 vs 8            - 8
    7 vs 9            - 9
    8 vs 9            - 9

If more than two classical bit patterns emerge with identical frequency, only
the first and last are considered.

At the end all counts are printed in CSV format, in toss order.
At present, this feature does not work correctly when all possible outcomes do not occur at least once.
In particular, it does not work correctly with the Aer state vector simulator.
"""

parser = argparse.ArgumentParser(description=explanation)
group = parser.add_mutually_exclusive_group()
group.add_argument("-q", "--ibmq", action="store_true",
                   help="Use genuine IBMQ processor (default)")
group.add_argument("-s", "--sim", action="store_true",
                   help="Use IBMQ qasm simulator")
group.add_argument("-a", "--aer", action="store_true",
                   help="User QISKit aer simulator")
parser.add_argument("-b", "--backend", action="store",
                    help="""genuine qpu backend to use, default is least busy
                    of large enough devices""")
parser.add_argument("-d", "--drawcircuit", action="store_true",
                    help="Draw the circuit in extended charset")
parser.add_argument("-i", "--identity", action="store",
                    help="IBM Q Experience identity token")
parser.add_argument("-m", "--max_credits", type=int, action="store", default=3,
                    help="max credits to expend, default is 3")
parser.add_argument("--qasm", action="store_true",
                    help="Show the qasm for the circuit")
parser.add_argument("--shots", type=int, action="store", default=1024,
                    help="number of execution shots, default is 1024")
parser.add_argument("--url", action="store", default='https://quantumexperience.ng.bluemix.net/api',
                    help="URL, default is https://quantumexperience.ng.bluemix.net/api")
parser.add_argument("-u", "--usage", action="store_true",
                    help="Show long usage message and exit 0")

args = parser.parse_args()

if args.usage:
    print(long_explanation)
    exit(0)

# Create a Quantum Register with 6 qubits.
q = QuantumRegister(6, 'q')

# Create a Quantum Circuit acting on the q register
circ = QuantumCircuit(q)

# Generate Bell state
circ.h(q[0])
circ.h(q[2])
circ.h(q[4])

circ.cx(q[0], q[1])
circ.cx(q[2], q[3])
circ.cx(q[4], q[5])

circ.x(q[0])
circ.x(q[2])
circ.x(q[4])

# drawing the circuit
if args.drawcircuit:
    print(circ.draw())

# Create a Classical Register with 3 bits.
c = ClassicalRegister(3, 'c')

# Create a Quantum Circuit
meas = QuantumCircuit(q, c)
meas.barrier(q)

# map the quantum measurement to the classical bits
meas.measure(q[1], c[0])
meas.measure(q[3], c[1])
meas.measure(q[5], c[2])

# The Qiskit circuit object supports composition using
# the addition operator.
qc = circ + meas

# show qasm
if args.qasm:
    print(qc.qasm())

# drawing the circuit
if args.drawcircuit:
    print(qc.draw())

# Choose backend
backend = None

if args.aer:
    # Import Aer
    from qiskit import BasicAer
    # Run the quantum circuit on a statevector simulator backend
    backend = BasicAer.get_backend('statevector_simulator')
else:
    from qiskit import IBMQ
    if args.identity:
        IBMQ.enable_account(args.identity, url=args.url)
    else:
        IBMQ.load_accounts()

    # Choose backend and connect
    if args.sim:
        backend = IBMQ.get_backend('ibmq_qasm_simulator')
    else:
        if args.backend:
            backend = IBMQ.get_backend(args.backend)
        else:
            from qiskit.providers.ibmq import least_busy
            large_enough_devices = IBMQ.backends(filters=lambda x: x.configuration().n_qubits > 5
                                                 and not x.configuration().simulator)
            backend = least_busy(large_enough_devices)
            print("The best backend is " + backend.name())

print("Backend is", end=" ")
print(backend)

if backend == None:
    print("No backend available, quitting.")
    exit(100)

# Prepare job

# Prepare to render
h = qh.QYQHexagram(backend)

# Loop running circuit and measuring.
# Each complete run provides the bit dictionary for one line.
for i in range(0, 6):
    job_exp = execute(qc, backend=backend, shots=args.shots,
                      max_credits=args.max_credits)
    job_monitor(job_exp)

    result_exp = job_exp.result()

    counts_exp = result_exp.get_counts(qc)
    print(counts_exp)
    sorted_keys = sorted(counts_exp.keys())
    sorted_counts = {}
    for i in sorted_keys:
        sorted_counts[i] = counts_exp[i]

    print(sorted_counts)

    h.assimilate(counts_exp)
    h.draw(True)  # draw reversed

print("CSV of run:")
print(h.csv())

print('Done!')

# End
