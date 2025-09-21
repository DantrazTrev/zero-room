"""
ADP-RBAC: Role-Based Access Control using Logical Principles
=============================================================

Extends the Axiom of Distinction Protocol to support enterprise-grade
Role-Based Access Control through pure logical foundations.
"""

from .roles import Role, RoleHierarchy, RoleAssignment, RoleType
from .permissions import (
    Permission, PermissionSet, AccessPolicy,
    PermissionType, ResourceType
)
from .rbac_protocol import ADPRBACProtocol
from .policy_engine import (
    PolicyEngine, PolicyDecision, PolicyRequest, PolicyResponse
)

__all__ = [
    'Role', 'RoleHierarchy', 'RoleAssignment', 'RoleType',
    'Permission', 'PermissionSet', 'AccessPolicy',
    'PermissionType', 'ResourceType',
    'ADPRBACProtocol', 
    'PolicyEngine', 'PolicyDecision', 'PolicyRequest', 'PolicyResponse'
]