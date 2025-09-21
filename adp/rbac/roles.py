"""
Role Management System for ADP-RBAC
====================================

Implements roles as logical constructs that exist in either
SHARED (role definitions) or SEPARATE (role assignments) realms.
"""

from typing import Set, Dict, List, Optional, FrozenSet
from dataclasses import dataclass, field
from enum import Enum
import time

from ..core.realms import LogicalState, SharedRealm, SeparateRealm
from ..core.state import LogicalBoundary


class RoleType(Enum):
    """Types of roles in the system."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    AUDITOR = "auditor"
    EDITOR = "editor"
    USER = "user"
    VIEWER = "viewer"
    CUSTOM = "custom"


@dataclass(frozen=True)
class Role:
    """
    Represents a role in the RBAC system.
    
    Roles are SHARED constructs - their definitions are universal.
    Role assignments to entities are SEPARATE.
    """
    name: str
    role_type: RoleType
    description: str
    parent_roles: FrozenSet[str] = frozenset()
    child_roles: FrozenSet[str] = frozenset()
    created_at: float = field(default_factory=time.time)
    
    def __hash__(self):
        return hash((self.name, self.role_type))
    
    def to_logical_state(self) -> LogicalState:
        """Convert role to a logical state for the shared realm."""
        return LogicalState(content={
            'type': 'role_definition',
            'name': self.name,
            'role_type': self.role_type.value,
            'description': self.description,
            'parent_roles': list(self.parent_roles),
            'child_roles': list(self.child_roles),
            'created_at': self.created_at
        })
    
    def inherits_from(self, other_role: str) -> bool:
        """Check if this role inherits from another role."""
        return other_role in self.parent_roles
    
    def is_parent_of(self, other_role: str) -> bool:
        """Check if this role is a parent of another role."""
        return other_role in self.child_roles


class RoleHierarchy:
    """
    Manages the role hierarchy using logical principles.
    
    The hierarchy itself is SHARED knowledge, but the assignment
    of entities to positions in the hierarchy is SEPARATE.
    """
    
    def __init__(self, shared_realm: SharedRealm):
        """
        Initialize role hierarchy.
        
        Args:
            shared_realm: Reference to the shared realm
        """
        self._shared_realm = shared_realm
        self._roles: Dict[str, Role] = {}
        self._hierarchy_graph: Dict[str, Set[str]] = {}
        
        # Initialize default roles
        self._initialize_default_roles()
        
    def _initialize_default_roles(self):
        """Initialize the default role hierarchy."""
        # Create default roles
        super_admin = Role(
            name="super_admin",
            role_type=RoleType.SUPER_ADMIN,
            description="Full system access",
            child_roles=frozenset(["admin", "auditor"])
        )
        
        admin = Role(
            name="admin",
            role_type=RoleType.ADMIN,
            description="Administrative access",
            parent_roles=frozenset(["super_admin"]),
            child_roles=frozenset(["editor", "user"])
        )
        
        auditor = Role(
            name="auditor",
            role_type=RoleType.AUDITOR,
            description="Audit and compliance access",
            parent_roles=frozenset(["super_admin"]),
            child_roles=frozenset(["viewer"])
        )
        
        editor = Role(
            name="editor",
            role_type=RoleType.EDITOR,
            description="Content editing access",
            parent_roles=frozenset(["admin"]),
            child_roles=frozenset(["viewer"])
        )
        
        user = Role(
            name="user",
            role_type=RoleType.USER,
            description="Standard user access",
            parent_roles=frozenset(["admin"]),
            child_roles=frozenset(["viewer"])
        )
        
        viewer = Role(
            name="viewer",
            role_type=RoleType.VIEWER,
            description="Read-only access",
            parent_roles=frozenset(["editor", "user", "auditor"])
        )
        
        # Register roles
        for role in [super_admin, admin, auditor, editor, user, viewer]:
            self.register_role(role)
            
    def register_role(self, role: Role) -> None:
        """
        Register a role in the hierarchy.
        
        This adds the role definition to the SHARED realm.
        
        Args:
            role: Role to register
        """
        if role.name in self._roles:
            raise ValueError(f"Role {role.name} already exists")
            
        self._roles[role.name] = role
        
        # Add to hierarchy graph
        self._hierarchy_graph[role.name] = set(role.child_roles)
        
        # Register in shared realm
        role_state = role.to_logical_state()
        self._shared_realm.add_method(role_state)
        
    def get_role(self, role_name: str) -> Optional[Role]:
        """Get a role by name."""
        return self._roles.get(role_name)
        
    def get_all_roles(self) -> List[Role]:
        """Get all registered roles."""
        return list(self._roles.values())
        
    def is_superior_role(self, role1: str, role2: str) -> bool:
        """
        Check if role1 is superior to role2 in the hierarchy.
        
        Uses logical transitivity to determine superiority.
        
        Args:
            role1: Potentially superior role
            role2: Potentially inferior role
            
        Returns:
            True if role1 is superior to role2
        """
        if role1 not in self._roles or role2 not in self._roles:
            return False
            
        # Check direct relationship
        if role2 in self._hierarchy_graph.get(role1, set()):
            return True
            
        # Check transitive relationship
        visited = set()
        to_check = [role1]
        
        while to_check:
            current = to_check.pop()
            if current in visited:
                continue
                
            visited.add(current)
            
            children = self._hierarchy_graph.get(current, set())
            if role2 in children:
                return True
                
            to_check.extend(children)
            
        return False
        
    def get_inherited_roles(self, role_name: str) -> Set[str]:
        """
        Get all roles inherited by a given role.
        
        Uses logical transitivity to find all inferior roles.
        
        Args:
            role_name: Role to check
            
        Returns:
            Set of inherited role names
        """
        if role_name not in self._roles:
            return set()
            
        inherited = set()
        to_check = [role_name]
        
        while to_check:
            current = to_check.pop()
            children = self._hierarchy_graph.get(current, set())
            
            for child in children:
                if child not in inherited:
                    inherited.add(child)
                    to_check.append(child)
                    
        return inherited
        
    def verify_hierarchy_consistency(self) -> bool:
        """
        Verify the role hierarchy is logically consistent.
        
        Checks for:
        - Circular dependencies
        - Orphaned roles
        - Conflicting relationships
        
        Returns:
            True if hierarchy is consistent
        """
        # Check for circular dependencies
        for role_name in self._roles:
            if self._has_circular_dependency(role_name):
                return False
                
        # Check parent-child consistency
        for role_name, role in self._roles.items():
            for parent in role.parent_roles:
                if parent in self._roles:
                    parent_role = self._roles[parent]
                    if role_name not in parent_role.child_roles:
                        return False
                        
            for child in role.child_roles:
                if child in self._roles:
                    child_role = self._roles[child]
                    if role_name not in child_role.parent_roles:
                        return False
                        
        return True
        
    def _has_circular_dependency(self, start_role: str) -> bool:
        """Check if a role has circular dependencies."""
        visited = set()
        path = []
        
        def dfs(role: str) -> bool:
            if role in path:
                return True  # Circular dependency found
                
            if role in visited:
                return False
                
            visited.add(role)
            path.append(role)
            
            for child in self._hierarchy_graph.get(role, set()):
                if dfs(child):
                    return True
                    
            path.pop()
            return False
            
        return dfs(start_role)


@dataclass
class RoleAssignment:
    """
    Represents the assignment of a role to an entity.
    
    Role assignments are SEPARATE - they exist exclusively
    in an entity's separate realm.
    """
    entity_id: str
    role_name: str
    assigned_by: str
    assigned_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    delegation_proof: Optional[LogicalState] = None
    
    def is_valid(self) -> bool:
        """Check if the assignment is currently valid."""
        if self.expires_at is None:
            return True
        return time.time() < self.expires_at
        
    def to_logical_state(self) -> LogicalState:
        """Convert assignment to logical state."""
        return LogicalState(content={
            'type': 'role_assignment',
            'entity_id': self.entity_id,
            'role_name': self.role_name,
            'assigned_by': self.assigned_by,
            'assigned_at': self.assigned_at,
            'expires_at': self.expires_at,
            'valid': self.is_valid()
        })
        
    def create_delegation_proof(self, delegator_realm: SeparateRealm) -> LogicalState:
        """
        Create a proof that this assignment was properly delegated.
        
        The proof demonstrates that the delegator had the authority
        to assign this role, without revealing their exclusive knowledge.
        
        Args:
            delegator_realm: The separate realm of the delegator
            
        Returns:
            Delegation proof
        """
        # Create challenge for delegation
        challenge = f"delegate:{self.entity_id}:{self.role_name}:{self.assigned_at}"
        
        # Generate proof using delegator's exclusive knowledge
        proof = delegator_realm.create_boundary_proof(challenge)
        
        self.delegation_proof = proof
        return proof


class RoleManager:
    """
    Manages role assignments using logical separation.
    
    Role definitions are SHARED, but assignments are SEPARATE.
    """
    
    def __init__(self, hierarchy: RoleHierarchy, boundary: LogicalBoundary):
        """
        Initialize role manager.
        
        Args:
            hierarchy: Role hierarchy
            boundary: Logical boundary system
        """
        self._hierarchy = hierarchy
        self._boundary = boundary
        self._assignments: Dict[str, List[RoleAssignment]] = {}
        
    def assign_role(self, entity_id: str, role_name: str, 
                   assigned_by: str, expires_at: Optional[float] = None) -> RoleAssignment:
        """
        Assign a role to an entity.
        
        This creates a SEPARATE assignment that exists only
        in the entity's realm.
        
        Args:
            entity_id: Entity to assign role to
            role_name: Name of role to assign
            assigned_by: Entity making the assignment
            expires_at: Optional expiration time
            
        Returns:
            RoleAssignment object
        """
        # Verify role exists
        role = self._hierarchy.get_role(role_name)
        if not role:
            raise ValueError(f"Role {role_name} does not exist")
            
        # Create assignment
        assignment = RoleAssignment(
            entity_id=entity_id,
            role_name=role_name,
            assigned_by=assigned_by,
            expires_at=expires_at
        )
        
        # Store in entity's separate realm
        entity_realm = self._boundary.get_boundary(entity_id)
        if entity_realm:
            assignment_state = assignment.to_logical_state()
            entity_realm.add_exclusive_knowledge(assignment_state)
            
        # Track assignment
        if entity_id not in self._assignments:
            self._assignments[entity_id] = []
        self._assignments[entity_id].append(assignment)
        
        return assignment
        
    def get_entity_roles(self, entity_id: str) -> List[str]:
        """
        Get all roles assigned to an entity.
        
        Includes inherited roles through hierarchy.
        
        Args:
            entity_id: Entity to check
            
        Returns:
            List of role names
        """
        if entity_id not in self._assignments:
            return []
            
        roles = set()
        for assignment in self._assignments[entity_id]:
            if assignment.is_valid():
                roles.add(assignment.role_name)
                # Add inherited roles
                inherited = self._hierarchy.get_inherited_roles(assignment.role_name)
                roles.update(inherited)
                
        return list(roles)
        
    def has_role(self, entity_id: str, role_name: str) -> bool:
        """
        Check if an entity has a specific role.
        
        Considers role inheritance.
        
        Args:
            entity_id: Entity to check
            role_name: Role to check for
            
        Returns:
            True if entity has the role
        """
        entity_roles = self.get_entity_roles(entity_id)
        return role_name in entity_roles
        
    def can_assign_role(self, assigner_id: str, role_to_assign: str) -> bool:
        """
        Check if an entity can assign a specific role.
        
        Uses logical hierarchy to determine delegation authority.
        
        Args:
            assigner_id: Entity attempting to assign
            role_to_assign: Role to be assigned
            
        Returns:
            True if assignment is allowed
        """
        assigner_roles = self.get_entity_roles(assigner_id)
        
        # Check if assigner has a superior role
        for assigner_role in assigner_roles:
            if self._hierarchy.is_superior_role(assigner_role, role_to_assign):
                return True
                
        return False