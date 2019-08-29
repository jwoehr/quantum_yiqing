# quantum_yiqing
Quantum Computer Casts Yi Qing Oracle

Yi Qing oracle is cast by some using three coins.
3 qubits in superposition represent the three coins.
The most prevalent result of multiple measurement runs becomes the "coin toss".

The oracle has an inline quantum program.

Alternatively, with the `-f FILEPATH` switch, you can provide your own OPENQASM 2.0 quantum program returning 3
classical bits. Two sample programs are provided for this purpose, `yiqing_inline.qasm` and `yiqing_simple.qasm`

You must have [QISKit](https://qiskit.org/) installed.

To use QI support you must also have installed the [Quantum Inspire SDK](https://github.com/QuTech-Delft/quantuminspire)
and have a token provided with your account from the [QuTech website](https://www.qutech.nl/).

You need an [IBMQ Experience](https://quantumexperience.ng.bluemix.net) account and token installed.

`python qyq.py --help` for an explanation.
