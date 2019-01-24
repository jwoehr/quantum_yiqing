class QYQLine:

	yin_c  = [False,True]
	yang_u = [True,False]
	yin_u  = [False,False]
	yang_c = [True,True]

	# The string pattern for the c-bits
	patt = {'000': yin_c,
			'001': yang_u,
			'010': yang_u,
			'011': yin_u,
			'100': yang_u,
			'101': yin_u,
			'110': yin_u,
			'111': yang_c
	}

	def __init__(self, yang_yin, changing):
		self.yang_yin = yang_yin
		self.changing = changing

	# Identify the pattern of the c-bits
	def getPattern(cbits):
		return QYQLine.patt[cbits]

	# Create line from pattern
	def newFromPattern(p):
		return QYQLine(p[0], p[1])

	# Render the line
	def draw(self):
		l = '*'
		if self.yang_yin:
			if self.changing:
				l+='0'
			else:
				l+='*'
		else:
			if self.changing:
				l+='X'
			else:
				l+=' '
		l += '*'
		print(l, end='')

	def interp(bit_dict):
		best = 0
		bits = [None,None]
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

# QYQHexagram keeps its lines in a list and draws them
class QYQHexagram:

	def __init__(self, lines=None):
		if lines == None:
			self.lines = []
		else:
			self.lines = lines

	def add(self, line):
		self.lines.append(line)

	def draw(self, reverse=False):
		qinglines = self.lines[:]
		
		if reverse:		
			qinglines.reverse()
			# print(qinglines)
			
		for i in qinglines:
			i.draw()
			print()

	def test(self):
		h=QYQHexagram()
		h.add(QYQLine(True,False))
		h.add(QYQLine(True,True))
		h.add(QYQLine(True,False))
		h.add(QYQLine(True,True))
		h.add(QYQLine(False,True))
		h.add(QYQLine(False,False))
		h.draw()
		h.draw(True)
