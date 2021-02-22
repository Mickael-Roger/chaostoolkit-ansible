import pytest

from chaoslib.exceptions import ActivityFailed, InvalidActivity

from chaosansible.actions import chaosansible_run
import json



# Test random
def test_chaosansible_run_random():
    result = chaosansible_run(ansible={'module':'shell', 'args': 'id'},
                                host_list=['localhost', '127.0.0.1'],
                                num_target="1")

    jsonresult = json.loads(result)

    print(jsonresult)

    assert len(jsonresult) == 1


# Test run failed
def test_chaosansible_run_failed():

    with pytest.raises(ActivityFailed) as excinfo:
        chaosansible_run(ansible={'module':'shell', 'args': 'fghf'},
                                  host_list=['localhost'])
    
    print(excinfo)

    assert "Failed to run ansible task" in str(excinfo.value)


# Test host unreachable
def test_chaosansible_run_unreachable():

    with pytest.raises(ActivityFailed) as excinfo:
        chaosansible_run(ansible={'module':'shell', 'args': 'ls'},
                                  host_list=['1.1.1.1'])
    
    print(excinfo)

    assert "At least one target is down" in str(excinfo.value)


# Testno ansible module name
def test_chaosansible_run_no_ansible_module():

    with pytest.raises(InvalidActivity) as excinfo:
        chaosansible_run(ansible={'args': 'ls'},
                                  host_list=['localhost'])
    
    print(excinfo)

    assert "No ansible module defined" in str(excinfo.value)


# Testno ansible module name
def test_chaosansible_run_no_args():

    with pytest.raises(InvalidActivity) as excinfo:
        chaosansible_run(ansible={'module': 'shell'},
                                  host_list=['localhost'])
    
    print(excinfo)

    assert "No ansible module args defined" in str(excinfo.value)