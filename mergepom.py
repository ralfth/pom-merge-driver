#! /usr/bin/env python3

# Copyright 2013 Ralf Thielow <ralf.thielow@gmail.com>
# Licensed under the GNU GPL version 2.

import sys, subprocess, shlex, codecs, re
import xml.dom.minidom as dom

def get_enc(line, default):
        m = re.search('encoding=[\'"](.*?)[\'"]', line)
        if m is not None:
                return m.group(1)
        return default


def change_tag(old_tag, new_tag, cont):
        return cont.replace("<tag>" + old_tag + "</tag>",
                            "<tag>" + new_tag + "</tag>")

def get_tag(f):
        try:
                tree = dom.parse(f)
                matchingNodes = tree.getElementsByTagName("tag")[0] if tree.getElementsByTagName("tag") else None
                if matchingNodes is not None and matchingNodes.firstChild is not None:
                        return matchingNodes.firstChild.nodeValue
                return None
        except Exception as e:
                print(e)
                print(sys.argv[0] + ': error while parsing pom.xml')
                return None

def change_version(old_version, new_version, cont):
        return cont.replace("<version>"+old_version+"</version>",
                            "<version>" + new_version + "</version>")

def get_project_version(f):
        try:
                tree = dom.parse(f)
                version = None
                parent_version = None
                for entry in tree.documentElement.childNodes:
                        if entry.nodeName == "version":
                                version = entry.firstChild.data
                        if entry.nodeName == "parent":
                                for entry2 in entry.childNodes:
                                        if entry2.nodeName == 'version':
                                                parent_version = entry2.firstChild.data

                if version is not None:
                        # version has a priority over parent version
                        return version
                else:
                        # may return None
                        return parent_version
        except:
                print(sys.argv[0] + ': error while parsing pom.xml')
                return None

if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Wrong number of arguments.")
        sys.exit(-1)

ancestor_version = get_project_version(sys.argv[1])
current_branch_version = get_project_version(sys.argv[2])
other_branch_version = get_project_version(sys.argv[3])

current_tag = get_tag(sys.argv[2])
other_tag = get_tag(sys.argv[3])
have_tags = True if current_tag is not None and other_tag is not None else False

# change current version in order to avoid merge conflicts
if (
        current_branch_version is not None
        and other_branch_version is not None
        and ancestor_version is not None
        and current_branch_version != other_branch_version
        and other_branch_version != ancestor_version
):
        with open(sys.argv[2], mode='r', encoding='utf-8') as f:
                enc = get_enc(f.readline(), 'utf-8')
        with codecs.open(sys.argv[2], 'r', enc) as f:
                other = f.read()
        other = change_version(current_branch_version, other_branch_version, other)
        other = change_tag(current_tag, other_tag, other) if have_tags else other
        with codecs.open(sys.argv[2], 'w', enc) as f:
                f.write(other)

cmd = "git merge-file -p -L mine -L base -L theirs " + sys.argv[2] + " " + sys.argv[1] + " " + sys.argv[3]
p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
git_merge_res = p.communicate()[0]
ret = p.returncode

enc = 'utf-8'
try:
        git_merge_res_str = git_merge_res.decode(enc)
except:
        # utf-8 failed, try again with iso-8859-1
        enc = 'iso-8859-1'
        git_merge_res_str = git_merge_res.decode(enc)

oenc = get_enc(git_merge_res_str.splitlines()[0], enc)
if enc != oenc:
        enc = oenc
        git_merge_res_str = git_merge_res.decode(enc)

cmd = "git rev-parse --abbrev-ref HEAD"
p = subprocess.check_output(shlex.split(cmd))
branch = p.strip().decode('utf-8')

cmd = "git config --get --bool merge.pommerge.keepmasterversion"
p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
val = p.communicate()[0]
val = val.strip().decode('utf-8')

keep = False
if (p.returncode == 0 and val == 'true'):
        keep = True

# When rebasing, we always want to keep the other_branch_version (branch being rebased)
# Unless one has explicitly checked-out by revision-id, branch should only be 'HEAD' when rebasing
if (branch == 'HEAD'):
        print('Rebasing pom version ' + other_branch_version + ' into ' + branch)

# revert pom project version on current branch, unless in master. Allows for gitflow release-finish, hotfix-finish, and feature-finish to work better
elif (current_branch_version is not None and (keep or branch != 'master')):
        print('Merging pom version ' + other_branch_version + ' into ' + branch + '. Keeping version ' + current_branch_version)
        git_merge_res_str = change_version(other_branch_version, current_branch_version, git_merge_res_str)
        print('Merging pom scm tag ' + other_tag + ' into ' + branch + '. Keeping scm tag ' + current_tag) if have_tags else 0
        git_merge_res_str = change_tag(other_tag, current_tag, git_merge_res_str) if have_tags else git_merge_res_str

with codecs.open(sys.argv[2], 'w', enc) as f:
        f.write(git_merge_res_str)

sys.exit(ret)
