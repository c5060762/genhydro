#!/usr/bin/env python3
# hydrogen drumkit generator
'''
This program generates hydrogen drumkits from a directory
full of .wav files. It groups files by instrument name and velocity layer.
'''

#### LICENSE is GPLV3
'''
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import sys
import os
import shutil
import tarfile
import argparse
from collections import defaultdict

# get pwd so we have default name for kit
UNIXPATH = os.getcwd()
PATHARRAY = UNIXPATH.split('/')
CWDNUM = len(PATHARRAY) - 1
KITNAME = PATHARRAY[CWDNUM]

def getOptions(args):
	'''This function parses the command line arguments to generate options, and
	presents help text if requested with -h or --help'''
	parser = argparse.ArgumentParser(description="WAV file archive program")
	parser.add_argument("-s", "--src-dir",
						action="store",
						dest="src_dir",
						help="configure the location of the source directory, default is current directory")
	parser.add_argument("-d", "--dst-dir",
						action="store",
						dest="dst_dir",
						help="configure the location of the destination directory, default is current directory")
	options = parser.parse_args(args)
	# did we get no command line arg for src-dir?
	if options.src_dir is None:
		options.src_dir = os.getcwd()
	# otherwise, check that the passed in one exists and is a directory
	elif not os.path.exists(options.src_dir) or not os.path.isdir(options.src_dir):
		print("** ERROR ** source directory %s doesn't exist" % options.src_dir)
		sys.exit(-1)
	# did we get no command line arg for dst-dir?
	if options.dst_dir is None:
		options.dst_dir = options.src_dir
	return options

# get the command line options
options = getOptions(sys.argv[1:])
KITNAME = os.path.basename(options.src_dir)
print(KITNAME)  # debug statement

# now we have KITNAME as name for the kit
# lets build the head of the file
KITFILE = open("drumkit.xml", 'w')
KITFILE.write('<drumkit_info>')
KITFILE.write("\n")
KITFILE.write('<name>' + KITNAME + 'Kit</name>')
KITFILE.write('''
<author>Klaatu</author>
<info>This drum kit was created with genhydro.py on behalf of the Second Great Linux Multimedia Sprint. Find out more info at http://slackermedia.info/sprint. It is licensed under the GPLv3 meaning you are free to use it, share it, and modify it, even for commercial purposes, although any changes you make to the kit itself must be made available to everyone for free.</info>
<license>GPLv3</license>''')
KITFILE.write("\n")
KITFILE.write('<instrumentList>')
KITFILE.write("\n")
# Reload file list
INSTNAME = [x for x in os.listdir(UNIXPATH) if x.endswith('.WAV')]
INSTNAME.sort()

# Debugging: Print the list of found .WAV files
#print("Found .WAV files:", INSTNAME)

# Check if any instruments were found
if not INSTNAME:
	print("No .WAV files found in the source directory.")
	sys.exit(0)

# Group files by instrument name and velocity layer
instruments = defaultdict(list)

import re
from collections import defaultdict

# Group files by instrument name and velocity layer
instruments = defaultdict(list)

for filename in INSTNAME:
	# Split the filename to get the instrument name and velocity layer
	base_name, ext = os.path.splitext(filename)

	# Use regex to find the instrument name and the two-digit velocity layer
	match = re.match(r'^(.*?)(\d{1,2})$', base_name)

	if match:
		instrument_name = match.group(1)  # Everything before the numbers
		velocity_layer = int(match.group(2))  # The two-digit velocity layer
		instruments[instrument_name].append((velocity_layer, filename))

# lets parse the instruments into XML
INSTNUM = 0

for instrument_name, layers in instruments.items():
	KITFILE.write('<instrument>')
	KITFILE.write('<id>' + str(INSTNUM) + '</id>')
	KITFILE.write('<name>' + instrument_name + '</name>')
	KITFILE.write('''
			<volume>1</volume>
			<isMuted>false</isMuted>
			<pan_L>1</pan_L>
			<pan_R>1</pan_R>
			<randomPitchFactor>0</randomPitchFactor>
			<filterActive>false</filterActive>
			<filterCutoff>1</filterCutoff>
			<filterResonance>0</filterResonance>
			<Attack>0</Attack>
			<Decay>0</Decay>
			<Sustain>1</Sustain>
			<Release>1000</Release>''')  # Removed <exclude />

	# Sort layers by velocity layer to ensure correct order
	layers.sort(key=lambda x: x[0])
	num_layers = len(layers)
	max_velocity = 1.0
	difference = max_velocity / num_layers
	min_velocity = 0
	for i, (velocity_layer, filename) in enumerate(layers):
		#print(i,velocity_layer,filename)
		# Calculate min and max based on the number of layers
		max_velocity = round(velocity_layer / num_layers,2)
		#print(filename, min_velocity, max_velocity)
		#input()
		KITFILE.write('<layer>')
		KITFILE.write('<filename>' + filename + '</filename>')
		KITFILE.write(f'''
				<min>{min_velocity}</min>
				<max>{max_velocity}</max>
				<gain>1</gain>
				<pitch>0</pitch>
			</layer>''')
		min_velocity = round((velocity_layer + difference) / num_layers,2)
		if(min_velocity == max_velocity):
			min_velocity = round((velocity_layer + 2*difference) / num_layers,2)
	KITFILE.write('</instrument>')
	INSTNUM += 1

# that should be all the instruments now
# so it's time to close the XML tree
KITFILE.write('</instrumentList>')
KITFILE.write('</drumkit_info>')
KITFILE.close()
print('XML file created successfully.')  # debugging

# i guess we should package it up now
os.makedirs(KITNAME + 'Kit', exist_ok=True)
DIRDEST = KITNAME + 'Kit'

# Move .WAV files to the destination directory
for DRUMFILE in os.listdir(UNIXPATH):
	if DRUMFILE.endswith(".WAV"):
		SRCFILE = os.path.join(UNIXPATH, DRUMFILE)
		DESTFILE = os.path.join(DIRDEST, DRUMFILE)
		shutil.move(SRCFILE, DESTFILE)

#Copy the XML file to the destination directory
shutil.copy("drumkit.xml", DIRDEST)

# Tar up the files in the destination directory
with tarfile.open(name=DIRDEST + '.h2drumkit', mode="w:gz") as tarfile_handle:
	tarfile_handle.add(DIRDEST, arcname=os.path.basename(DIRDEST))

print('Drumkit packaged successfully as ' + DIRDEST + '.h2drumkit')

