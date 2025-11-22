"""
Database models for MTCloud multi-tenant platform
"""

from .organization import Organization
from .client import Client
from .site import Site
from .user import User
from .device import Device, DeviceGroup, DeviceConfig, device_group_members
from .interface import Interface, InterfaceStat
from .metric import DeviceMetric
from .alert import Alert, AlertHistory
from .ai import AIInsight, AIQuery, MetricEmbedding

__all__ = [
    "Organization",
    "Client",
    "Site",
    "User",
    "Device",
    "DeviceGroup",
    "DeviceConfig",
    "device_group_members",
    "Interface",
    "InterfaceStat",
    "DeviceMetric",
    "Alert",
    "AlertHistory",
    "AIInsight",
    "AIQuery",
    "MetricEmbedding",
]
