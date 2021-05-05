from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from chaoslib.exceptions import FailedActivity, InvalidActivity
from chaoslib.types import Configuration, Secrets

import json
import shutil
from random import randint

import ansible.constants as C
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible import context

__all__ = ["chaosansible_run"]


class ResultsCollectorJSONCallback(CallbackBase):
    """
    A callback plugin used to stored results
    """

    def __init__(self, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):

        chost = result._host.get_name()

        try:
            self.host_ok[chost]
        except Exception:
            self.host_ok[chost] = {}

        try:
            # Facts
            if result._task._ds['name'] == 'facts':
                self.host_ok[chost]['facts'] = result._result['ansible_facts']

            # Task results
            elif result._task._ds['name'] == 'task':
                self.host_ok[chost]['task'] = result._result['stdout']
        except Exception:
            pass

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result


def random_host(host_list: list,
                num_target: int):

    new_host_list = host_list[:]

    if num_target <= 0 or num_target > len(new_host_list):
        raise InvalidActivity('Number of target is not correct')

    try:
        nb_remove_target = len(new_host_list) - int(num_target)

        if nb_remove_target > 0:
            for i in range(nb_remove_target):
                rand = randint(0, len(new_host_list)-1)
                new_host_list.pop(rand)

    except Exception:
        raise InvalidActivity('Could not generate host list')

    return new_host_list


def chaosansible_run(host_list: list = ('localhost'),
                     configuration: Configuration = None,
                     facts: bool = False,
                     become: bool = False,
                     run_once: bool = False,
                     ansible: dict = {},
                     num_target: str = 'all',
                     secrets: Secrets = None):

    """
    Run a task through ansible and eventually gather facts from host
    """

    # Check for correct inputs
    if ansible:
        if ansible.get('module') is None:
            raise InvalidActivity('No ansible module defined')

        if ansible.get('args') is None:
            raise InvalidActivity('No ansible module args defined')

    configuration = configuration or {}

    # Ansible configuration elements
    module_path = configuration.get('ansible_module_path') or None
    become_user = configuration.get('ansible_become_user') or None
    ssh_key_path = configuration.get('ansible_ssh_private_key') or None
    ansible_user = configuration.get('ansible_user') or None
    become_ask_pass = configuration.get('become_ask_pass') or None

    context.CLIARGS = ImmutableDict(connection='smart',
                                    verbosity=0,
                                    module_path=module_path,
                                    forks=10, become=become,
                                    become_method='sudo',
                                    become_user=become_user,
                                    check=False,
                                    diff=False,
                                    private_key_file=ssh_key_path,
                                    remote_user=ansible_user)

    # Update host_list regarding the number of desired target.
    # Need to generate a new host-list because after being update
    # and will be used later
    if num_target != 'all':
        new_host_list = random_host(host_list, int(num_target))
    else:
        new_host_list = host_list[:]

    # Create an inventory
    sources = ','.join(new_host_list)
    if len(new_host_list) == 1:
        sources += ','

    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=sources)

    # Instantiate callback for storing results
    results_callback = ResultsCollectorJSONCallback()

    variable_manager = VariableManager(loader=loader, inventory=inventory)
    if become_ask_pass:
        passwords = dict(become_pass=become_ask_pass)
    else:
        passwords = None

    # Ansible taskmanager
    tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords=passwords,
        stdout_callback=results_callback,
        run_additional_callbacks=False,
    )

    # Ansible playbook
    play_source = dict(
        name="Ansible Play",
        hosts=new_host_list,
        gather_facts=facts,
        tasks=[
            dict(name='facts', action=dict(module='debug',
                                           args=dict(var='ansible_facts'))),
        ]
    )

    # In cas we only want to gather facts
    if ansible:
        module = ansible.get('module')
        args = ansible.get('args')
        play_source['tasks'].append(dict(name='task',
                                         run_once=run_once,
                                         action=dict(module=module,
                                                     args=args),
                                         register='shell_out'))

    # Create an ansible playbook
    play = Play().load(play_source,
                       variable_manager=variable_manager,
                       loader=loader)

    # Run it
    try:
        result = tqm.run(play)
    finally:
        tqm.cleanup()
        if loader:
            loader.cleanup_all_tmp_files()

    # Remove ansible tmpdir
    shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    if len(results_callback.host_failed) > 0:
        print("Ansible error(s): ")
        for error in results_callback.host_failed:
            print(results_callback.host_failed[error].__dict__)

        raise FailedActivity("Failed to run ansible task")

    elif len(results_callback.host_unreachable) > 0:
        print("Unreachable host(s): ")
        for error in results_callback.host_unreachable:
            print(error)
            
        raise FailedActivity("At least one target is down")

    else:
        results = {}

        for host, result in results_callback.host_ok.items():
            results[host] = result

        return json.dumps(results)
