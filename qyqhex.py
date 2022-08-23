"""qyqhex.py ... Calculate hexagram and changed hexagram from IBMQ bit dictionary
QUANTUM YI QING - Cast a Yi Qing Oracle using IBM Q for the cast.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES."""

import datetime as dt
import csv

# Embody and render a line of a hexagram
# Keeps state so changed line can be rendered


class QYQLine:
    """Interpret a bit pattern as a hexagram line"""

    yin_c = [False, True]
    yang_u = [True, False]
    yin_u = [False, False]
    yang_c = [True, True]

    patt = {
        "000": yin_c,
        "001": yang_u,
        "010": yang_c,
        "011": yin_u,
        "100": yang_u,
        "101": yin_c,
        "110": yin_u,
        "111": yang_c,
    }
    """The string pattern for the c-bits"""

    def __init__(self, yang_yin, changing):
        """Strong or weak line, changing or unchanging"""
        self.yang_yin = yang_yin
        self.changing = changing

    @staticmethod
    def getPattern(cbits):
        """Identify the pattern of the c-bits and return a line"""
        return QYQLine.patt[cbits]

    @staticmethod
    def newFromPattern(p):
        """Create line from pattern"""
        return QYQLine(p[0], p[1])

    def draw(self):
        """Render the line"""
        the_line = "***"
        if self.yang_yin:
            if self.changing:
                the_line += "000"
            else:
                the_line += "***"
        else:
            if self.changing:
                the_line += "XXX"
            else:
                the_line += "   "
        the_line += "***"
        return the_line

    def draw_changed(self):
        """Render a changed line for the second hexagram"""
        if self.yang_yin:
            if self.changing:
                the_line = "***   ***"
            else:
                the_line = "*********"
        else:
            if self.changing:
                the_line = "*********"
            else:
                the_line = "***   ***"
        return the_line

    @staticmethod
    def interp(bit_dict):
        """Analyse a bit dictionary and create the line"""
        best = 0
        bits = [None, None]
        for i in bit_dict.keys():
            val = bit_dict[i]
            if val == best:
                bits[1] = i
                if bits[0] is None:
                    bits[0] = i
            elif val > best:
                best = val
                bits[1] = None
                bits[0] = i
        if bits[1] is None:
            return QYQLine.newFromPattern(QYQLine.getPattern(bits[0]))
        else:
            x = [QYQLine.getPattern(bits[0]), QYQLine.getPattern(bits[1])]
            if x[0] == x[1]:
                return QYQLine.newFromPattern(x[0])
            if QYQLine.yin_c in x:
                if QYQLine.yang_u in x:
                    return QYQLine.newFromPattern(QYQLine.yang_u)
                if QYQLine.yin_u in x:
                    return QYQLine.newFromPattern(QYQLine.yin_u)
                if QYQLine.yang_c in x:
                    return QYQLine.newFromPattern(QYQLine.yin_c)
            elif QYQLine.yang_u in x:
                if QYQLine.yin_u in x:
                    return QYQLine.newFromPattern(QYQLine.yin_u)
                if QYQLine.yang_c in x:
                    return QYQLine.newFromPattern(QYQLine.yang_c)
            else:
                return QYQLine.newFromPattern(QYQLine.yang_c)


class QYQTimedCountsExp:
    """Sorted counts_exp with timestamp"""

    def __init__(self, counts_exp):
        self.time = dt.datetime.now()
        sorted_keys = sorted(counts_exp.keys())
        sorted_counts = {}
        for i in sorted_keys:
            sorted_counts[i] = counts_exp[i]
        self.counts_exp = sorted_counts


class QYQHexagram:
    """
    QYQHexagram keeps its lines in a list
    and draws hexagram and changed hexagram
    """

    def __init__(self, provider, backend, lines=None):
        self.provider = provider
        self.backend = backend
        self.qyqTimeCountsCollection = []
        if lines is None:
            self.lines = []
        else:
            self.lines = lines

    def add(self, line):
        """Add a line to hexagram"""
        self.lines.append(line)

    def assimilate(self, counts_exp):
        """Add line with counts_exp preserved to hexagram"""
        self.qyqTimeCountsCollection.append(QYQTimedCountsExp(counts_exp))
        self.add(QYQLine.interp(counts_exp))

    def draw(self, reverse=False):
        """Print hexagram at current state"""
        qinglines = self.lines[:]

        if reverse:
            qinglines.reverse()
            # print(qinglines)

        for i in qinglines:
            print(i.draw() + "   " + i.draw_changed())

    def csv(self):
        """Create a csv of the hex run"""
        result = str(self.provider) + ":" + str(self.backend) + ";"
        for i in QYQLine.patt.keys():
            result += i
            result += ";"
        result += "\n"
        for i in self.qyqTimeCountsCollection:
            result += i.time.strftime("%Y-%m-%d_%H:%M:%S:%f")
            result += ";"
            for j in i.counts_exp.values():
                result += str(j)
                result += ";"
            result += "\n"
        return result

    @staticmethod
    def from_csv(csv_filename):
        """Load a csv file previously output by Quantum Yi Qing
        and display the pair of hexagrams it represents"""

        bit_keys = ["000", "001", "010", "011", "100", "101", "110", "111"]

        _qyqh = QYQHexagram("", "")

        with open(csv_filename) as _csvfile:

            r = csv.reader(_csvfile, delimiter=";")
            rows = []
            for row in r:
                rows.append(row)
            rows = rows[1:7]
            for row in rows:
                line_dict = {}
                row_list = []
                for item in row:
                    row_list.append(item)
                row_list = row_list[1:9]
                for i in range(0, 8):
                    line_dict[bit_keys[i]] = int(row_list[i])
                _qyqh.assimilate(line_dict)

        _csvfile.close()
        _qyqh.draw(True)

    @staticmethod
    def test():
        """Test routine"""
        h = QYQHexagram("Test", "Test")
        h.add(QYQLine(True, False))
        h.add(QYQLine(True, True))
        h.add(QYQLine(True, False))
        h.add(QYQLine(True, True))
        h.add(QYQLine(False, True))
        h.add(QYQLine(False, False))
        h.draw()
        h.draw(True)


# End
