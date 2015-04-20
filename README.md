Terraform Tools
===============

This repository defines the configuration for our OpenStack deployments.
It uses [Terraform][1] and [git-crypt][2].

[1]: <http://terraform.io/>
[2]: <https://www.agwa.name/projects/git-crypt/>

### Requirements

In order to use this repository, you need the following:

-   Terraform 0.4.2 or later (see the [installation instructions][3])

-   [OpenStack][4] userid with permissions for the relevant tenants (projects)

-   [Git][5] 1.7.2 or newer

-   [GPG/PGP key][6] added as a collaborator in `.git-crypt/keys/default/`

-   Binary git-crypt (Homebrew: `brew install git-crypt`)

    *or*

    C++ compiler (g++ preferred), OpenSSL develop+runtime libraries and `make`

[3]: <https://terraform.io/intro/getting-started/install.html>
[4]: <http://docs.openstack.org/user-guide/>
[5]: <http://git-scm.com/downloads>
[6]: <https://www.gnupg.org/gph/en/manual.html#AEN26>

If you will be making changes and committing to this repository, you also need:

-   Python (2 or 3) with virtualenv` (`virtualenvwrapper` or `pyenv`) installed

Git-crypt encryption
--------------------

After checking out this repository,
run the following commands to access encrypted data:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ which git-crypt || (git submodule init && cd git-crypt && make)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If this checks out and builds `git-crypt/git-crypt` (you may see compiler
warnings), install it into a directory in your `$PATH`.

Now you can unlock the repository with your GPG/PGP key:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ git-crypt unlock

You need a passphrase to unlock the secret key for
user: "Example User <user@example.com>"
4096-bit RSA key, ID 0x855F9E71BBEFB55E, created 2015-03-27
         (subkey on main key ID 0x482A696450DCF16F)

Your branch is up-to-date with 'origin/master'.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pre-commit setup
----------------

Before you make any changes to the repository,
you should enable the Git pre-commit hooks.
You can do this by (creating and) activating a virtualenv with
`mkvirtualenv`, `workon`, or `pyenv` and then running the
`./installprecommit.py` command.

### Adding files to the repository

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
