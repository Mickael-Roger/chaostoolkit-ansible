import json

import pytest
from chaosansible.probes import chaosansible_probe


# Test default values -> Empty fact
def test_chaosansible_probe_default():
    result = chaosansible_probe()

    jsonresult = json.loads(result)

    assert (
        type(jsonresult["localhost"]["facts"]) is dict
        and not jsonresult["localhost"]["facts"]
    )


# Test gather fact only
def test_chaosansible_probe_factsonly():
    result = chaosansible_probe(facts=True)

    jsonresult = json.loads(result)

    assert (
        type(jsonresult["localhost"]["facts"]) is dict
        and jsonresult["localhost"]["facts"]
    )


# Test id as root user
def test_chaosansible_probe_become_id():
    result = chaosansible_probe(become=True, ansible={"module": "shell", "args": "id"})

    jsonresult = json.loads(result)

    assert jsonresult["localhost"]["task"] == "uid=0(root) gid=0(root) groups=0(root)"
