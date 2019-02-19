# qyqhex.py ... Calculate hexagram and changed hexagram from IBMQ bit dictionary
# QUANTUM YI QING - Cast a Yi Qing Oracle using IBM Q for the cast.
# Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
# BSD-3 license -- See LICENSE which you should have received with this code.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# WIHTOUT ANY EXPRESS OR IMPLIED WARRANTIES.

import datetime as dt

# Embody and render a line of a hexagram
# Keeps state so changed line can be rendered


class QYQLine:
    """Interpret a bit pattern as a hexagram line"""
    yin_c = [False, True]
    yang_u = [True, False]
    yin_u = [False, False]
    yang_c = [True, True]

    patt = {'000': yin_c,
            '001': yang_u,
            '010': yang_u,
            '011': yin_u,
            '100': yang_u,
            '101': yin_u,
            '110': yin_u,
            '111': yang_c
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
        l = '***'
        if self.yang_yin:
            if self.changing:
                l += '000'
            else:
                l += '***'
        else:
            if self.changing:
                l += 'XXX'
            else:
                l += '   '
        l += '***'
        return l

    def draw_changed(self):
        """Render a changed line for the second hexagram"""
        if self.yang_yin:
            if self.changing:
                l = '***   ***'
            else:
                l = '*********'
        else:
            if self.changing:
                l = '*********'
            else:
                l = '***   ***'
        return l

    def interp(bit_dict):
        """Analyse a bit dictionary and create the line"""
        best = 0
        bits = [None, None]
        for i in bit_dict.keys():
            val = bit_dict[i]
            if val == best:
                bits[1] = i
                if bits[0] == None:
                    bits[0] = i
            elif val > best:
                best = val
                bits[1] = None
                bits[0] = i
        if bits[1] == None:
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

    def __init__(self, backend, lines=None):
        self.backend = backend
        self.qyqTimeCountsCollection = []
        if lines == None:
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
            print (i.draw() + '   ' + i.draw_changed())

    def csv(self):
        """Create a csv of the hex run"""
        result = str(self.backend) + ';'
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

    def test(self):
        """Test routine"""
        h = QYQHexagram()
        h.add(QYQLine(True, False))
        h.add(QYQLine(True, True))
        h.add(QYQLine(True, False))
        h.add(QYQLine(True, True))
        h.add(QYQLine(False, True))
        h.add(QYQLine(False, False))
        h.draw()
        h.draw(True)

# End
