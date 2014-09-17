#! /usr/bin/env python

# Copyright 2013 Ralf Thielow <ralf.thielow@gmail.com>
# Licensed under the GNU GPL version 2.

import sys, subprocess, shlex, codecs
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
		print(sys.argv[0] + ': error while parsing pom.xml')
		return 'unknown'

if len(sys.argv) < 4 or len(sys.argv) > 5:
	print("Wrong number of arguments.")
	sys.exit(-1)

ancestor_version = get_project_version(sys.argv[1])
current_branch_version = get_project_version(sys.argv[2])
other_branch_version = get_project_version(sys.argv[3])

# change current version in order to avoid merge conflicts
if (current_branch_version != 'unknown' and
		other_branch_version != 'unknown' and
		ancestor_version != 'unknown' and
		current_branch_version != other_branch_version and
		other_branch_version != ancestor_version):
	f = codecs.open(sys.argv[2],'r', 'utf-8')
	other = f.read()
	f.close()
	other = change_version(current_branch_version, other_branch_version, other)
	f = codecs.open(sys.argv[2],'w', 'utf-8')
	f.write(other)
	f.close()

cmd = "git merge-file -p -L mine -L base -L theirs " + sys.argv[2] + " " + sys.argv[1] + " " + sys.argv[3]
p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
git_merge_res = p.communicate()[0]
ret = p.returncode

git_merge_res_str = git_merge_res.strip().decode('utf-8')

cmd2 = "git rev-parse --abbrev-ref HEAD"
p2 = subprocess.check_output(shlex.split(cmd2))
branch = p2.strip().decode('utf-8')

# revert pom project version on current branch, unless in master. Allows for gitflow release-finish, hotfix-finish, and feature-finish to work better
if (branch != 'master'):
	print('Merging pom version ' + other_branch_version + ' into ' + branch + '. Keeping version ' + current_branch_version)
	git_merge_res_str = change_version(other_branch_version, current_branch_version, git_merge_res_str)

f = codecs.open(sys.argv[2],'w', 'utf-8')
f.write(git_merge_res_str)
f.close

sys.exit(ret)