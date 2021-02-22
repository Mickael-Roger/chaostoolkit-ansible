 # Chaos toolkit Extension for using ansible as event execution tool

[![Python versions](https://img.shields.io/pypi/pyversions/chaostoolkit-ansible.svg)](https://www.python.org/)


This project is a collection of [actions][] and [probes][], gathered as an
extension to the [Chaos Toolkit][chaostoolkit].

[actions]: http://chaostoolkit.org/reference/api/experiment/#action
[probes]: http://chaostoolkit.org/reference/api/experiment/#probe
[chaostoolkit]: http://chaostoolkit.org


<h1 align="center">
    <img src="docs/images/ansible.png" alt="Ansible Icon" width="470" height="200">
</h1>


***Please NOTE*** This extension is in the _early_ stages of development and could need to be tested in different usa case scenario.

## Install

This package requires Python 3.5+

To be used from your experiment, this package must be installed in the Python
environment where [chaostoolkit][] already lives.
```
$ pip install -U chaostoolkit-ansible
```

## Principles

This chaos toolkit driver provides you an easy way to execute probe and/or actions using ansible modules. By using it, you can execute task, gather facts, ... on remote systems

## Usage

To use the probes and actions from this package, add the following to your
experiment file:

In JSON:
```json
{
"configuration": {
    "ansible_ssh_private_key": "/home/me/.ssh/mykey"
},
"steady-state-hypothesis": {
    "title": "Tests",
    "probes": [
        {
            "type": "probe",
            "name": "test-current-directory",
            "tolerance": {
              "type": "jsonpath",
              "path": "$.localhost.task",
              "expect": "/home/me"
            },
            "provider": {
                "type": "python",
                "module": "chaosansible.probes",
                "func": "chaosansible_probe",
                "arguments": {
                    "host_list": ["localhost", "myserver1"],
                    "facts": "yes",
                    "ansible": {
                        "module": "shell",
                        "args": "pwd"
                    }
                }
            }
        }
    ]
}
```

In YAML:
```yaml
---
steady-state-hypothesis:
  title: The current working directory must be /home/me
  probes:
  - type: probe
    name: test-current-directory
    tolerance:
      type: regex
      target: localhost.stdout
      pattern: /home/me
    provider:
      type: python
      module: chaosansible.probes
      func: chaosansible_probe
      arguments:
        host_list: ["localhost", "myserver1"]
        facts: "yes"
        ansible:
          module: shell
          args: pwd
method:
- type: action
  name: file-be-gone
  provider:
    type: python
    module: os
    func: remove
    arguments:
      path: some/file
  pauses:
    after: 5
- ref: file-must-exist
```

That's it!

## Detailled usage

Important: Each chaostoolkit-ansible action or probe run an ansible task on one or multiple target host. Values returned from the execution are in the form of a json result:

For example:
```json
{
  "target1": {
    "fact": "... -> JSON result of the ansible gather_facts",
    "task": "... -> String result containing the stdout value of the task result"
  },
  "target2": {
    "fact": "...",
    "task": "..."
  }
}
```


### Configuration block

The configuration block can be used to specify specific parameters to use. This block can be omit unless you really need to change default ansible parameters to run your exeperiment

Configuration variables that can be used by this driver are:

- **ansible_module_path**: Path of your ansible library
- **ansible_become_user**: Privileged user used when you call privilege escalation (root by default)
- **ansible_ssh_private_key**: Your ssh private key used to connect to targets (~/.ssh/id_rsa by default)
- **ansible_user**: User on target host used by ansible (current username by default)
- become_ask_pass

In case you need to change one/or many default configuration(s), you can specify your value using the configuration block

```json
"configuration": {
    "ansible_ssh_private_key": "/home/me/.ssh/mykey"
}
```

### Action/probe block

You can use function `chaosansible_run` and `chaosansible_probe` the same way.

```json

  "provider": {
      "type": "python",
      "module": "chaosansible.probes",
      "func": "chaosansible_run",
      "arguments": {
          "host_list": ["localhost", "myserver1"],
          "facts": true,
          "become": false,
          "run_once": false,
          "num_target": "all",
          "ansible": {
              "module": "shell",
              "args": "pwd"
          }
      }
  }

```

Arguments list (Most argument are classical ansible parameters):

| Argument | Type | Required | Default value | Description |
| --- | --- | --- | --- | --- |
| host_list | Array |  | localhost | List of host to use |
| facts | bool |  | false | Gather_facts |
| become | bool |  | false | Escalate privilege to run task |
| run_once | bool |  | false | Run the task only once on one target |
| num_target | str |  | all | "all" or "x" where x is an integer. Run the task to only x target among the host_list. Ideal to create random event |
| ansible | dict | * | - | Execute ansible task. Cf ansible dict format|


Ansible dict format:

```json
  "ansible": {
      "module": "ansible-module-name",
      "args": {
        "module-parameter1": "value1",
        "module-parameter2": "value2"
      }
  }
```


## Example of usage

### Delete /etc/hosts file on 2 random servers out of 5

```json
"method": [
    {
        "type": "action",
        "name": "delete-etc-hosts-file",
        "provider": {
            "type": "python",
            "module": "chaosansible.actions",
            "func": "chaosansible_run",
            "arguments": {
                "host_list": ["server1","server2","server3","server4","server5"],
                "num_target": "2",
                "become": true,
                "ansible": {
                    "module": "file",
                    "args": {
                        "path": "/etc/hosts",
                        "state": "absent"
                    }
                }
            }
        }
    }
]
```

### Run 100% cpu load on 3 server out of 5

```json
"method": [
    {
        "type": "action",
        "name": "delete-etc-hosts-file",
        "provider": {
            "type": "python",
            "module": "chaosansible.actions",
            "func": "chaosansible_run",
            "arguments": {
                "host_list": ["server1","server2","server3","server4","server5"],
                "num_target": "3",
                "ansible": {
                    "module": "shell",
                    "args": {
                        "cmd": "stress-ng --cpu 0 --cpu-method matrixprod -t 60s",
                    }
                }
            }
        }
    }
]
```



## Contribute

If you wish to contribute more functions to this package, you are more than
welcome to do so. Please, fork this project, make your changes following the
usual [PEP 8][pep8] code style, sprinkling with tests and submit a PR for
review.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/

The Chaos Toolkit projects require all contributors must sign a
[Developer Certificate of Origin][dco] on each commit they would like to merge
into the master branch of the repository. Please, make sure you can abide by
the rules of the DCO before submitting a PR.

[dco]: https://github.com/probot/dco#how-it-works

### Develop

If you wish to develop on this project, make sure to install the development
dependencies. But first, [create a virtual environment][venv] and then install
those dependencies.

[venv]: http://chaostoolkit.org/reference/usage/install/#create-a-virtual-environment

```console
$ pip install -r requirements-dev.txt -r requirements.txt
```

Then, point your environment to this directory:

```console
$ pip install -e .
```

Now, you can edit the files and they will be automatically be seen by your
environment, even when running from the `chaos` command locally.

### Test

To run the tests for the project execute the following:

```
$ pytest
```
