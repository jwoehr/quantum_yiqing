"""qyq.py ... Main script. Run and render.
QUANTUM YI QING - Cast a Yi Qing Oracle using IBM Q for the cast.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES."""

import argparse
import sys

from qiskit.converters import circuit_to_dag
from qiskit.tools.monitor import job_monitor
from qiskit import (IBMQ, execute, QuantumCircuit,
                    ClassicalRegister, QuantumRegister)

import qyqhex as qh

EXPLANATION = """QUANTUM YI QING - Cast a Yi Qing Oracle using IBM Q for the cast.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
"""

LONG_EXPLANATION = """QUANTUM YI QING - Cast a Yi Qing Oracle using IBM Q for the cast.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

Default is to run on genuine IBM Q quantum processor.

Default is to assume the user has stored an IBM Q account identity token
which can be retrieved by qiskit.IBMQ.load_accounts(). Alternatively, the
token can be provided via the -i --identity switch. Additionally, the
--url switch can provide a specific url.

Quantum Inspire (https://www.qutech.nl/) simulator is also supported.

Default for QI is to assume the user has stored a QI account identity token
as explained on the Quantum Inspire SDK GitHub page
(https://github.com/QuTech-Delft/quantuminspire). Alternatively, the token can
be provided via the -i --identity switch.

To use QI support you must also have installed the Quantum Inspire SDK.

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

The inline quantum program uses 6 qubits and puts them by pairs in a Bell state:
h q[0];
cx q[0],q[1];
x q[0];

It measures the entangled bits q[1], q[3], q[5].

You may alternatively provide via the -f switch  a QASM file returning three
classical bits. This will be used instead of the inline program.

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
At present, this feature does not work correctly when all possible outcomes
do not occur at least once. In particular, it does not work correctly with the
Aer state vector simulator.
"""

PARSER = argparse.ArgumentParser(description=EXPLANATION)
GROUP = PARSER.add_mutually_exclusive_group()
GROUP.add_argument("-q", "--ibmq", action="store_true",
                   help="Use genuine IBMQ processor (default)")
GROUP.add_argument("-s", "--sim", action="store_true",
                   help="Use IBMQ qasm simulator")
GROUP.add_argument("-a", "--aer", action="store_true",
                   help="User QISKit aer simulator")
GROUP.add_argument("-g", "--qcgpu", action="store_true",
                   help="Use qcgpu simulator (requires GPU)")
PARSER.add_argument("--api_provider", action="store",
                    help="""Backend api provider,
                    currently supported are [IBMQ | QI].
                    Default is IBMQ.""", default="IBMQ")
PARSER.add_argument("-b", "--backend", action="store",
                    help="""genuine qpu backend to use, default is least busy
                    of large enough devices""")
PARSER.add_argument("-c", "--max_credits", type=int, action="store", default=3,
                    help="max credits to expend on run, default is 3")
PARSER.add_argument("-d", "--drawcircuit", action="store_true",
                    help="Draw the circuit in extended charset")
PARSER.add_argument("-f", "--filepath", type=str, action="store",
                    help="""OPENQASM 2.0 file to use for the oracle circuit,
                    must return 3 classical bits""")
PARSER.add_argument("--from_csv", action="store",
                    help="""Load a csv file previously output by Quantum Yi Qing
                    and display the pair of hexagrams it represents""")
PARSER.add_argument("-m", "--memory", action="store_true",
                    help="Print individual results of multishot experiment")
PARSER.add_argument("--qasm", action="store_true",
                    help="Show the qasm for the circuit")
PARSER.add_argument("--shots", type=int, action="store", default=1024,
                    help="number of execution shots, default is 1024")
PARSER.add_argument("--token", action="store",
                    help="Use this token if a --url argument is also provided")
PARSER.add_argument("--url", action="store",
                    help="Use this url if a --token argument is also provided")
PARSER.add_argument("-u", "--usage", action="store_true",
                    help="Show long usage message and exit 0")
PARSER.add_argument("--use_job_monitor", action="store_true",
                    help="Use the job monitor (doesn't work with QI)")
PARSER.add_argument("-v", "--verbose", action="count", default=0,
                    help="Increase verbosity each -v up to 3")


def verbosity(text, count):
    """Print text if count exceeds verbose level"""
    if ARGS.verbose >= count:
        print(text)


def create_circuit(filepath=None):
    """Return circuit from either a qasm file or the inline circuit below."""

    if filepath:
        qc = QuantumCircuit.from_qasm_file(filepath)

    else:
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
        if ARGS.drawcircuit:
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

    return qc


def ibmq_account_fu(token, url):
    """Load IBMQ account appropriately and return provider"""
    if token:
        provider = IBMQ.enable_account(token, url=url)
    else:
        provider = IBMQ.load_account()
    return provider


def qi_account_fu(token):
    """Load Quantum Inspire account appropriately and return provider"""
    from quantuminspire.qiskit import QI
    from quantuminspire.credentials import enable_account
    if token:
        enable_account(token)
    QI.set_authentication()
    return QI


def account_fu(token, url):
    """Load account from correct API provider"""
    a_p = API_PROVIDER.upper()
    if a_p == "IBMQ":
        provider = ibmq_account_fu(token, url)
    elif a_p == "QI":
        provider = qi_account_fu(token)
    return provider


# Choose backend
# ##############


def choose_backend(local_sim, token, url, b_end, sim, qubits):
    """Return backend selected by user if account will activate and allow."""
    backend = None
    if local_sim == 'aer':
        # Import Aer
        from qiskit import BasicAer
        # Run the quantum circuit on a statevector simulator backend
        backend = BasicAer.get_backend('statevector_simulator')
    elif local_sim == 'qcgpu':
        from qiskit_qcgpu_provider import QCGPUProvider
        backend = QCGPUProvider().get_backend('qasm_simulator')
    else:
        provider = account_fu(token, url)
        verbosity("Provider is " + str(provider), 3)
        verbosity("provider.backends is " + str(provider.backends()), 3)
        if b_end:
            backend = provider.get_backend(b_end)
            verbosity('b_end provider.get_backend() returns ' + str(backend), 3)
        elif sim:
            backend = provider.get_backend('ibmq_qasm_simulator')
            verbosity('sim provider.get_backend() returns ' + str(backend), 3)
        else:
            from qiskit.providers.ibmq import least_busy
            large_enough_devices = provider.backends(
                filters=lambda x: x.configuration().n_qubits >= qubits
                and not x.configuration().simulator)
            backend = least_busy(large_enough_devices)
            verbosity("The best backend is " + backend.name(), 2)
    verbosity("Backend is " + str(backend), 1)
    return backend


######
# Main
######


ARGS = PARSER.parse_args()
API_PROVIDER = ARGS.api_provider.upper()
TOKEN = ARGS.token
URL = ARGS.url
FROM_CSV = ARGS.from_csv
USE_JM = ARGS.use_job_monitor

if ARGS.usage:
    print(LONG_EXPLANATION)
    exit(0)

if FROM_CSV:
    qh.QYQHexagram.from_csv(FROM_CSV)
    exit(0)

if API_PROVIDER == "IBMQ" and ((TOKEN and not URL) or (URL and not TOKEN)):
    print('--token and --url must be used together for IBMQ provider or not at all',
          file=sys.stderr)
    exit(1)

QC = create_circuit(ARGS.filepath)
NUM_QUBITS = circuit_to_dag(QC).num_qubits()
verbosity("NUM_QUBITS == " + str(NUM_QUBITS), 2)

# show qasm
if ARGS.qasm:
    print(QC.qasm())

# drawing the circuit
if ARGS.drawcircuit:
    print(QC.draw())

# Did user call for local simulator?
LOCAL_SIM = ''
if ARGS.aer:
    LOCAL_SIM = 'aer'
    API_PROVIDER = 'aer'
elif ARGS.qcgpu:
    LOCAL_SIM = 'qcgpu'
    API_PROVIDER = 'qcgpu'

# Choose backend
BACKEND = choose_backend(LOCAL_SIM, ARGS.token, ARGS.url,
                         ARGS.backend, ARGS.sim, NUM_QUBITS)

print("Backend is " + str(BACKEND))

if BACKEND is None:
    print("No backend available, quitting.")
    exit(100)

# Prepare to render
H = qh.QYQHexagram(API_PROVIDER, BACKEND)

# Loop running circuit and measuring.
# Each complete run provides the bit dictionary for one line.
for i in range(0, 6):
    job_exp = execute(QC, backend=BACKEND, shots=ARGS.shots,
                      max_credits=ARGS.max_credits, memory=ARGS.memory)
    if USE_JM:
        job_monitor(job_exp)

    result_exp = job_exp.result()

    # Raw data if requested
    if ARGS.memory:
        print(result_exp.data())

    # Prepare data
    counts_exp = result_exp.get_counts(QC)
    print(counts_exp)
    sorted_keys = sorted(counts_exp.keys())
    sorted_counts = {}
    for j in sorted_keys:
        k = j
        if len(j) >3:  # truncate left if necessary
            k = j[len(j)-3:]
        sorted_counts[k] = counts_exp[j]

    # Print the sorted counts
    print(sorted_counts)

    # Generate and draw hexagram
    H.assimilate(sorted_counts)
    H.draw(True)  # draw reversed

print("CSV of run:")
print(H.csv())

print('Done!')

# End
