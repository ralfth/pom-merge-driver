pom-merge-driver
================

Custom Git merge driver for Maven's pom.xml.

If there is a conflict in the project version
of the branch to be merged, the conflict will
automatically be resolved by keeping our version except
for master branch to allow gitflow's release-finish,
hotfix-finish and feature-finish work better. Other
changes in the file will be merged as usual.

If Git configuration variable "merge.pommerge.keepmasterversion"
is set to true, the project version will always be kept
even on master branch.

Installation
-------------

git-config:
<pre>
[merge "pommerge"]
        name = A custom merge driver for Maven's pom.xml
        driver = $PATH_TO/mergepom.py %O %A %B
</pre>
"$PATH_TO" needs to be replaced with the full path to "mergepom.py".

.gitattributes
<pre>
pom.xml merge=pommerge
</pre>
