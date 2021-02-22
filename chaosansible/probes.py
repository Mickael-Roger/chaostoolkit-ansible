from chaosansible.actions import chaosansible_run

__all__ = ["chaosansible_probe"]

# Because getting a probe with ansible is the same than running an ansible task
chaosansible_probe = chaosansible_run
