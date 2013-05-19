#!/usr/bin/python
"""https://github.com/xenomonadbase/glcall.git
glcall.py global gtags bash completed function name caller callee explorer
usage: glcall.py <-x|-r> <symbolname> [-l level] [-f filterstr] [-o]
       used with bash_completion as follows to auto complete next caller/callee names
       glcall -x <symbolname> next_[TAB] ...
"""

import sys, string, os, re, getopt, os.path
import heapq
verbose=0
output=0
level=" "
fstr=""
gcmd=0
sopts="hvir:l:x:of:"
lopts=["help", "verbose", "calls=", "stdin", "level=", "called=", "output", "filter="]
try:
	opts, args = getopt.getopt(sys.argv[1:],sopts,lopts) 

except getopt.GetoptError:
	# print help information and exit:
	print __doc__ 
	print "typed:", sys.argv[0]
	print "options:\n    short:",sopts
	print "    long:",lopts
	sys.exit(2)


def getline(df, doprint=verbose):
	try:
		line = df.readline()
	except:
		if verbose: print "no more input"
		sys.exit()
	if not line:
		if verbose: print "no more input"
		sys.exit()	
	if doprint: print line	
	return line

enum_calls = 0
enum_called = 1
glcmds = {
	enum_called : "global -rx",
	enum_calls : "global -x"
}

for o, a in opts:
	if o in ("-v", "--verbose"):
		verbose = 1
	if o in ("-h", "--help"):
		print __doc__
		print "options:\n    short:",sopts
		print "    long:",lopts
		sys.exit()
	if o in ("-i", "--stdin"):
		df = sys.stdin
	if o in ("-r","--called"):
		gcmd = enum_called
		cmd = glcmds[gcmd]+" "+a
		if verbose: print cmd
		df = os.popen(cmd)
	if o in ("-x","--calls"):
		gcmd = enum_calls
		cmd = glcmds[gcmd]+" "+a
		if verbose: print cmd
		df = os.popen(cmd)
	if o in ("-l","--level"):
		level = " "*int(a,10)
	if o in ("-o","--output"):
		output = 1
	if o in ("-f","--filter"):
		fstr = a


"""
compress           36 libutil/compress.h char *compress(const char *text, const char *name);
compress           91 libutil/fileop.c  if (compress) {
compress          103 libutil/fileop.c  if (compress)
compress          106 libutil/fileop.c  if (compress)
compress          433 libutil/gtagsop.c                         strbuf_puts(gtop->sb, compress(ptable.part[PART_TAG].start, key));
compress          440 libutil/gtagsop.c                         compress(ptable.part[PART_LINE].start, key) :
compress          755 libutil/gtagsop.c                         strbuf_puts(gtop->sb, compress(entry->name, key));
"""
regs = {
	enum_called : re.compile(r'(\S+)\s+(\d+)\s+(\S+)\s+(.*)'),
	enum_calls : re.compile(r'(\S+)\s+(\d+)\s+(\S+)\s+(.*)'),
}
def doprint(l):
	print l
def split_gtag(m):
	if verbose: dummy=[doprint(l) for l in [m.group(i) for i in [1,2,3,4]]]
	return (m.group(1), int(m.group(2),10), m.group(3), m.group(4))

def get_func_end(flnm, lno):
	"""parse the sym definition of a file
	   and return the one just after
	   the specified line number to get the end of
           function line
	"""
	global verbose
	global gcmd
	if verbose: print get_func_end
	#cmd = "gtags-parser -t %s" % flnm # for version 5.7.7 or earlier...
	cmd = "global -f %s" % flnm
	gp = os.popen(cmd)
	if verbose:
		print "cmd: ", cmd
	endlno = 0
	for gpline in gp:
		if verbose:
			print "gpline: ", gpline
		m = regs[gcmd].match(gpline)
		if m:
			plno=int(m.group(2),10)
			if plno > lno:
				endlno = plno
				break
	gp.close()
	return endlno


def get_func_caller(flnm, lno):
	""" return what function is calling the function specified as lineno in a file
	"""
	global verbose
	global gcmd
	if verbose: print get_func_caller
	#cmd = "gtags-parser -t %s" % flnm # for version 5.7.7 or earlier...
	cmd = "global -f %s" % flnm
	gp = os.popen(cmd)
	if verbose:
		print "cmd: ", cmd
	caller = ""
	prevno = 0
	for gpline in gp:
		if verbose:
			print "gpline: ", gpline
		m = regs[gcmd].match(gpline)
		if m:
			plno=int(m.group(2),10)
			if plno > lno:
				break
			else:
				prevno = plno
				caller = m.group(1)
	gp.close()
	return (caller, prevno)

def get_func_calls(flnm, lno, defined, endlno):
	""" return symbol calls in the flnm from the func(defined) until the endlno
	"""
	global verbose
	global gcmd
	if verbose: print get_func_calls
	#cmd = "gtags-parser -r %s" % flnm # for version 5.7.7 or earlier...
	cmd = "global -r -f %s" % flnm
	gp = os.popen(cmd)
	if verbose:
		print "cmd: ", cmd
	calls = ""
	for gpline in gp:
		if verbose:
			print "gpline: ", gpline
		m = regs[gcmd].match(gpline)
		if m:
			(calls,plno,flnm,rest)=split_gtag(m)
			if verbose: print "plno: %d lno: %d endlno: %d"%(plno, lno, endlno)
			if lno < plno and plno < endlno:
				calls_line = "%s:%d => %s:%d"%(defined, lno, calls, plno)
				spaces=" "*(40-min(len(calls_line),40))
				spaces2=" "*(34-min(len(flnm), 32))
				if output: print "%s"%calls
				elif (fstr == calls or fstr == "all"):
					print "%s%s %s |%s %s |%s"%(level, calls_line, spaces, flnm, spaces2, rest)
			if plno > endlno:
				break
	gp.close()



def calls_func(m):
	if verbose: print calls_func
	(defined,lno,flnm,rest) = split_gtag(m)
	endlno = get_func_end(flnm, lno)
	if verbose: print "endlno: ", endlno
	get_func_calls(flnm, lno, defined, endlno)

def called_func(m):
	if verbose: print called_func
	(callee,lno,flnm,rest) = split_gtag(m)
	(caller_func, caller_lno) = get_func_caller(flnm, lno)
	if caller_func:
		caller_line = "%s:%d <= %s:%d"%(callee, lno, caller_func, caller_lno)
		spaces=" "*(40-min(len(caller_line),40))
		spaces2=" "*(34-min(len(flnm), 32))
		if output: print "%s"%caller_func
		elif (fstr == caller_func or fstr == "all"):
			print "%s%s %s |%s %s |%s"%(level, caller_line, spaces, flnm, spaces2, rest)
	else:
		caller_line = "%s:%d <= unknown"%(callee, lno)
		spaces=" "*(40-min(len(caller_line),40))
		spaces2=" "*(34-min(len(flnm), 32))
		if output: print "unknown"
		elif fstr == "all":
			print "%s%s %s |%s %s |%s"%(level, caller_line, spaces, flnm, spaces2, rest)

proc_funcs = {
	enum_called : called_func,
	enum_calls : calls_func,
}

while 1:
	line = getline(df)
	m = regs[gcmd].match(line)
	if not m:
		print "not match: ", line
		continue
	proc_funcs[gcmd](m)



