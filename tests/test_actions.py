import pytest

from chaoslib.exceptions import ActivityFailed, InvalidActivity

from chaosansible.actions import chaosansible_run, random_host
import json


# Test no ansible module name
def test_chaosansible_run_no_ansible_module():

    with pytest.raises(InvalidActivity) as excinfo:
        chaosansible_run(ansible={'args': 'ls'},
                                  host_list=['localhost'])

    assert "No ansible module defined" in str(excinfo.value)


# Test no ansible module name
def test_chaosansible_run_no_args():

    with pytest.raises(InvalidActivity) as excinfo:
        chaosansible_run(ansible={'module': 'shell'},
                                  host_list=['localhost'])

    assert "No ansible module args defined" in str(excinfo.value)

# Test random number of host
def test_random_host():

    host_list = ['host1', 'host2', 'host3']

    resultone = random_host(host_list, 1)
    resultthree = random_host(host_list, 3)

    with pytest.raises(InvalidActivity) as error4:
        random_host(host_list, 4)

    with pytest.raises(InvalidActivity) as error0:
        random_host(host_list, 0)
        
    with pytest.raises(InvalidActivity) as errorminus:
        random_host(host_list, -1)



    assert len(resultone) == 1 and set(resultone).issubset(host_list)
    assert len(resultthree) == 3 and set(resultthree).issubset(host_list)

    assert "Number of target is not correct" in str(error4.value)
    assert "Number of target is not correct" in str(error0.value)
    assert "Number of target is not correct" in str(errorminus.value)

