# quantum_yiqing
Quantum Computer Casts Yi Qing Oracle

Yi Qing oracle is cast by some using three coins.
3 qubits in superposition represent the three coins.
The most prevalent result of multiple measurement runs becomes the "coin toss".

The oracle has an inline quantum program which is used by default.

Optionally, with the `-f FILEPATH` switch, you can provide your own OPENQASM 2.0 quantum program returning 3
classical bits. Two sample programs are provided for this purpose, `yiqing_inline.qasm` and `yiqing_simple.qasm`

You must have [QISKit](https://qiskit.org/) installed.

To use IBM Q Experience online devices and/or simulator(s), you must have an account from [IBM Q Experience](https://quantum-computing.ibm.com/) .

To use QI support you must also have installed the [Quantum Inspire SDK](https://github.com/QuTech-Delft/quantuminspire)
and have a token provided with your account from the [QuTech website](https://www.qutech.nl/).

```
$ python qyq.py --help
usage: qyq.py [-h] [-q | -s | -a] [--api_provider API_PROVIDER] [-b BACKEND]
              [-c MAX_CREDITS] [-d] [-f FILEPATH] [-m] [--qasm]
              [--shots SHOTS] [--token TOKEN] [--url URL] [-u] [-v]

QUANTUM YI QING - Cast a Yi Qing Oracle using IBM Q for the cast. Copyright
2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051 BSD-3
license -- See LICENSE which you should have received with this code. THIS
SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.

optional arguments:
  -h, --help            show this help message and exit
  -q, --ibmq            Use genuine IBMQ processor (default)
  -s, --sim             Use IBMQ qasm simulator
  -a, --aer             User QISKit aer simulator
  --api_provider API_PROVIDER
                        Backend api provider, currently supported are [IBMQ |
                        QI]. Default is IBMQ.
  -b BACKEND, --backend BACKEND
                        genuine qpu backend to use, default is least busy of
                        large enough devices
  -c MAX_CREDITS, --max_credits MAX_CREDITS
                        max credits to expend on run, default is 3
  -d, --drawcircuit     Draw the circuit in extended charset
  -f FILEPATH, --filepath FILEPATH
                        OPENQASM 2.0 file to use for the oracle circuit, must
                        return 3 classical bits
  -m, --memory          Print individual results of multishot experiment
  --qasm                Show the qasm for the circuit
  --shots SHOTS         number of execution shots, default is 1024
  --token TOKEN         Use this token if a --url argument is also provided
  --url URL             Use this url if a --token argument is also provided
  -u, --usage           Show long usage message and exit 0
  -v, --verbose         Increase verbosity each -v up to 3
```
