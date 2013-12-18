#! /usr/bin/env python

# Copyright 2013 Ralf Thielow <ralf.thielow@gmail.com>
# Licensed under the GNU GPL version 2.

import sys, subprocess, shlex
import xml.dom.minidom as dom

def change_version(old_version, new_version, cont):
	return cont.replace("<version>"+old_version+"</version>",
			"<version>" + new_version + "</version>")

def get_project_version(f):
	try:
		tree = dom.parse(f)
		for entry in tree.documentElement.childNodes:
			if entry.nodeName == "version":
				return entry.firstChild.data
			if entry.nodeName == "parent":
				for entry2 in entry.childNodes:
					if entry2.nodeName == 'version':
						return entry2.firstChild.data
		return 'unknown'
	except:
		print sys.argv[0] + ': error while parsing pom.xml'
		return 'unknown'

if len(sys.argv) < 4 or len(sys.argv) > 5:
	print "Wrong number of arguments."
	sys.exit(-1)

ancestor_version = get_project_version(sys.argv[1])
current_branch_version = get_project_version(sys.argv[2])
other_branch_version = get_project_version(sys.argv[3])

if (current_branch_version != 'unknown' and
		other_branch_version != 'unknown' and
		ancestor_version != 'unknown' and
		current_branch_version != other_branch_version and
		other_branch_version != ancestor_version):
	f = open(sys.argv[2],'r')
	other = f.read()
	f.close()
	other = change_version(current_branch_version, other_branch_version, other)
	f = open(sys.argv[2],'w')
	f.write(other)
	f.close()

cmd = "git merge-file -p -L mine -L base -L theirs " + sys.argv[2] + " " + sys.argv[1] + " " + sys.argv[3]
p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
git_merge_res = p.communicate()[0]
ret = p.returncode

f = open(sys.argv[2],'w')
f.write(git_merge_res)
f.close

sys.exit(ret)
