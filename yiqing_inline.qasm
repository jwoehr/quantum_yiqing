// yiqing_inline.qasm (one of many possible)
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
