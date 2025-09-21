"""
State Management and Transition System
=======================================

Enforces logical rules about state transitions and maintains
boundaries between SHARED and SEPARATE realms.
"""

from typing import Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from .realms import SharedRealm, SeparateRealm, LogicalState


class StateType(Enum):
    """Fundamental state types in the protocol."""
    SHARED = "SHARED"
    SEPARATE = "SEPARATE"
    TRANSITIONING = "TRANSITIONING"  # Temporary state during validation


@dataclass(frozen=True)
class TransitionRule:
    """Defines valid state transitions."""
    from_state: StateType
    to_state: StateType
    allowed: bool
    reason: str


class StateTransition:
    """
    Enforces the fundamental rule: SHARED cannot become SEPARATE.
    
    This class ensures logical consistency by preventing information
    that exists in the shared realm from being claimed as exclusive.
    """
    
    # Define transition rules based on logical necessity
    TRANSITION_RULES = [
        TransitionRule(StateType.SHARED, StateType.SHARED, True, 
                      "Shared remains shared"),
        TransitionRule(StateType.SHARED, StateType.SEPARATE, False, 
                      "Shared cannot become separate - fundamental axiom"),
        TransitionRule(StateType.SEPARATE, StateType.SEPARATE, True, 
                      "Separate remains separate"),
        TransitionRule(StateType.SEPARATE, StateType.SHARED, True, 
                      "Separate can be revealed to become shared"),
    ]
    
    def __init__(self):
        """Initialize the state transition system."""
        self._transition_log = []
        
    def validate_transition(self, from_state: StateType, to_state: StateType) -> Tuple[bool, str]:
        """
        Validate if a state transition is logically valid.
        
        Returns:
            Tuple of (is_valid, reason)
        """
        for rule in self.TRANSITION_RULES:
            if rule.from_state == from_state and rule.to_state == to_state:
                self._log_transition(from_state, to_state, rule.allowed, rule.reason)
                return rule.allowed, rule.reason
                
        # Unknown transition - default to disallow
        reason = "Unknown transition - not defined in logical framework"
        self._log_transition(from_state, to_state, False, reason)
        return False, reason
        
    def _log_transition(self, from_state: StateType, to_state: StateType, 
                       allowed: bool, reason: str) -> None:
        """Log transition attempts for verification."""
        self._transition_log.append({
            'from': from_state,
            'to': to_state,
            'allowed': allowed,
            'reason': reason,
            'timestamp': LogicalState(content="").timestamp
        })
        
    def attempt_transition(self, state: LogicalState, from_type: StateType, 
                          to_type: StateType) -> Optional[LogicalState]:
        """
        Attempt to transition a logical state.
        
        Returns:
            New state if transition is valid, None otherwise
        """
        is_valid, reason = self.validate_transition(from_type, to_type)
        
        if not is_valid:
            return None
            
        # Create new state with transition metadata
        new_content = {
            'original': state.content,
            'transition': f"{from_type.value} -> {to_type.value}",
            'reason': reason
        }
        
        return LogicalState(content=new_content)
        
    def get_transition_log(self) -> list:
        """Return the transition log for auditing."""
        return self._transition_log.copy()


class LogicalBoundary:
    """
    Maintains separation between realms without preventing verification.
    
    The boundary allows entities to prove knowledge without revealing it,
    enabling authentication while preserving logical separation.
    """
    
    def __init__(self, shared_realm: SharedRealm):
        """Initialize boundary with reference to shared realm."""
        self._shared_realm = shared_realm
        self._boundaries = {}  # entity_id -> SeparateRealm
        self._boundary_commitments = {}  # entity_id -> commitment
        
    def create_boundary(self, entity_id: str) -> SeparateRealm:
        """Create a new logical boundary for an entity."""
        if entity_id in self._boundaries:
            raise ValueError(f"Boundary already exists for entity {entity_id}")
            
        separate_realm = SeparateRealm(entity_id)
        self._boundaries[entity_id] = separate_realm
        
        # Register boundary existence in shared realm
        commitment = LogicalState(content={
            'type': 'boundary_declaration',
            'entity': entity_id,
            'marker': separate_realm.get_separation_marker()
        })
        self._shared_realm.register_commitment(entity_id, commitment)
        self._boundary_commitments[entity_id] = commitment
        
        return separate_realm
        
    def get_boundary(self, entity_id: str) -> Optional[SeparateRealm]:
        """Retrieve a boundary for an entity."""
        return self._boundaries.get(entity_id)
        
    def verify_separation(self, entity_id: str, knowledge: LogicalState) -> bool:
        """
        Verify that knowledge is properly separated.
        
        Ensures that claimed exclusive knowledge doesn't exist in shared realm.
        """
        # Check if knowledge exists in shared realm
        if self._shared_realm.contains(knowledge):
            return False  # Cannot be exclusive if it's shared
            
        # Check if entity has a boundary
        boundary = self._boundaries.get(entity_id)
        if not boundary:
            return False
            
        # Verify the boundary owns this knowledge
        return boundary.verify_ownership(knowledge)
        
    def create_verification_challenge(self, entity_id: str) -> Optional[str]:
        """
        Create a challenge that can verify boundary without crossing it.
        
        The challenge is shared, but the response requires exclusive knowledge.
        """
        if entity_id not in self._boundaries:
            return None
            
        # Generate challenge from shared information
        import hashlib
        import time
        
        shared_seed = f"{entity_id}:{time.time()}"
        challenge = hashlib.sha256(shared_seed.encode()).hexdigest()
        
        # Register challenge in shared realm
        challenge_state = LogicalState(content={
            'type': 'verification_challenge',
            'entity': entity_id,
            'challenge': challenge
        })
        self._shared_realm.add_witness(challenge_state)
        
        return challenge
        
    def verify_boundary_proof(self, entity_id: str, challenge: str, 
                            proof: LogicalState) -> bool:
        """
        Verify a proof without crossing the boundary.
        
        This allows authentication without knowledge revelation.
        """
        boundary = self._boundaries.get(entity_id)
        if not boundary:
            return False
            
        # Check if boundary has exclusive knowledge
        if not boundary.has_exclusive_knowledge():
            return False
            
        # Verify the proof matches what the boundary would generate
        expected_proof = boundary.get_proof_for_challenge(challenge)
        if not expected_proof:
            # Generate proof if not cached
            expected_proof = boundary.create_boundary_proof(challenge)
            
        return expected_proof.content['proof'] == proof.content.get('proof')
        
    def list_boundaries(self) -> list:
        """List all registered boundaries."""
        return list(self._boundaries.keys())
        
    def get_boundary_commitment(self, entity_id: str) -> Optional[LogicalState]:
        """Get the public commitment for a boundary."""
        return self._boundary_commitments.get(entity_id)