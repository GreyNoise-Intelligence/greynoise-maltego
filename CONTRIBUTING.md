Contribution Guide
===================

Welcome! Here you can find guidance on the best way to contribute to this repo.

Bugs Reports / Feature Requests
---------------------------------

We are happy to receive feature request or bug reports on the GitHub [issue tracker].

A bug report is most useful if it gives detailed, *reproducible* instructions. Additionally, it should include:

* the version.
* the exact arguments used.
* the exact config used.
* the output received.
* the output you expected instead.
* screenshots if available.

This will allow us to help you more quickly. A template is included via `.github/ISSUE_TEMPLATE/bug.md` as well.

Pull Requests
-------------

We appreciate PRs but encourage you to follow these guidelines for the reviewer:

* Provide context to the reviewer in the "Description" of the PR.
* Add/update tests for the code modified.
* PRs should be kept small and cohesive. If you're making bigger change, consider chunking up the PR into small pieces.

Github actions are used to run tests on the latest ubuntu:20.04 image.

Commits
-------

Please follow the usual guidelines for git commits: keep commits atomic, self-contained, and add a brief but clear
commit message. This [guide](https://chris.beams.io/posts/git-commit/) by Chris Beams is a good resource if you'd like
to learn more.

However, don't fret over this too much. You can also just accumulate commits without much thought for this rule. All
commits in a PR can be squashed into a single commit upon merging. It is still appreciated if the commit message
doesn't need to be rewritten.

Releases
--------

* Use tags for each Github release.
* Avoid checking in large files into the repo. Instead, attach files as artifacts to Github releases.
