# Pre requisites

Copy target private key to /home/ubuntu/privatekey.pem

Install nginx on all targets

# Installation

On ubuntu

```bash
sudo apt update
sudo apt install -y python3-pip
```

```bash
pip3 install chaostoolkit chaostoolkit-ansible chaostoolkit-lib[jsonpath]
```

# Experiment 

```yaml
---
title: Quickstart tutorial
description: Is using chaostoolkit-ansible difficult?
version: 0.1

configuration:
  ansible_ssh_private_key: "/home/ubuntu/privatekey.pem"   # The ssh private key file used to connect to targets

steady-state-hypothesis:
  title: All my targets are up and running                      # Steady state: Be sure all my nginx servers are running
  probes:
  - type: probe                                             
    name: demo-target-up
    provider:
      type: python
      module: chaosansible.probes
      func: chaosansible_probe
      arguments:
        host_list: ["10.1.1.94", "10.1.1.239", "10.1.1.110"]    # Please change with the ip list of your targets
        facts: True
        become: True
        ansible:                                                # Call the systemd ansible module to be sure all nginx services are started
          module: systemd
          args:
            name: nginx
            state: started

method:
- type: action                                                  # First action: Kill nginx
  name: demo-kill-nginx
  provider:
    type: python
    module: chaosansible.actions
    func: chaosansible_run
    arguments:
        host_list: ["10.1.1.94", "10.1.1.239", "10.1.1.110"]    # Please change with the ip list of your targets
        facts: False
        num_target: "2"                                         # This action will be executed to only 2 targets choosed randomly in the host_list
        ansible:
          module: systemd                                       # Call the systemd ansible module to stop nginx (on 2 targets)
          args:
            name: nginx
            state: stopped
  pauses:
    after: 30
    


- type: probe
  name: demo-nginx-is-killed
  tolerance:
    type: jsonpath
    path: "$.*.task"
    expect: HEALTH_WARN
  provider:
    type: python
    module: chaosansible.probes
    func: chaosansible_probe
    arguments:
      host_list: ["10.1.1.94", "10.1.1.239", "10.1.1.110"]    # Please change with the ip list of your targets
      facts: "no"
      run_once: true
      become: true
      ansible:
        module: shell
        args: podman exec -it ceph-tool ceph health



- type: action
  name: ceph-cluster-start-all-ceph-mon-process
  provider:
    type: python
    module: chaosansible.actions
    func: chaosansible_run
    arguments:
        host_list: ["172.24.1.10", "172.24.2.11", "172.24.3.12"]
        facts: "no"
        ansible:
          module: shell
          args: podman start ceph-mon
  pauses:
    after: 60

- ref: ceph-cluster-healthy

rollbacks:
- ref: ceph-cluster-start-all-ceph-mon-process
```