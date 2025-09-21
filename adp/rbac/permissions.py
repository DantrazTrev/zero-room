"""
Permission Framework for ADP-RBAC
==================================

Implements permissions as logical predicates that can be evaluated
using the fundamental principles of the ADP protocol.
"""

from typing import Set, Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time

from ..core.realms import LogicalState, SharedRealm
from ..foundation.axioms import SharedAxiom


class PermissionType(Enum):
    """Types of permissions in the system."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    AUDIT = "audit"
    DELEGATE = "delegate"
    ADMIN = "admin"


class ResourceType(Enum):
    """Types of resources that can be accessed."""
    DATA = "data"
    CONFIG = "config"
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    AUDIT_LOG = "audit_log"
    SYSTEM = "system"


@dataclass(frozen=True)
class Permission:
    """
    Represents a permission in the system.
    
    Permissions are SHARED constructs that define what actions
    can be performed on resources. The actual authorization
    decisions are made using logical evaluation.
    """
    name: str
    permission_type: PermissionType
    resource_type: ResourceType
    resource_pattern: str  # Pattern for resource matching (e.g., "user:*", "data:finance/*")
    conditions: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    
    def __hash__(self):
        return hash((self.name, self.permission_type, self.resource_type))
    
    def matches_resource(self, resource: str) -> bool:
        """
        Check if this permission matches a specific resource.
        
        Uses logical pattern matching.
        
        Args:
            resource: Resource identifier to check
            
        Returns:
            True if permission applies to resource
        """
        import fnmatch
        return fnmatch.fnmatch(resource, self.resource_pattern)
    
    def evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate permission conditions against a context.
        
        Uses logical evaluation of predicates.
        
        Args:
            context: Context containing values for condition evaluation
            
        Returns:
            True if all conditions are satisfied
        """
        for key, expected_value in self.conditions.items():
            if key not in context:
                return False
                
            actual_value = context[key]
            
            # Handle different condition types
            if callable(expected_value):
                if not expected_value(actual_value):
                    return False
            elif actual_value != expected_value:
                return False
                
        return True
    
    def to_logical_state(self) -> LogicalState:
        """Convert permission to logical state."""
        return LogicalState(content={
            'type': 'permission',
            'name': self.name,
            'permission_type': self.permission_type.value,
            'resource_type': self.resource_type.value,
            'resource_pattern': self.resource_pattern,
            'conditions': str(self.conditions),
            'description': self.description
        })


@dataclass
class PermissionSet:
    """
    A collection of permissions that can be evaluated together.
    
    Permission sets use logical conjunction (AND) and disjunction (OR)
    to combine individual permissions.
    """
    name: str
    permissions: Set[Permission] = field(default_factory=set)
    require_all: bool = True  # True = AND, False = OR
    
    def add_permission(self, permission: Permission) -> None:
        """Add a permission to the set."""
        self.permissions.add(permission)
        
    def remove_permission(self, permission: Permission) -> None:
        """Remove a permission from the set."""
        self.permissions.discard(permission)
        
    def evaluate(self, action: PermissionType, resource: str, 
                context: Dict[str, Any]) -> bool:
        """
        Evaluate if an action on a resource is allowed.
        
        Uses logical evaluation based on require_all setting.
        
        Args:
            action: Action to perform
            resource: Resource to access
            context: Context for condition evaluation
            
        Returns:
            True if action is allowed
        """
        matching_permissions = [
            p for p in self.permissions
            if p.permission_type == action and p.matches_resource(resource)
        ]
        
        if not matching_permissions:
            return False
            
        results = [
            p.evaluate_conditions(context) 
            for p in matching_permissions
        ]
        
        if self.require_all:
            return all(results)  # Logical AND
        else:
            return any(results)  # Logical OR
            
    def to_logical_state(self) -> LogicalState:
        """Convert permission set to logical state."""
        return LogicalState(content={
            'type': 'permission_set',
            'name': self.name,
            'permission_count': len(self.permissions),
            'require_all': self.require_all
        })


class AccessPolicy:
    """
    Defines access control policies using logical rules.
    
    Policies combine roles and permissions to make authorization decisions.
    """
    
    def __init__(self, name: str, shared_realm: SharedRealm):
        """
        Initialize access policy.
        
        Args:
            name: Policy name
            shared_realm: Reference to shared realm
        """
        self.name = name
        self._shared_realm = shared_realm
        self._role_permissions: Dict[str, PermissionSet] = {}
        self._default_permissions = PermissionSet("default", require_all=False)
        
        # Initialize default policies
        self._initialize_default_policies()
        
    def _initialize_default_policies(self):
        """Initialize default role-permission mappings."""
        
        # Super Admin - all permissions
        super_admin_perms = PermissionSet("super_admin_permissions")
        for perm_type in PermissionType:
            for resource_type in ResourceType:
                perm = Permission(
                    name=f"{perm_type.value}_{resource_type.value}",
                    permission_type=perm_type,
                    resource_type=resource_type,
                    resource_pattern="*",
                    description=f"Super admin {perm_type.value} on {resource_type.value}"
                )
                super_admin_perms.add_permission(perm)
        self._role_permissions["super_admin"] = super_admin_perms
        
        # Admin - most permissions except system
        admin_perms = PermissionSet("admin_permissions")
        for perm_type in [PermissionType.CREATE, PermissionType.READ, 
                         PermissionType.UPDATE, PermissionType.DELETE]:
            for resource_type in [ResourceType.DATA, ResourceType.CONFIG, 
                                 ResourceType.USER, ResourceType.ROLE]:
                perm = Permission(
                    name=f"{perm_type.value}_{resource_type.value}",
                    permission_type=perm_type,
                    resource_type=resource_type,
                    resource_pattern="*",
                    description=f"Admin {perm_type.value} on {resource_type.value}"
                )
                admin_perms.add_permission(perm)
        self._role_permissions["admin"] = admin_perms
        
        # Auditor - read and audit permissions
        auditor_perms = PermissionSet("auditor_permissions")
        for resource_type in ResourceType:
            read_perm = Permission(
                name=f"read_{resource_type.value}",
                permission_type=PermissionType.READ,
                resource_type=resource_type,
                resource_pattern="*",
                description=f"Auditor read on {resource_type.value}"
            )
            auditor_perms.add_permission(read_perm)
            
            if resource_type == ResourceType.AUDIT_LOG:
                audit_perm = Permission(
                    name=f"audit_{resource_type.value}",
                    permission_type=PermissionType.AUDIT,
                    resource_type=resource_type,
                    resource_pattern="*",
                    description=f"Auditor audit on {resource_type.value}"
                )
                auditor_perms.add_permission(audit_perm)
        self._role_permissions["auditor"] = auditor_perms
        
        # Editor - create, read, update on data
        editor_perms = PermissionSet("editor_permissions")
        for perm_type in [PermissionType.CREATE, PermissionType.READ, PermissionType.UPDATE]:
            perm = Permission(
                name=f"{perm_type.value}_data",
                permission_type=perm_type,
                resource_type=ResourceType.DATA,
                resource_pattern="*",
                description=f"Editor {perm_type.value} on data"
            )
            editor_perms.add_permission(perm)
        self._role_permissions["editor"] = editor_perms
        
        # User - read and limited update
        user_perms = PermissionSet("user_permissions")
        user_perms.add_permission(Permission(
            name="read_data",
            permission_type=PermissionType.READ,
            resource_type=ResourceType.DATA,
            resource_pattern="*",
            description="User read on data"
        ))
        user_perms.add_permission(Permission(
            name="update_own_data",
            permission_type=PermissionType.UPDATE,
            resource_type=ResourceType.DATA,
            resource_pattern="user:${entity_id}/*",
            conditions={"owner": lambda x: x == "${entity_id}"},
            description="User update on own data"
        ))
        self._role_permissions["user"] = user_perms
        
        # Viewer - read only
        viewer_perms = PermissionSet("viewer_permissions")
        viewer_perms.add_permission(Permission(
            name="read_data",
            permission_type=PermissionType.READ,
            resource_type=ResourceType.DATA,
            resource_pattern="*",
            description="Viewer read on data"
        ))
        self._role_permissions["viewer"] = viewer_perms
        
        # Register all permission sets in shared realm
        for role, perm_set in self._role_permissions.items():
            self._shared_realm.add_method(perm_set.to_logical_state())
            
    def get_role_permissions(self, role: str) -> Optional[PermissionSet]:
        """Get permissions for a specific role."""
        return self._role_permissions.get(role)
        
    def add_role_permissions(self, role: str, permissions: PermissionSet) -> None:
        """Add permissions for a role."""
        self._role_permissions[role] = permissions
        self._shared_realm.add_method(permissions.to_logical_state())
        
    def check_permission(self, roles: List[str], action: PermissionType,
                        resource: str, context: Dict[str, Any]) -> bool:
        """
        Check if a set of roles has permission for an action.
        
        Uses logical evaluation to determine authorization.
        
        Args:
            roles: List of roles to check
            action: Action to perform
            resource: Resource to access
            context: Context for evaluation
            
        Returns:
            True if permission is granted
        """
        # Check each role's permissions
        for role in roles:
            perm_set = self._role_permissions.get(role)
            if perm_set and perm_set.evaluate(action, resource, context):
                return True
                
        # Check default permissions
        if self._default_permissions.evaluate(action, resource, context):
            return True
            
        return False
        
    def create_permission_proof(self, entity_id: str, roles: List[str],
                              action: PermissionType, resource: str) -> LogicalState:
        """
        Create a proof that an entity has permission for an action.
        
        This proof can be verified without revealing the entity's
        exclusive role assignments.
        
        Args:
            entity_id: Entity requesting permission
            roles: Entity's roles
            action: Action to perform
            resource: Resource to access
            
        Returns:
            Permission proof
        """
        # Check if permission is granted
        context = {"entity_id": entity_id}
        has_permission = self.check_permission(roles, action, resource, context)
        
        # Create proof
        proof_content = {
            'type': 'permission_proof',
            'entity_id': entity_id,
            'action': action.value,
            'resource': resource,
            'granted': has_permission,
            'timestamp': time.time(),
            'roles_hash': hash(tuple(sorted(roles)))  # Hash roles to maintain privacy
        }
        
        return LogicalState(content=proof_content)


class PermissionEvaluator:
    """
    Evaluates permissions using logical principles.
    
    Combines the axioms of the ADP with permission logic.
    """
    
    def __init__(self, shared_axioms: SharedAxiom, policy: AccessPolicy):
        """
        Initialize permission evaluator.
        
        Args:
            shared_axioms: Reference to shared axioms
            policy: Access policy to use
        """
        self._axioms = shared_axioms
        self._policy = policy
        self._evaluation_cache: Dict[str, bool] = {}
        
    def evaluate_access(self, entity_id: str, roles: List[str],
                       action: PermissionType, resource: str,
                       context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Evaluate if access should be granted.
        
        Uses logical evaluation combining axioms and permissions.
        
        Args:
            entity_id: Entity requesting access
            roles: Entity's roles
            action: Action to perform
            resource: Resource to access
            context: Optional context for evaluation
            
        Returns:
            Tuple of (granted, reason)
        """
        if context is None:
            context = {}
            
        # Add entity_id to context
        context["entity_id"] = entity_id
        
        # Create cache key
        cache_key = f"{entity_id}:{':'.join(sorted(roles))}:{action.value}:{resource}"
        
        # Check cache
        if cache_key in self._evaluation_cache:
            granted = self._evaluation_cache[cache_key]
            reason = "Cached result" if granted else "Cached denial"
            return granted, reason
            
        # Evaluate permission
        granted = self._policy.check_permission(roles, action, resource, context)
        
        # Apply axiom of consistency
        permission_state = LogicalState(content={
            'entity': entity_id,
            'action': action.value,
            'resource': resource,
            'granted': granted
        })
        
        denial_state = LogicalState(content={
            'entity': entity_id,
            'action': action.value,
            'resource': resource,
            'granted': not granted
        })
        
        # Verify consistency
        if not self._axioms.verify_consistency(permission_state, denial_state):
            # Inconsistent state - deny by default
            granted = False
            reason = "Logical inconsistency detected"
        else:
            reason = "Permission granted by policy" if granted else "Permission denied by policy"
            
        # Cache result
        self._evaluation_cache[cache_key] = granted
        
        return granted, reason
        
    def clear_cache(self) -> None:
        """Clear the evaluation cache."""
        self._evaluation_cache.clear()