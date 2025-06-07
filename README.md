# quantum_yiqing

Quantum Computer Casts I Ching Oracle

I Ching oracle is cast by some using three coins.
3 qubits in superposition represent the three coins.
The most prevalent result of multiple measurement runs becomes the "coin toss".

The oracle has an inline quantum program which is used by default.

Optionally, with the `-f FILEPATH` switch, you can provide your own OpenQASM 2 quantum program returning 3 classical bits. Two sample programs are provided for this purpose, `yiqing_inline.qasm` and `yiqing_simple.qasm`

You must have [Qiskit](https://qiskit.org/) installed.

To use IBM Quantum devices, you must have an account with [IBM Quantum](https://quantum.cloud.ibm.com/).

```text
$ python qyq.py -h
usage: qyq.py [-h] [-b BACKEND] [-d] [-f FILEPATH] [--from_csv FROM_CSV] [--qasm] [--shots SHOTS] [--token TOKEN] [--url URL] [--channel CHANNEL] [--filename FILENAME]
              [--name NAME] [--instance INSTANCE] [-u] [-v]

QUANTUM YI QING - Cast an I Ching Oracle using IBM Quantum for the cast. Copyright 2019, 2025 Jack Woehr jwoehr@softwoehr.com PO Box 82, Beulah, CO 81024 BSD-3 license --
See LICENSE which you should have received with this code. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED
WARRANTIES.

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
  --token TOKEN         IBM Cloud API key or IBM Quantum API token
  --url URL             The API URL. Defaults to https://cloud.ibm.com (ibm_cloud) or https://auth.quantum.ibm.com/api (ibm_quantum).
  --channel CHANNEL     Channel type. ibm_cloud, ibm_quantum or local. If local is selected, the local testing mode will be used, and primitive queries will run on a local
                        simulator. For more details, check the Qiskit Runtime local testing mode documentation.
  --filename FILENAME   Full path of the file where the account is created. Default: _DEFAULT_ACCOUNT_CONFIG_JSON_FILE
  --name NAME           Name of the account to load.
  --instance INSTANCE   The service instance to use. For ibm_cloud runtime, this is the Cloud Resource Name (CRN) or the service name. For ibm_quantum runtime, this is the
                        hub/group/project in that format.
  -u, --usage           Show long usage message and exit 0
  -v, --verbose         Increase verbosity each -v up to 3
```

Jack Woehr 2025-06-08
