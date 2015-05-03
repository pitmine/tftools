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

-   Your [GPG/PGP key][6] added as a collaborator in `.git-crypt/keys/default/`

-   Binary git-crypt (Homebrew: `brew install git-crypt`)

    *or*

    C++ compiler (g++ preferred), OpenSSL develop+runtime libraries and `make`

[3]: <https://terraform.io/intro/getting-started/install.html>
[4]: <http://docs.openstack.org/user-guide/>
[5]: <http://git-scm.com/downloads>
[6]: <https://www.gnupg.org/gph/en/manual.html#AEN26>

If you will be making changes and committing to this repository, you also need:

-   Python (2 or 3) with virtualenv (`virtualenvwrapper`or`pyenv`) installed

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

Making changes
--------------

Before making changes to the Terraform configuration
or other files in this repository,
read the `PRE-COMMIT-README.md` file
for instructions on installing the Yelp pre-commit checks and
tips to avoid committing sensitive information to the Git repository.
