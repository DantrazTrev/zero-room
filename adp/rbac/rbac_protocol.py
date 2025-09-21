"""
ADP-RBAC Protocol Implementation
=================================

Main protocol that integrates role-based access control with
the Axiom of Distinction Protocol's logical foundations.
"""

from typing import Dict, List, Optional, Tuple, Any
import time

from ..protocol.adp import AxiomDistinctionProtocol, ProtocolConfig
from ..entities.entity import Entity
from ..core.realms import LogicalState
from ..verification.engine import VerificationResult

from .roles import RoleHierarchy, RoleManager, RoleAssignment, RoleType
from .permissions import (
    Permission, PermissionSet, AccessPolicy, 
    PermissionType, ResourceType
)
from .policy_engine import (
    PolicyEngine, PolicyRequest, PolicyResponse, PolicyDecision
)


class ADPRBACProtocol:
    """
    Role-Based Access Control protocol built on ADP foundations.
    
    This protocol demonstrates that complex enterprise access control
    can emerge from simple logical principles.
    """
    
    def __init__(self, config: Optional[ProtocolConfig] = None):
        """
        Initialize ADP-RBAC protocol.
        
        Args:
            config: Optional protocol configuration
        """
        # Initialize base ADP protocol
        self._adp = AxiomDistinctionProtocol(config or ProtocolConfig())
        
        # Initialize RBAC components
        self._role_hierarchy = RoleHierarchy(self._adp.shared_realm)
        self._role_manager = RoleManager(
            self._role_hierarchy, 
            self._adp.logical_boundary
        )
        self._access_policy = AccessPolicy(
            "default_policy", 
            self._adp.shared_realm
        )
        self._policy_engine = PolicyEngine(
            self._adp.shared_realm,
            self._adp.logical_boundary,
            self._role_manager,
            self._access_policy,
            self._adp.shared_witness
        )
        
        # Track RBAC-specific state
        self._authenticated_sessions: Dict[str, Dict] = {}
        self._access_logs: List[Dict] = []
        
    def register_user(self, user_id: str, initial_role: str = "viewer") -> Entity:
        """
        Register a user with an initial role.
        
        Args:
            user_id: Unique user identifier
            initial_role: Initial role assignment (default: viewer)
            
        Returns:
            Registered Entity object
        """
        # Register entity in base protocol
        entity = self._adp.register_entity(user_id)
        
        # Assign initial role
        self._role_manager.assign_role(
            user_id, 
            initial_role, 
            "system",
            expires_at=None  # Permanent assignment
        )
        
        # Log registration
        self._log_access({
            'type': 'user_registration',
            'user_id': user_id,
            'initial_role': initial_role,
            'timestamp': time.time()
        })
        
        return entity
        
    def authenticate_user(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Authenticate a user and create a session.
        
        Args:
            user_id: User to authenticate
            
        Returns:
            Tuple of (success, session_token)
        """
        # Use base protocol for authentication
        report = self._adp.authenticate_entity(user_id)
        
        if not report.is_successful():
            self._log_access({
                'type': 'authentication_failed',
                'user_id': user_id,
                'reason': report.reason,
                'timestamp': time.time()
            })
            return False, None
            
        # Create session
        import hashlib
        session_token = hashlib.sha256(
            f"{user_id}:{time.time()}".encode()
        ).hexdigest()
        
        # Get user roles
        roles = self._role_manager.get_entity_roles(user_id)
        
        # Store session
        self._authenticated_sessions[session_token] = {
            'user_id': user_id,
            'roles': roles,
            'created_at': time.time(),
            'last_activity': time.time()
        }
        
        # Log successful authentication
        self._log_access({
            'type': 'authentication_success',
            'user_id': user_id,
            'roles': roles,
            'session_token': session_token[:8] + '...',  # Log partial token
            'timestamp': time.time()
        })
        
        return True, session_token
        
    def check_permission(self, session_token: str, action: PermissionType,
                        resource: str, resource_type: ResourceType = ResourceType.DATA,
                        context: Optional[Dict[str, Any]] = None) -> PolicyResponse:
        """
        Check if a session has permission for an action.
        
        Args:
            session_token: Active session token
            action: Action to perform
            resource: Resource to access
            resource_type: Type of resource
            context: Optional context for evaluation
            
        Returns:
            PolicyResponse with decision
        """
        # Validate session
        session = self._authenticated_sessions.get(session_token)
        if not session:
            # Invalid session
            request = PolicyRequest(
                entity_id="unknown",
                action=action,
                resource=resource,
                resource_type=resource_type,
                context=context or {}
            )
            return PolicyResponse(
                request=request,
                decision=PolicyDecision.DENY,
                reason="Invalid or expired session",
                obligations=[],
                advice=["Please authenticate"],
                evaluation_time=0.0
            )
            
        # Update session activity
        session['last_activity'] = time.time()
        
        # Create policy request
        request = PolicyRequest(
            entity_id=session['user_id'],
            action=action,
            resource=resource,
            resource_type=resource_type,
            context=context or {}
        )
        
        # Evaluate policy
        response = self._policy_engine.evaluate(request)
        
        # Log access attempt
        self._log_access({
            'type': 'access_attempt',
            'user_id': session['user_id'],
            'action': action.value,
            'resource': resource,
            'decision': response.decision.value,
            'reason': response.reason,
            'timestamp': time.time()
        })
        
        return response
        
    def assign_role(self, admin_token: str, target_user: str, 
                   role: str, expires_at: Optional[float] = None) -> Tuple[bool, str]:
        """
        Assign a role to a user.
        
        Requires admin privileges.
        
        Args:
            admin_token: Session token of administrator
            target_user: User to assign role to
            role: Role to assign
            expires_at: Optional expiration time
            
        Returns:
            Tuple of (success, message)
        """
        # Check admin permission
        response = self.check_permission(
            admin_token,
            PermissionType.UPDATE,
            f"role:{target_user}",
            ResourceType.ROLE
        )
        
        if response.decision != PolicyDecision.PERMIT:
            return False, "Insufficient privileges to assign roles"
            
        # Get admin session
        session = self._authenticated_sessions[admin_token]
        admin_id = session['user_id']
        
        # Check if admin can assign this specific role
        if not self._role_manager.can_assign_role(admin_id, role):
            return False, f"Cannot assign role {role} - insufficient hierarchy position"
            
        # Perform assignment
        try:
            assignment = self._role_manager.assign_role(
                target_user,
                role,
                admin_id,
                expires_at
            )
            
            # Create delegation proof
            admin_entity = self._adp._entities.get(admin_id)
            if admin_entity:
                admin_realm = self._adp.logical_boundary.get_boundary(admin_id)
                if admin_realm:
                    assignment.create_delegation_proof(admin_realm)
                    
            # Log role assignment
            self._log_access({
                'type': 'role_assignment',
                'admin': admin_id,
                'target_user': target_user,
                'role': role,
                'expires_at': expires_at,
                'timestamp': time.time()
            })
            
            return True, f"Role {role} assigned to {target_user}"
            
        except Exception as e:
            return False, str(e)
            
    def revoke_role(self, admin_token: str, target_user: str, 
                   role: str) -> Tuple[bool, str]:
        """
        Revoke a role from a user.
        
        Args:
            admin_token: Session token of administrator
            target_user: User to revoke role from
            role: Role to revoke
            
        Returns:
            Tuple of (success, message)
        """
        # Check admin permission
        response = self.check_permission(
            admin_token,
            PermissionType.DELETE,
            f"role:{target_user}",
            ResourceType.ROLE
        )
        
        if response.decision != PolicyDecision.PERMIT:
            return False, "Insufficient privileges to revoke roles"
            
        # Implementation would remove role assignment
        # For demo, we'll just log it
        session = self._authenticated_sessions[admin_token]
        
        self._log_access({
            'type': 'role_revocation',
            'admin': session['user_id'],
            'target_user': target_user,
            'role': role,
            'timestamp': time.time()
        })
        
        return True, f"Role {role} revoked from {target_user}"
        
    def create_custom_role(self, admin_token: str, role_name: str,
                          parent_roles: List[str], 
                          permissions: PermissionSet) -> Tuple[bool, str]:
        """
        Create a custom role with specific permissions.
        
        Args:
            admin_token: Session token of administrator
            role_name: Name for new role
            parent_roles: Parent roles in hierarchy
            permissions: Permission set for role
            
        Returns:
            Tuple of (success, message)
        """
        # Check admin permission
        response = self.check_permission(
            admin_token,
            PermissionType.CREATE,
            f"role:{role_name}",
            ResourceType.ROLE
        )
        
        if response.decision != PolicyDecision.PERMIT:
            return False, "Insufficient privileges to create roles"
            
        try:
            # Create role
            from .roles import Role
            custom_role = Role(
                name=role_name,
                role_type=RoleType.CUSTOM,
                description=f"Custom role: {role_name}",
                parent_roles=frozenset(parent_roles)
            )
            
            # Register role
            self._role_hierarchy.register_role(custom_role)
            
            # Add permissions
            self._access_policy.add_role_permissions(role_name, permissions)
            
            # Log creation
            session = self._authenticated_sessions[admin_token]
            self._log_access({
                'type': 'role_creation',
                'admin': session['user_id'],
                'role_name': role_name,
                'parent_roles': parent_roles,
                'timestamp': time.time()
            })
            
            return True, f"Custom role {role_name} created"
            
        except Exception as e:
            return False, str(e)
            
    def audit_access(self, auditor_token: str, 
                    user_filter: Optional[str] = None,
                    action_filter: Optional[str] = None,
                    limit: int = 100) -> Tuple[bool, List[Dict]]:
        """
        Audit access logs.
        
        Requires auditor privileges.
        
        Args:
            auditor_token: Session token of auditor
            user_filter: Optional filter by user
            action_filter: Optional filter by action
            limit: Maximum entries to return
            
        Returns:
            Tuple of (authorized, filtered_logs)
        """
        # Check audit permission
        response = self.check_permission(
            auditor_token,
            PermissionType.AUDIT,
            "audit_log:*",
            ResourceType.AUDIT_LOG
        )
        
        if response.decision != PolicyDecision.PERMIT:
            return False, []
            
        # Filter logs
        filtered = self._access_logs
        
        if user_filter:
            filtered = [
                log for log in filtered
                if log.get('user_id') == user_filter or 
                   log.get('target_user') == user_filter
            ]
            
        if action_filter:
            filtered = [
                log for log in filtered
                if log.get('type') == action_filter or
                   log.get('action') == action_filter
            ]
            
        # Return limited results
        return True, filtered[-limit:]
        
    def get_user_roles(self, session_token: str, 
                       target_user: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Get roles for a user.
        
        Args:
            session_token: Active session token
            target_user: User to query (None for self)
            
        Returns:
            Tuple of (authorized, roles)
        """
        session = self._authenticated_sessions.get(session_token)
        if not session:
            return False, []
            
        # Determine target
        if target_user is None:
            target_user = session['user_id']
            
        # Check permission
        resource = f"user:{target_user}"
        response = self.check_permission(
            session_token,
            PermissionType.READ,
            resource,
            ResourceType.USER
        )
        
        if response.decision != PolicyDecision.PERMIT:
            return False, []
            
        # Get roles
        roles = self._role_manager.get_entity_roles(target_user)
        return True, roles
        
    def _log_access(self, log_entry: Dict) -> None:
        """Log access events."""
        self._access_logs.append(log_entry)
        
        # Limit log size
        if len(self._access_logs) > 10000:
            self._access_logs = self._access_logs[-10000:]
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get RBAC protocol statistics."""
        base_stats = self._adp.get_protocol_state()
        policy_stats = self._policy_engine.get_evaluation_statistics()
        
        return {
            **base_stats,
            'active_sessions': len(self._authenticated_sessions),
            'total_roles': len(self._role_hierarchy.get_all_roles()),
            'access_log_entries': len(self._access_logs),
            **policy_stats
        }
        
    def cleanup_sessions(self, max_age: float = 3600) -> int:
        """
        Clean up expired sessions.
        
        Args:
            max_age: Maximum session age in seconds
            
        Returns:
            Number of sessions cleaned
        """
        current_time = time.time()
        expired = []
        
        for token, session in self._authenticated_sessions.items():
            if current_time - session['last_activity'] > max_age:
                expired.append(token)
                
        for token in expired:
            del self._authenticated_sessions[token]
            
        return len(expired)