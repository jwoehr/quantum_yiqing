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

# Import Aer
from qiskit import BasicAer

# Run the quantum circuit on a statevector simulator backend
# backend = BasicAer.get_backend('statevector_simulator')

# Create a Quantum Program for execution 
# job = execute(circ, backend)

# result = job.result()

# outputstate = result.get_statevector(circ, decimals=3)

# show(plot(outputstate))
# print('A')
# print(outputstate)
# print('B')
# from qiskit.tools.visualization import plot_state_city
# print('C')
# plot_state_city(outputstate) # nothing seems to work here
# print('D')
# show(plot_state_city(outputstate)) # nothing seems to work here
# print('E')
# print('Done')

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

# Use Aer's qasm_simulator
backend_sim = BasicAer.get_backend('qasm_simulator')

# Execute the circuit on the qasm simulator.
# We've set the number of repeats of the circuit
# to be 1024, which is the default.
job_sim = execute(qc, backend_sim, shots=1024)

# Grab the results from the job.
result_sim = job_sim.result()

counts = result_sim.get_counts(qc)
print(counts)

from qiskit.tools.visualization import plot_histogram
show(plot_histogram(counts))

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

print("Plotting historogram: plot_histogram([counts_exp,counts])")
plot_histogram([counts_exp,counts])

# End
