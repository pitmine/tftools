Terraform Tools
===============

This repository defines the configuration for our OpenStack deployments.
It uses [Terraform][1] and [git-crypt][2].

[1]: <http://terraform.io/>

[2]: <https://www.agwa.name/projects/git-crypt/>

### Requirements

In order to use this repository, you need the following:

-   Terraform 0.5 or later (see the [installation instructions][3])

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

Using Terraform
---------------

To ensure a consistent operational workflow,
two scripts are provided in this repository:
`tfplan` and `tfapply`.
They should be used in the following workflow:

1.  Update repository with `git pull --rebase` or `git pull`
2.  Modify or add Terraform '.tf' files and stage changes with `git add`
3.  Run `tfplan $DEPLOYMENT.tfvars` to generate a plan for a given tenant
4.  Review plan and repeat steps 2 and 3 until plan is correct
5.  Commit all terraform '.tf' configuration files with `git commit`
6.  Run `tfapply $DEPLOYMENT/2015*-*.plan` to apply plan to live configuration

Safety precautions
------------------

While the two phase plan—apply workflow helps prevent accidental termination
of vital infrastructure (e.g. OpenVPN gateway, Jira, Confluence)
we *really* want to be sure these are not destroyed inadvertently.
To prevent (almost) any possibility of accidental destruction,
we use the Nova `lock` facility to disable termination of these instances.

In a virtualenv with the OpenStack CLI loaded,
you can lock the *vpngw* instance with the command `nova lock vpngw`,
and unlock it with `nova unlock vpngw`.
Unfortunately the extension to [show the lock status][7] of an instance
is not available in the OpenStack release that we are using,
so there is no way to get a list of all locked instances.
Our general approach is to lock all officially provisioned instances
in the **int** tenant that lack numeric suffixes (e.g. `-1`, `-2`, `-3`, etc.).
We don’t currently lock instances in the operational tenants (dev1/qa1/...).

[7]: <https://blueprints.launchpad.net/nova/+spec/get-lock-status-of-instance>

The `lock` facility protects instances from deletion,
but does not protect volumes from deletion.
The existence of a snapshot of a volume prevents the volume from being deleted,
so we can prevent volume deletion by adding a local-exec provisioner
that run cinders to create a snapshot:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
cinder snapshot-create ${self.id}        \
  --display-name "${self.name}-protect"  \
  --display-description "Prevents deletion of ${self.name}"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
