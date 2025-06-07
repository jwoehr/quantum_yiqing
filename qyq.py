#!/usr/bin/env python

"""qyq.py ... Main script. Run and render.
QUANTUM YI QING - Cast an I Ching Oracle using IBM Q for the cast.
Copyright 2019, 2022, 2024, 2025 Jack Woehr jwoehr@softwoehr.com PO Box 82, Beulah, CO 81024
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES."""

import argparse
import pprint
from qiskit.converters import circuit_to_dag
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, qasm3
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import qyqhex as qh

EXPLANATION = """QUANTUM YI QING - Cast an I Ching Oracle using IBM Quantum for the cast.
Copyright 2019, 2025 Jack Woehr jwoehr@softwoehr.com PO Box 82, Beulah, CO 81024
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
"""

LONG_EXPLANATION = f"""{EXPLANATION}
Performs the oracle on a genuine IBM quantum processor.

Default is to assume the user has stored an IBM Quantum account token
which can be retrieved by qiskit.QiskitRuntimeService(). Alternatively, the
various keyword arguments can be provided by any reasonable combination of
the program switches --url --token --name --filename --instance --channel.

The easiest is "no switches" which uses your account defaults. If you have
multiple accounts in your qiskit json file, use --name to identify the
desired account.

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
changed hexagram stands as calculated per above.

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
PARSER.add_argument(
    "-b",
    "--backend",
    action="store",
    help="""genuine qpu backend to use, default is least busy
                    of large enough devices""",
)
PARSER.add_argument(
    "-d",
    "--drawcircuit",
    action="store_true",
    help="Draw the circuit in extended charset",
)
PARSER.add_argument(
    "-f",
    "--filepath",
    type=str,
    action="store",
    help="""OPENQASM file to use for the oracle circuit,
                    must return 3 classical bits""",
)
PARSER.add_argument(
    "--from_csv",
    action="store",
    help="""Load a csv file previously output by Quantum Yi Qing
                    and display the pair of hexagrams it represents""",
)
PARSER.add_argument("--qasm", action="store_true", help="Show the qasm for the circuit")
PARSER.add_argument(
    "--shots",
    type=int,
    action="store",
    default=2048,
    help="number of execution shots, default is 2048",
)
PARSER.add_argument(
    "--token",
    action="store",
    help="IBM Cloud API key or IBM Quantum API token",
)
PARSER.add_argument(
    "--url",
    action="store",
    help="""The API URL.
    Defaults to https://cloud.ibm.com (ibm_cloud) or 
    https://auth.quantum.ibm.com/api (ibm_quantum).""",
)
PARSER.add_argument(
    "--channel",
    action="store",
    help="""Channel type. ibm_cloud, ibm_quantum or local. If local is 
    selected, the local testing mode will be used, and primitive queries will 
    run on a local simulator. For more details, check the Qiskit Runtime 
    local testing mode documentation.""",
)
PARSER.add_argument(
    "--filename",
    action="store",
    help="""Full path of the file where the account is created. 
    Default: _DEFAULT_ACCOUNT_CONFIG_JSON_FILE""",
)
PARSER.add_argument("--name", action="store", help="""Name of the account to load.""")
PARSER.add_argument(
    "--instance",
    action="store",
    help="""The service instance to use. For ibm_cloud runtime, this is the
    Cloud Resource Name (CRN) or the service name. For ibm_quantum runtime,
    this is the hub/group/project in that format. """,
)
PARSER.add_argument(
    "-u", "--usage", action="store_true", help="Show long usage message and exit 0"
)
PARSER.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Increase verbosity each -v up to 3",
)


def verbosity(text, count):
    """Print text if count exceeds verbose level"""
    if ARGS.verbose >= count:
        print(text)


def create_circuit(filepath=None):
    """Return circuit from either a qasm file or the inline circuit below."""

    circ = None

    if filepath:
        circ = QuantumCircuit.from_qasm_file(filepath)

    else:
        # Create a Quantum Register with 6 qubits.
        q = QuantumRegister(6, "q")

        # Create a Classical Register with 3 bits.
        c = ClassicalRegister(3, "c")

        # Create a Quantum Circuit acting on the registers
        circ = QuantumCircuit(q, c)

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

        circ.barrier(q)

        # map the quantum measurement to the classical bits
        circ.measure(q[1], c[0])
        circ.measure(q[3], c[1])
        circ.measure(q[5], c[2])

    return circ


def formulate_account_kwargs() -> dict:
    """
    Build the kwargs to the account from options

    Returns
    -------
    dict
        The key/value dict of kwargs for QiskitRuntimeService()

    """
    kwargs = {}
    if TOKEN:
        kwargs["token"] = TOKEN
    if URL:
        kwargs["url"] = URL
    if CHANNEL:
        kwargs["channel"] = CHANNEL
    if FILENAME:
        kwargs["filename"] = FILENAME
    if NAME:
        kwargs["name"] = NAME
    if INSTANCE:
        kwargs["instance"] = INSTANCE
    return kwargs


def account_fu(kwargs: dict):
    """Load IBMQ account appropriately and return service"""
    service = None
    if len(kwargs) > 0:
        service = QiskitRuntimeService(**kwargs)
    else:
        service = QiskitRuntimeService()
    return service


# Choose backend
# ##############


def choose_backend(token, url, b_end, qubits=6):
    """Return backend selected by user if account will activate and allow."""
    backend = None
    service = account_fu(formulate_account_kwargs())
    verbosity("service is " + str(service), 3)
    verbosity("service.backends is " + str(service.backends()), 3)
    if b_end:
        backend = service.get_backend(b_end)
        verbosity("b_end service.get_backend() returns " + str(backend), 3)
    else:
        backend = service.least_busy(min_num_qubits=qubits)
        verbosity("The best backend is " + backend.name, 2)
    verbosity("Backend is " + str(backend), 1)
    return backend


######
# Main
######


ARGS = PARSER.parse_args()
# API_service = ARGS.api_service.upper()
SHOTS = ARGS.shots
TOKEN = ARGS.token
URL = ARGS.url
CHANNEL = ARGS.channel
FILENAME = ARGS.filename
NAME = ARGS.name
INSTANCE = ARGS.instance
FROM_CSV = ARGS.from_csv
# USE_JM = ARGS.use_job_monitor

if ARGS.usage:
    print(LONG_EXPLANATION)
    exit(0)

if FROM_CSV:
    qh.QYQHexagram.from_csv(FROM_CSV)
    exit(0)

QC = create_circuit(ARGS.filepath)
NUM_QUBITS = circuit_to_dag(QC).num_qubits()
verbosity("NUM_QUBITS == " + str(NUM_QUBITS), 2)

# show qasm
if ARGS.qasm:
    print(qasm3.dumps(QC))

# drawing the circuit
if ARGS.drawcircuit:
    print(QC.draw())

# Choose backend
BACKEND = choose_backend(ARGS.token, ARGS.url, ARGS.backend, NUM_QUBITS)

print("Backend is " + str(BACKEND))

if BACKEND is None:
    print("No backend available, quitting.")
    exit(100)

# Prepare to render
H = qh.QYQHexagram("IBM Quantum", BACKEND)

# Loop compiling and transpiling circuit 6 times for 6 lines.
# Each circuit will provide the bit dictionary for one line.
circuits = []
pm = generate_preset_pass_manager(optimization_level=1, backend=BACKEND)

for i in range(0, 6):
    circuits.append(pm.run(QC))

sampler = Sampler(mode=BACKEND)
job = sampler.run(circuits, shots=SHOTS)
print(f">>> Job ID: {job.job_id()}")
print(f">>> Job Status: {job.status()}")
result = job.result()
all_counts_sorted = []

index = 1
for item in result:
    sorted_counts = {}
    counts = item.data["c"].get_counts()
    print(f"Counts for QYQ circuit {index} : {counts}")
    sorted_keys = sorted(counts.keys())
    for j in sorted_keys:
        k = j
        if len(j) > 3:  # truncate left if necessary
            k = j[len(j) - 3 :]
        sorted_counts[k] = counts[j]
    all_counts_sorted.append(sorted_counts)
    index += 1

# Print all sorted counts
pprint.pprint(all_counts_sorted)

# Generate and draw hexagram
for scounts in all_counts_sorted:
    H.assimilate(scounts)
H.draw(True)  # draw reversed

print("CSV of run:")
print(H.csv())
print("Done!")

# End
