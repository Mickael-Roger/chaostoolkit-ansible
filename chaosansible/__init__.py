# -*- coding: utf-8 -*-

"""Top-level package for chaostoolkit-ansible."""

from typing import List

from chaoslib.discovery.discover import (
    discover_actions,
    discover_probes,
    initialize_discovery_result,
)
from chaoslib.types import DiscoveredActivities, Discovery
from logzero import logger

__version__ = "IN_PROGRESS"


def discover(discover_system: bool = True) -> Discovery:
    """
    Discover Ansible capabilities from this extension.
    """
    logger.info("Discovering capabilities from chaostoolkit-ansible")

    discovery = initialize_discovery_result(
        "chaostoolkit-ansible", __version__, "ansible"
    )
    discovery["activities"].extend(load_exported_activities())

    return discovery


###############################################################################
# Private functions
###############################################################################
def load_exported_activities() -> List[DiscoveredActivities]:
    """
    Extract metadata from actions and probes exposed by this extension.
    """
    activities = []
    activities.extend(discover_probes("chaosansible.probes"))
    activities.extend(discover_actions("chaosansible.actions"))

    return activities
