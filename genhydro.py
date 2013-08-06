#!/usr/bin/env python
# hydrogen drumkit generator
'''
This program generates hydrogen drumkits from a directory
full of .flac files. Currently it's quite specific to that
although in the future i will try to breakout the file format
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

# get pwd so we have default name for kit

UNIXPATH = os.getcwd()
PATHARRAY = UNIXPATH.split('/')
CWDNUM = len(PATHARRAY)-1
KITNAME = PATHARRAY[CWDNUM]
# print(KITNAME) ## debug statement

def getOptions(args):
    '''This function parses the command line arguments to generate options, and 
    presents help text if requested with -h or --help'''
    parser = argparse.ArgumentParser(description="Flac file archive program")
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
        print "** ERROR ** source directory %s doesn't exist" % options.src_dir
        sys.exit(-1)
    # did we get no command line arg for dst-dir?
    if options.dst_dir is None:
        options.dst_dir = options.src_dir
    return options

# get the command line options
options = getOptions(sys.argv[1:])
KITNAME = os.path.basename(options.src_dir)
print(KITNAME) ## debug statement

# now we have KITNAME as name for the kit
# lets build the head of the file

KITFILE = open("drumkit.xml", 'w')
KITFILE.write('<drumkit_info>')
KITFILE.write('<name>'+KITNAME+'Kit</name>')
KITFILE.write('''
<author>Klaatu</author>
<info>This drum kit was created with genhydro.py on behalf of the Second Great Linux Multimedia Sprint. Find out more info at http://slackermedia.info/sprint. It is licensed under the GPLv3 meaning you are free to use it, share it, and modify it, even for commercial purposes, although any changes you make to the kit itself must be made available to everyone for free.</info>
<license>GPLv3</license>''')
KITFILE.write('<instrumentList>')

# the basic info of the drumkit exists.
# now let's loop through each sound file in pwd
# and add them as instruments

INSTNUM=0
# reload file list
INSTNAME = filter(lambda x: x.endswith('.flac'), os.listdir(UNIXPATH))
INSTNAME.sort()
#print(INSTNAME) #### debug statement
# lets parse the instruments into XML

for DRUMTYPE in INSTNAME:
    #    print(DRUMTYPE)    #### debug statement
    KITFILE.write('<instrument>')
    KITFILE.write('<id>'+str(INSTNUM)+'</id>')
    KITFILE.write('<name>'+os.path.splitext(INSTNAME[INSTNUM])[0]+'</name>')
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
            <Release>1000</Release>
            <exclude />''')
    KITFILE.write('<layer>')
    KITFILE.write('<filename>'+INSTNAME[INSTNUM]+'</filename>')
    KITFILE.write('''
                <min>0</min>
                <max>1</max>
                <gain>1</gain>
                <pitch>0</pitch>
            </layer>
        </instrument>''')
    # increment instrument number
    INSTNUM=INSTNUM+1
 # that should be all the instruments now
# so its time to close the XML tree
KITFILE.write('</instrumentList>')
KITFILE.write('</drumkit_info>')
KITFILE.close()
print('xml closing') ## debugging

# i guess we should package it up now
# this is really clunky
# i know there is a better way to move files

os.makedirs(KITNAME+'Kit')
# DIRSRC = "."
DIRDEST = KITNAME+'Kit'

# print(DIRSRC)  ##  debug statements
# print(DIRDEST) ##

for DRUMFILE in os.listdir(UNIXPATH):
	if DRUMFILE.endswith(".flac"):
		SRCFILE = os.path.join(UNIXPATH, DRUMFILE)
		DESTFILE = os.path.join(DIRDEST, DRUMFILE)
		shutil.move(SRCFILE, DESTFILE)

for DRUMFILE in os.listdir(UNIXPATH):
	if DRUMFILE.endswith(".xml"):
		SRCFILE = os.path.join(UNIXPATH, DRUMFILE)
		DESTFILE = os.path.join(DIRDEST, DRUMFILE)
		shutil.copy(SRCFILE, DESTFILE)

### gnutar is randomly closing before all the files are written completely
### so i will do this step in a shell script instead until i figure out 
### whats going on 
#GNUTAR = tarfile.open(name=DIRDEST+'.h2drumkit', mode="w:gz")
#GNUTAR.add(DIRDEST)
#GNUTAR.close()

#patch by Doug
# tar up the files in the destination directory    
tarfile_handle = tarfile.open(name=DIRDEST + '.h2drumkit', mode="w:gz")
tarfile_handle.add(DIRDEST)
tarfile_handle.close()
