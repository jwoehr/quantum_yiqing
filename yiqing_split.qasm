// yiqing_simple.qasm (one of many possible)
OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg c[3];
h q[0];
h q[2];
h q[4];
measure q[0] -> c[0];
measure q[2] -> c[1];
measure q[4] -> c[2];
