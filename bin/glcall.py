#!/usr/bin/python
"""https://github.com/xenomonadbase/glcall.git
glcall.py global gtags bash completed function name caller callee explorer
usage: glcall.py <-x|-r> <symbolname> [-l level] [-f filterstr] [-o]
       used with bash_completion as follows to auto complete next caller/callee names
       glcall -x <symbolname> next_[TAB] ...
"""

import sys, string, os, re, getopt, os.path
import heapq
import subprocess
verbose=0
output=0
level=" "
fstr=""
gcmd=0
nlevel=0
strlmax = 32
sopts="hvir:l:x:of:s:"
lopts=["help", "verbose", "calls=", "stdin", "level=", "called=", "output", "filter=", "linemax="]
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
dfls = []

glcmds = {
	enum_called : ["global -rx", "global -sx"],
	enum_calls : ["global -sx", "global -x"]
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
		dfls += sys.stdin.readlines()
	if o in ("-r","--called", "-rx"):
		gcmd = enum_called
		for glcmd in glcmds[gcmd]:
			cmd = glcmd+" "+a
			if verbose: print cmd
			dfls += os.popen(cmd).readlines()
	if o in ("-x","--calls", "-sx", "-s"):
		gcmd = enum_calls
		for glcmd in glcmds[gcmd]:
			cmd = glcmd+" "+a
			if verbose: print cmd
			dfls += os.popen(cmd).readlines()
	if o in ("-l","--level"):
		nlevel = int(a,10)
		level = " "*nlevel
	if o in ("-o","--output"):
		output = 1
	if o in ("-f","--filter"):
		fstr = a
	if o  == "--linemax":
		linmx = int(a)
		if linmx > 0:
			print "opt strlmax: %d opt:%s"%(linmx, o)


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
	enum_calls  : re.compile(r'(\S+)\s+(\d+)\s+(\S+)\s+(.*)'),
}
def doprint(l):
	print l
def split_gtag(m):
	if verbose: dummy=[doprint(l) for l in [m.group(i) for i in [1,2,3,4]]]
	return (m.group(1), int(m.group(2),10), m.group(3), m.group(4))

def wccount(filename):
	out = subprocess.Popen(['wc', '-l', filename],
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT
			).communicate()[0]
	return int(out.partition(b' ')[0])

def get_func_end(flnm, lno):
	"""parse the sym definition of a file
	   and return the one just after
	   the specified line number to get the end of
		   function line
	"""
	global verbose
	global gcmd
	#if verbose: print get_func_end
	#cmd = "gtags-parser -t %s" % flnm # for version 5.7.7 or earlier...
	cmd = "global -f %s" % flnm
	gp = os.popen(cmd)
	if verbose:
		print "get_func_end cmd: %s %d"%(cmd, lno)
	endlno = wccount(flnm)
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
	if verbose: print "endlno: %d"%(endlno)
	return endlno


def get_func_caller(flnm, lno):
	""" return what function is calling the function specified as lineno in a file
	"""
	global verbose
	global gcmd
	#if verbose: print get_func_caller
	#cmd = "gtags-parser -t %s" % flnm # for version 5.7.7 or earlier...
	cmds = ["global -f %s" % flnm]
	caller = ""
	prevno = 0

	for cmd in cmds:
		gp = os.popen(cmd)
		if verbose:
			print "get_func_caller cmd: ", cmd
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
		if verbose: print "caller: %s prevno:%d"%(caller, prevno)
	return (caller, prevno)

def get_func_calls(flnm, lno, defined, endlno):
	""" return symbol calls in the flnm from the func(defined) until the endlno
	"""
	global verbose
	global gcmd
	global strlmax
	if verbose: print get_func_calls
	#cmd = "gtags-parser -r %s" % flnm # for version 5.7.7 or earlier...
	cmds = ["global -r -f %s" % flnm, "global -s -f %s" % flnm]
	for cmd in cmds:
		gp = os.popen(cmd)
		if verbose:
			print "get_func_calls cmd: %s lno:%d endlno:%d"%(cmd,lno, endlno)
		calls = ""
		for gpline in gp:
			if verbose:
				print "gpline: ", gpline
			m = regs[gcmd].match(gpline)
			if m:
				(calls,plno,flnm,rest)=split_gtag(m)
				if verbose: print "plno: %d lno: %d endlno: %d"%(plno, lno, endlno)
				if lno < plno and plno < endlno:
					calls_line = "%-*s"%(strlmax-nlevel, defined[:(strlmax-nlevel)])+":%6d => "%lno+"%-*s"%(strlmax, calls[:strlmax])+":%6d"%plno
					if output: print "%s"%calls
					elif (fstr == calls or fstr == "all"):
						print "%s%s |%s |%s"%(level, calls_line, flnm, rest)
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
	global strlmax
	if verbose: print called_func
	(callee,lno,flnm,rest) = split_gtag(m)
	(caller_func, caller_lno) = get_func_caller(flnm, lno)
	if caller_func:
		caller_line = "%-*s"%(strlmax-nlevel, callee[:(strlmax-nlevel)])+":%6d => "%lno+"%-*s"%(strlmax, caller_func[:strlmax])+":%6d"%caller_lno
		#caller_line = "%-32s:%6d <= %-32s:%6d"%(callee, lno, caller_func, caller_lno)
		if output: print "%s"%caller_func
		elif (fstr == caller_func or fstr == "all"):
			print "%s%s |%s |%s"%(level, caller_line, flnm, rest)
	else:
		caller_line = "%s:%d <= unknown"%(callee, lno)
		if output: print "unknown"
		elif fstr == "all":
			print "%s%s |%s |%s"%(level, caller_line, flnm, rest)

proc_funcs = {
	enum_called : called_func,
	enum_calls : calls_func,
}

for line in dfls:
	m = regs[gcmd].match(line)
	if not m:
		print "not match: ", line
		continue
	proc_funcs[gcmd](m)



