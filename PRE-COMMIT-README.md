Pre-commit setup
================

This repository uses the pre-commit framework from Yelp (http://pre-commit.com)
to implement a number of pre-commit checks that can help avoid errors,
and to ensure a consistent code style.

Before you make any changes to the repository,
you should enable the Git pre-commit hooks.
You can do this by (creating and) activating a virtualenv with
`mkvirtualenv`, `workon`, or `pyenv` and then running the
`./installprecommit.py` command.

You must run these commands in *every* clone of this repository that you create
for them to have the pre-commit git hook.
The virtualenv does not need to be activated once the hook is installed,
but it must remain accessible at the same path.

If you *really* need to make a commit, and the pre-commit hooks are failing,
you can disable all hooks with `git commit --no-verify`,
but it is better to use the SKIP environment variable to just disable
more demanding checks, e.g. `SKIP=flake8,pylint git commit`.

Adding files to the repository
------------------------------

Before committing new files to this repository,
make sure there is no unencrypted sensitive information;
do this after adding new files with `git add` and before committing them
(and absolutely before pushing the commit).
The following command will list any unencrypted files staged for commit:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ git-crypt status $(git ls-files --cached)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For any unencrypted files with sensitive information,
unstage them from the index with `git reset HEAD -- $FILES`.
Then add the filenames or patterns to a `.gitattributes` file
(in the same directory or at the top level)
and git-crypt will encrypt them when you run `git add` again
to stage them to the index.
Re-run `git check-attr` afterwards to confirm
that all files with sensitive information are now being encrypted.

The pre-commit hooks detect some types of sensitive information (RSA/DSA keys)
but you should not rely on them to find all sensitive information.
