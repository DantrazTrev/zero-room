"""
Policy Engine for ADP-RBAC
===========================

Implements policy decision making using logical inference
and the fundamental principles of the ADP protocol.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time
import json

from ..core.realms import LogicalState, SharedRealm
from ..core.state import LogicalBoundary
from ..foundation.axioms import SharedWitness
from .roles import RoleManager
from .permissions import PermissionType, ResourceType, AccessPolicy, PermissionEvaluator


class PolicyDecision(Enum):
    """Policy decision outcomes."""
    PERMIT = "permit"
    DENY = "deny"
    INDETERMINATE = "indeterminate"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class PolicyRequest:
    """Represents a policy evaluation request."""
    entity_id: str
    action: PermissionType
    resource: str
    resource_type: ResourceType
    context: Dict[str, Any]
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
            
    def to_logical_state(self) -> LogicalState:
        """Convert request to logical state."""
        return LogicalState(content={
            'type': 'policy_request',
            'entity_id': self.entity_id,
            'action': self.action.value,
            'resource': self.resource,
            'resource_type': self.resource_type.value,
            'context': self.context,
            'timestamp': self.timestamp
        })


@dataclass
class PolicyResponse:
    """Represents a policy evaluation response."""
    request: PolicyRequest
    decision: PolicyDecision
    reason: str
    obligations: List[str]
    advice: List[str]
    evaluation_time: float
    
    def to_logical_state(self) -> LogicalState:
        """Convert response to logical state."""
        return LogicalState(content={
            'type': 'policy_response',
            'request': self.request.to_logical_state().content,
            'decision': self.decision.value,
            'reason': self.reason,
            'obligations': self.obligations,
            'advice': self.advice,
            'evaluation_time': self.evaluation_time
        })


class PolicyEngine:
    """
    Policy decision engine using logical inference.
    
    Combines roles, permissions, and logical principles to make
    authorization decisions.
    """
    
    def __init__(self, shared_realm: SharedRealm, boundary: LogicalBoundary,
                 role_manager: RoleManager, access_policy: AccessPolicy,
                 witness_system: SharedWitness):
        """
        Initialize policy engine.
        
        Args:
            shared_realm: Reference to shared realm
            boundary: Logical boundary system
            role_manager: Role management system
            access_policy: Access control policy
            witness_system: Witness system for consensus
        """
        self._shared_realm = shared_realm
        self._boundary = boundary
        self._role_manager = role_manager
        self._access_policy = access_policy
        self._witness_system = witness_system
        
        # Initialize evaluator
        from ..foundation.axioms import SharedAxiom
        axioms = SharedAxiom()
        self._evaluator = PermissionEvaluator(axioms, access_policy)
        
        # Policy evaluation history
        self._evaluation_history: List[PolicyResponse] = []
        
        # Conflict resolution strategies
        self._conflict_resolution = self._default_conflict_resolution
        
    def evaluate(self, request: PolicyRequest) -> PolicyResponse:
        """
        Evaluate a policy request.
        
        Uses logical inference to determine the appropriate decision.
        
        Args:
            request: Policy request to evaluate
            
        Returns:
            Policy response with decision
        """
        start_time = time.time()
        
        # Get entity's roles
        roles = self._role_manager.get_entity_roles(request.entity_id)
        
        if not roles:
            # No roles assigned - check default policy
            response = PolicyResponse(
                request=request,
                decision=PolicyDecision.DENY,
                reason="No roles assigned to entity",
                obligations=[],
                advice=["Request role assignment"],
                evaluation_time=time.time() - start_time
            )
            self._record_evaluation(response)
            return response
            
        # Evaluate permission
        granted, reason = self._evaluator.evaluate_access(
            request.entity_id,
            roles,
            request.action,
            request.resource,
            request.context
        )
        
        # Determine decision
        if granted:
            decision = PolicyDecision.PERMIT
            obligations = self._get_obligations(request, roles)
            advice = self._get_advice(request, roles)
        else:
            decision = PolicyDecision.DENY
            obligations = []
            advice = self._get_denial_advice(request, roles)
            
        response = PolicyResponse(
            request=request,
            decision=decision,
            reason=reason,
            obligations=obligations,
            advice=advice,
            evaluation_time=time.time() - start_time
        )
        
        # Record evaluation
        self._record_evaluation(response)
        
        # Register in shared realm for witnessing
        self._shared_realm.add_witness(response.to_logical_state())
        
        return response
        
    def evaluate_with_proof(self, request: PolicyRequest, 
                          proof: LogicalState) -> PolicyResponse:
        """
        Evaluate a request with an existing permission proof.
        
        This allows verification without accessing the entity's
        separate realm.
        
        Args:
            request: Policy request
            proof: Permission proof from entity
            
        Returns:
            Policy response
        """
        start_time = time.time()
        
        # Verify proof validity
        if not self._verify_proof(proof, request):
            response = PolicyResponse(
                request=request,
                decision=PolicyDecision.DENY,
                reason="Invalid or expired proof",
                obligations=[],
                advice=["Generate new permission proof"],
                evaluation_time=time.time() - start_time
            )
            self._record_evaluation(response)
            return response
            
        # Extract decision from proof
        granted = proof.content.get('granted', False)
        
        if granted:
            decision = PolicyDecision.PERMIT
            reason = "Valid permission proof provided"
            obligations = ["Log access with proof"]
            advice = []
        else:
            decision = PolicyDecision.DENY
            reason = "Proof indicates permission denied"
            obligations = []
            advice = ["Request higher privileges"]
            
        response = PolicyResponse(
            request=request,
            decision=decision,
            reason=reason,
            obligations=obligations,
            advice=advice,
            evaluation_time=time.time() - start_time
        )
        
        self._record_evaluation(response)
        return response
        
    def _verify_proof(self, proof: LogicalState, request: PolicyRequest) -> bool:
        """Verify a permission proof is valid for a request."""
        if proof.content.get('type') != 'permission_proof':
            return False
            
        # Check entity matches
        if proof.content.get('entity_id') != request.entity_id:
            return False
            
        # Check action and resource match
        if proof.content.get('action') != request.action.value:
            return False
        if proof.content.get('resource') != request.resource:
            return False
            
        # Check proof age (5 minute validity)
        proof_time = proof.content.get('timestamp', 0)
        if time.time() - proof_time > 300:
            return False
            
        return True
        
    def _get_obligations(self, request: PolicyRequest, 
                        roles: List[str]) -> List[str]:
        """Get obligations for a permitted request."""
        obligations = []
        
        # Audit obligation for sensitive resources
        if request.resource_type in [ResourceType.USER, ResourceType.ROLE, 
                                    ResourceType.PERMISSION]:
            obligations.append("Audit log required")
            
        # Notification obligation for admin actions
        if request.action in [PermissionType.DELETE, PermissionType.ADMIN]:
            obligations.append("Notify administrators")
            
        # Witness obligation for critical actions
        if request.action == PermissionType.DELETE and \
           request.resource_type == ResourceType.SYSTEM:
            obligations.append("Require witness confirmation")
            
        return obligations
        
    def _get_advice(self, request: PolicyRequest, roles: List[str]) -> List[str]:
        """Get advice for a permitted request."""
        advice = []
        
        # Suggest best practices
        if request.action == PermissionType.UPDATE:
            advice.append("Create backup before modification")
            
        if request.resource_type == ResourceType.CONFIG:
            advice.append("Test configuration changes in staging")
            
        return advice
        
    def _get_denial_advice(self, request: PolicyRequest, 
                          roles: List[str]) -> List[str]:
        """Get advice for a denied request."""
        advice = []
        
        # Suggest how to get access
        required_roles = self._find_required_roles(request.action, 
                                                  request.resource_type)
        if required_roles:
            advice.append(f"Request one of these roles: {', '.join(required_roles)}")
            
        # Suggest alternative actions
        if request.action == PermissionType.DELETE:
            advice.append("Consider archiving instead of deleting")
            
        if request.action == PermissionType.ADMIN:
            advice.append("Contact system administrator")
            
        return advice
        
    def _find_required_roles(self, action: PermissionType, 
                            resource_type: ResourceType) -> List[str]:
        """Find roles that would grant the requested permission."""
        required_roles = []
        
        # Check each role's permissions
        for role_name in ["super_admin", "admin", "auditor", "editor", "user", "viewer"]:
            perm_set = self._access_policy.get_role_permissions(role_name)
            if perm_set:
                # Create a test resource
                test_resource = f"{resource_type.value}:test"
                if perm_set.evaluate(action, test_resource, {}):
                    required_roles.append(role_name)
                    
        return required_roles
        
    def _record_evaluation(self, response: PolicyResponse) -> None:
        """Record evaluation for audit and learning."""
        self._evaluation_history.append(response)
        
        # Limit history size
        if len(self._evaluation_history) > 1000:
            self._evaluation_history = self._evaluation_history[-1000:]
            
    def _default_conflict_resolution(self, decisions: List[PolicyDecision]) -> PolicyDecision:
        """
        Default conflict resolution strategy.
        
        Uses logical principles to resolve conflicting decisions.
        """
        # Deny overrides
        if PolicyDecision.DENY in decisions:
            return PolicyDecision.DENY
            
        # Permit if any permit
        if PolicyDecision.PERMIT in decisions:
            return PolicyDecision.PERMIT
            
        # Otherwise indeterminate
        return PolicyDecision.INDETERMINATE
        
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """Get statistics about policy evaluations."""
        if not self._evaluation_history:
            return {
                'total_evaluations': 0,
                'permit_rate': 0.0,
                'deny_rate': 0.0,
                'average_evaluation_time': 0.0
            }
            
        total = len(self._evaluation_history)
        permits = sum(1 for r in self._evaluation_history 
                     if r.decision == PolicyDecision.PERMIT)
        denies = sum(1 for r in self._evaluation_history 
                    if r.decision == PolicyDecision.DENY)
        avg_time = sum(r.evaluation_time for r in self._evaluation_history) / total
        
        return {
            'total_evaluations': total,
            'permit_rate': permits / total,
            'deny_rate': denies / total,
            'average_evaluation_time': avg_time,
            'recent_evaluations': [
                {
                    'entity': r.request.entity_id,
                    'action': r.request.action.value,
                    'resource': r.request.resource,
                    'decision': r.decision.value,
                    'time': r.evaluation_time
                }
                for r in self._evaluation_history[-5:]
            ]
        }
        
    def create_policy_proof(self, entity_id: str, action: PermissionType,
                           resource: str) -> LogicalState:
        """
        Create a proof of policy evaluation.
        
        This proof can be used for distributed authorization
        without re-evaluating the policy.
        
        Args:
            entity_id: Entity requesting access
            action: Action to perform
            resource: Resource to access
            
        Returns:
            Policy proof
        """
        # Create request
        request = PolicyRequest(
            entity_id=entity_id,
            action=action,
            resource=resource,
            resource_type=ResourceType.DATA,  # Default
            context={}
        )
        
        # Evaluate policy
        response = self.evaluate(request)
        
        # Create proof
        proof_content = {
            'type': 'policy_proof',
            'entity_id': entity_id,
            'action': action.value,
            'resource': resource,
            'decision': response.decision.value,
            'reason': response.reason,
            'timestamp': time.time(),
            'valid_until': time.time() + 300  # 5 minute validity
        }
        
        # Add witness if decision was permit
        if response.decision == PolicyDecision.PERMIT:
            self._witness_system.witness(
                LogicalState(content=proof_content),
                entity_id
            )
            
        return LogicalState(content=proof_content)