#!/usr/local/bin/python
#
# lineterm.py
#
# <This one may actually be cross-platform!!!>
#
# Usage: python lineterm.py [options] files
#
# Options:
#  	-h, --help    : Show this message
#	-m, --mac     : Convert file(s) to Mac format (carriage returns)
#	-p, --pc      : Convert file(s) to PC format (carriage return/linefeeds)
#	-u, --unix    : Convert file(s) to Unix format (linefeeds)
#   -v, --verbose : Show the number of CRs, LFs, and CR/LFs for the file(s)
#
# Arguments:
#	files : any file or group of files (wildcards allowed)
#
# Note:
#	Does not currently recurse directories or distinguish between
#	binary and ASCII file types.  Creates a ~temp file in the current
#	directory when converting files to a different format.
#

import os, getopt, sys, curses

def main():
	convertToMac = 0
	convertToPC = 0
	convertToUNIX = 0
	isVerbose = 0

	try:
		opts, args = getopt.getopt( sys.argv[1:], "hmpuv:", ["help", "mac", "pc", "unix", "verbose"] )

	except getopt.GetoptError:
		# print help information and exit:
		usage()
		sys.exit( 2 )

	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		if o in ("-m", "--mac"):
			# print "output reached"
			# output = a
			convertToMac = 1
		if o in ("-p", "--pc"):
			convertToPC = 1
		if o in ("-u", "--unix"):
			convertToUNIX = 1
		if o in ("-v", "--verbose"):
			isVerbose = 1

	if len(args) == 0:
		usage()
		sys.exit()

	for FILE in args:
		fileType = readFile( FILE, isVerbose )
		if fileType != "Undefined":
			if convertToMac == 1:
				toMac( FILE, fileType )
			if convertToPC == 1:
				toPC( FILE, fileType )
			if convertToUNIX == 1:
				toUNIX( FILE, fileType )
		else:
			print "file "
			print FILE
			print " is undefined, therefore conversion was aborted"

def toMac( fileName, fileType ):
	FILE = open( fileName, "r" )

	os.system( "touch ~temp" )
	OUTFILE = open( "~temp", "w" )

	char = FILE.read( 1 )
	last = 0

	while char:
		if fileType == "UNIX":
			if char == chr(0x0a):				# LINE FEED
				OUTFILE.write( chr(0x0d) )  	# replace LF with CR
			else:
				OUTFILE.write( char )
		elif fileType == "MAC":
			OUTFILE.write( char )				# file already in mac format
		elif fileType == "PC":
			if last == chr(0x0a):				# if last character was CR
				if char == chr(0x0d):			# ...and this one is LF
					OUTFILE.write( chr(0x0d) )	# then replace CR/LF with CR
					last = 0
				else:
					OUTFILE.write( char )
			elif char == chr(0x0a):
				last = chr(0x0a)
			else:
				OUTFILE.write( char )
		char = FILE.read( 1 )


	FILE.close()
	OUTFILE.close()
	os.system( "mv ~temp " + fileName + ".MAC" )

	print "MAC"


def toPC( fileName, fileType ):
	FILE = open( fileName, "r" )

	os.system( "touch ~temp" )
	OUTFILE = open( "~temp", "w" )

	char = FILE.read( 1 )

	while char:
		if fileType == "UNIX":
			if char == chr(0x0a):			# LF
				OUTFILE.write( chr(0x0d) )  # replace LF with CR/LF
				OUTFILE.write( chr(0x0a) )
			else:
				OUTFILE.write( char )
		elif fileType == "MAC":
			if char == chr(0x0d):
				OUTFILE.write( chr(0x0d) )	# replace CR with CR/LF
				OUTFILE.write( chr(0x0a) )
			else:
				OUTFILE.write( char )
		elif fileType == "PC":
			OUTFILE.write( char )			# file already in PC format
		char = FILE.read( 1 )

	FILE.close()
	OUTFILE.close()
	os.system( "mv ~temp " + fileName + ".PC" )

	print "PC"

def toUNIX( fileName, fileType ):
	FILE = open( fileName, "r" )

	os.system( "touch ~temp" )
	OUTFILE = open( "~temp", "w" )

	char = FILE.read( 1 )
	last = 0

	while char:
		if fileType == "UNIX":
			OUTFILE.write( char )			# file already in UNIX format
		elif fileType == "MAC":
			if char == chr(0x0d):
				OUTFILE.write( chr(0x0a) )
			else:
				OUTFILE.write( char )
		elif fileType == "PC":
			if last == chr(0x0d):				# if last character was CR
				if char == chr(0x0a):			# ...and this one is LF
					OUTFILE.write( chr(0x0a) )	# then replace CR/LF with LF
					last = 0
				else:
					OUTFILE.write( char )
			elif char == chr(0x0d):
				last = chr(0x0d)
			else:
				OUTFILE.write( char )
		char = FILE.read( 1 )

	FILE.close()
	OUTFILE.close()
	os.system( "mv ~temp " + fileName + ".UNIX" )

	print "UNIX"


def readFile( fileName, isVerbose ):
	numCR = 0
	numLF = 0
	numCRLF = 0

	FILE = open( fileName, "r" )

	char = FILE.read( 1 )
	last = 0

	while char:
		if char == chr(0x0a):			# LINE FEED
			numLF = numLF + 1
			if last == chr(0x0d):		# CR/LF
				numCRLF = numCRLF + 1
		elif char == chr(0x0d):			# CARRIAGE RETURN
			numCR = numCR + 1
		else:
			pass

		last = char
		char = FILE.read( 1 )

	FILE.close()

	fileType = "Undefined"

	if numCRLF > 0:
		print fileName, ": PC Format (CR/LF)"
		fileType = "PC"
	elif numCR > 0:
		if numLF == 0:
			print fileName, ": MAC Format (CR only)"
			fileType = "MAC"
		elif numCR > numLF:
			print fileName, ": mix of CR and LF... probably MAC Format"
		elif numCR == numLF:
			print fileName, ": mix of CR and LF... undetermined format"
		else:
			print fileName, ": mix of CR and LF... probably UNIX Format"
	elif numLF > 0:
		print fileName, ": UNIX Format (LF only)"
		fileType = "UNIX"
	else:
		print fileName, ": This file had no terminators"

	if isVerbose:
		print "CR:   ", numCR
		print "LF:   ", numLF
		print "CRLF: ", numCRLF

	return fileType

def usage():
	print '''\
	Usage: 	python lineterm.py [options] files

	Options:
		-h, --help    : Show this message
		-m, --mac     : Convert file(s) to Mac format (carriage returns)
		-p, --pc      : Convert file(s) to PC format (carriage return/linefeeds)
		-u, --unix    : Convert file(s) to Unix format (linefeeds)
		-v, --verbose : Show the number of CRs, LFs, and CR/LFs for the file(s)

	Arguments:
		files : any file or group of files (wildcards allowed)

	Note:
		Does not currently recurse directories or distinguish between
		binary and ASCII file types.  Creates a ~temp file in current
		directory when converting files.
	'''

if __name__ == "__main__":
	main()