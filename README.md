# makehuman_stable_python3

This is (for now) just a playground to see if it would be viable to backport the python3 port to stable

## Branches

There are four branches here:

* bitbucket-stable: This is the code as it looks right now in the stable branch at bitbucket
* bitbucket-default: This is the code as it looks right now in the default branch at bitbucket
* old_python3_for_unstable: This is a raw import of the code from the makehuman_python3 repo
* master: At the time of creating the repo, this is the same code as in bitbucket-stable. Master is the branch in which changes should be made (the other ones should only be touched if there is something new to import from bitbucket)

## Diffs

Current latest diffs are:

* [Changes from stable to default](http://www.jwp.se/files/stable_vs_unstable.diff): These are the difference between the "stable" and the "default" branches on bitbucket.
* [Changes from default to python3](http://www.jwp.se/files/unstable_vs_python3.diff): These are what was changed between bitbucket's default and Rob's python 3 repo.

The diffs are not updated dynamically.
