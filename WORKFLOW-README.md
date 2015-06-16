Terraform workflow
==================

This repository includes scripts for managing a terraform workflow in a single
Git repository using branches for independent environments. [Hashicorp
Atlas][1], with its GitHub integration and shared configuration and state, also
provides a workflow, but because our OpenStack infrastructure APIs are only
available via VPN, and our configuration repositories are in a self-hosted
GitLab, Atlas is not a practical option for us right now.[^1] We can and do use
Atlas to manage shared state (although Consul would work nearly as well, apart
from requiring additional setup on the back end).

[1]: <https://atlas.hashicorp.com/session>

[^1]: [See Mitchell Hashimoto's comment on the mailing list about this][2].

[2]: <https://groups.google.com/forum/#!msg/terraform-tool/GMHSxoAdyTM/GnT-iS-RZegJ>

The goal of the workflow is to try to capture in Git all the Terraform
**configuration** that is live (or has the possibility of going live), in order
to determine the source configuration for any given deployment, and to be able
to modify that in the future with Terraform. Note that the workflow does *not*
track Terraform **state** in Git — for disposable test environments, local state
files (separate for each environment) can be used; for longer-lived or shared
environments, Atlas shared state should be used to provide coordination among
multiple users.

Branching model
---------------

The **master** branch has only tools and documentation like this. Changes to
these files should be made on the **master** branch and then merged into
**common**, or if necessary, into specific environment branches. Eventually, we
may want to use a GitFlow development approach for these tools and their
documentation, in which case changes would be made on a feature or hot fix
branch, then merged into **develop** and/or **master** branches, but that is not
yet the case.

The **common** branch has common infrastructure definitions that apply to
multiple environments. Examples of this are (git-crypt encrypted) OpenStack
credentials and basic configuration like routers, networks, and security groups,
terraform variable maps that apply to multiple tenants, as well as encrypted
credentials for Atlas and the DNS provider (in our case, CloudFlare).

There are additional branches for each particular *environment* (which would
usually correspond to one OpenStack tenant, although one environment could
involve multiple tenants), and the environment-specific definitions are kept in
a `.tfvars` file. A particular branch may have multiple `.tfvars` files, but
typically only the one named after the current branch will be used.

Terraform’s `plan` subcommand uses a `terraform.tfvars` file if it exists and no
specific `‑var‑file` option is given. This implies that you should not use a
**terraform** branch unless you understand the implications of using that name
(the workflow plan script always uses `‑var‑file`, so it only affects direct use
of terraform commands).

Tools
-----

The command-line tools we use are the **tfplan** and **tfapply** scripts. These
scripts are front ends to the corresponding `terraform plan` and `terraform
apply` commands, but they perform some additional operations and checks that
enforce a basic Git discipline on the use of Terraform.

There is also a **tfremote** script for managing shared Terraform *state* (but
not configuration) in Atlas.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage: tfplan [‑destroy] [‑target=RESOURCE]... DEPLOY[.tfvars]
 (if DEPLOY is omitted, defaults to current branch 'myenv')

Usage: tfapply PLAN[.plan]
 (if PLAN is omitted, defaults to current branch 'myenv')

Usage: tfremote config [ORG_OR_USER/]DEPLOY
          | push | pull | status | disable
 (if DEPLOY is omitted, defaults to current branch 'myenv')
 (if ORG_OR_USER is omitted, defaults to 'example/')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a few additional options not documented in the tools’ usage messages
(see the **tfplan** source code for details).

Configuration files
-------------------

There are several different types of configuration files; some are standard
Terraform configuration files, but others are specific to our workflow.

### Terraform .tf files

These are the standard Terraform configuration source files; just the same as if
you were using the `terraform` command directly, *all* `.tf` files in the
current directory will be used as input. Because all of them are used as input
(whether they are committed or even staged to Git), the **tfplan** command
requires that they all be at least staged to the index, and the **tfapply**
command requires that they all be committed into the repository, in both cases
with no local modifications. This helps to make sure that all configuration is
captured in Git, at least at the moment that any changes are made.

### Terraform .tfvars file

Each environment has a `.tfvars` file that sets the values of Terraform
variables; this file is passed as the argument to the **tfplan** `‑var‑file`
option, and follows the syntax specified in the “**From a file**” section of the
[Input Variables][3] documentation:

[3]: <https://www.terraform.io/intro/getting-started/variables.html>

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
access_user = "foo"
tenant_name = "bar"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The use of `access_key` and `secret_key` in the official Terraform documentation
is an anti-pattern for the workflow, as it will lead to embedding confidential
or secret keys in the Terraform state file.

### Workflow .env files

In order to avoid capturing confidential information like access tokens or
private keys in the Terraform state file, the workflow allows it to be specified
in the POSIX process environment instead, where that is supported by the
provider.

### Workflow .tfenv file

This is used less often; since it is loaded last (after all $.env$ files are
loaded) it is often used to override settings for a particular environment. Just
as for the `.tfvars` file, only the file with a base name matching the PLAN or
DEPLOY argument (or current Git branch default) is used.

State files
-----------

### Local state

### Remote state

Confidential data
-----------------

Using the workflow
------------------

### Creating infrastructure

### Destroying infrastructure

### Focused usage with -target

Cloud-init
----------

### Cloud-init support scripts
