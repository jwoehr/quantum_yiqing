# quantum_yiqing

Quantum Computer Casts I Ching Oracle

I Ching oracle is cast by some using three coins.
3 qubits in superposition represent the three coins.
The most prevalent result of multiple measurement runs becomes the "coin toss".

The oracle has an inline quantum program which is used by default.

Optionally, with the `-f FILEPATH` switch, you can provide your own OpenQASM 2 quantum program returning 3 classical bits. Two sample programs are provided for this purpose, `yiqing_inline.qasm` and `yiqing_simple.qasm`

You must have [Qiskit](https://qiskit.org/) installed.

To use IBM Quantum devices, you must have an account with [IBM Quantum](https://quantum.ibm.com/) .

```text
$ ./qyq.py --help
usage: qyq.py [-h] [-b BACKEND] [-d] [-f FILEPATH] [--from_csv FROM_CSV] [--qasm] [--shots SHOTS] [--token TOKEN] [--url URL] [-u] [-v]

QUANTUM YI QING - Cast an I Ching Oracle using IBM Quantum for the cast. Copyright 2019, 2022, 2024 Jack Woehr jwoehr@softwoehr.com PO Box 82, Beulah, CO 81024 BSD-3
license -- See LICENSE which you should have received with this code. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND WITHOUT ANY EXPRESS
OR IMPLIED WARRANTIES.

options:
  -h, --help            show this help message and exit
  -b BACKEND, --backend BACKEND
                        genuine qpu backend to use, default is least busy of large enough devices
  -d, --drawcircuit     Draw the circuit in extended charset
  -f FILEPATH, --filepath FILEPATH
                        OPENQASM file to use for the oracle circuit, must return 3 classical bits
  --from_csv FROM_CSV   Load a csv file previously output by Quantum Yi Qing and display the pair of hexagrams it represents
  --qasm                Show the qasm for the circuit
  --shots SHOTS         number of execution shots, default is 2048
  --token TOKEN         Use this token if a --url argument is also provided
  --url URL             Use this url if a --token argument is also provided
  -u, --usage           Show long usage message and exit 0
  -v, --verbose         Increase verbosity each -v up to 3
```

Jack Woehr 2024-12-15
