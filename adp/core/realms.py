"""
Realm Management System
=======================

Implements the fundamental distinction between SHARED and SEPARATE states.
These realms represent the ontological foundation of the protocol.
"""

from typing import Any, Dict, Set, Optional, Tuple, FrozenSet
from dataclasses import dataclass, field
from functools import reduce
import hashlib
import time


@dataclass(frozen=True)
class LogicalState:
    """Immutable representation of a logical state."""
    content: Any
    timestamp: float = field(default_factory=time.time)
    
    def __hash__(self):
        """Generate deterministic hash for logical state."""
        if isinstance(self.content, (list, dict, set)):
            content_str = str(sorted(str(self.content)))
        else:
            content_str = str(self.content)
        return hash((content_str, self.timestamp))


class SharedRealm:
    """
    Manages universally accessible information.
    
    The SharedRealm contains all information that exists simultaneously
    for all entities. This includes axioms, methods, and witnessed facts.
    """
    
    def __init__(self):
        """Initialize the shared realm with foundational axioms."""
        self._axioms: FrozenSet[LogicalState] = frozenset()
        self._methods: FrozenSet[LogicalState] = frozenset()
        self._witnesses: FrozenSet[LogicalState] = frozenset()
        self._commitments: Dict[str, LogicalState] = {}
        
        # Initialize with foundational axiom
        self._add_axiom(LogicalState(
            content="That which can be distinguished exists"
        ))
        
    def _add_axiom(self, axiom: LogicalState) -> None:
        """Add a new axiom to the shared realm."""
        self._axioms = self._axioms | {axiom}
        
    def add_method(self, method: LogicalState) -> None:
        """Add a universal verification method."""
        self._methods = self._methods | {method}
        
    def add_witness(self, witness: LogicalState) -> None:
        """Add a collectively observed fact."""
        self._witnesses = self._witnesses | {witness}
        
    def register_commitment(self, entity_id: str, commitment: LogicalState) -> None:
        """Register a boundary commitment from an entity."""
        self._commitments[entity_id] = commitment
        
    def get_commitment(self, entity_id: str) -> Optional[LogicalState]:
        """Retrieve a registered commitment."""
        return self._commitments.get(entity_id)
        
    def get_axioms(self) -> FrozenSet[LogicalState]:
        """Return all axioms (immutable)."""
        return self._axioms
        
    def get_methods(self) -> FrozenSet[LogicalState]:
        """Return all shared methods (immutable)."""
        return self._methods
        
    def get_witnesses(self) -> FrozenSet[LogicalState]:
        """Return all witnessed facts (immutable)."""
        return self._witnesses
        
    def contains(self, state: LogicalState) -> bool:
        """Check if a state exists in the shared realm."""
        return (state in self._axioms or 
                state in self._methods or 
                state in self._witnesses)
                
    def derive_truth(self, premise1: LogicalState, premise2: LogicalState) -> LogicalState:
        """Derive new truth from existing shared knowledge."""
        if self.contains(premise1) and self.contains(premise2):
            combined = f"{premise1.content} AND {premise2.content}"
            return LogicalState(content=combined)
        raise ValueError("Cannot derive from non-shared premises")


class SeparateRealm:
    """
    Manages entity-exclusive information with secure boundaries.
    
    The SeparateRealm maintains information that exists exclusively
    for one entity, ensuring logical separation from shared knowledge.
    """
    
    def __init__(self, entity_id: str):
        """Initialize a separate realm for a specific entity."""
        self._entity_id = entity_id
        self._exclusive_knowledge: FrozenSet[LogicalState] = frozenset()
        self._boundary_proofs: Dict[str, LogicalState] = {}
        self._separation_marker = self._generate_separation_marker()
        
    def _generate_separation_marker(self) -> str:
        """Generate a unique marker that defines this realm's boundary."""
        # Use logical necessity: entity_id + timestamp creates uniqueness
        timestamp = time.time()
        marker_content = f"{self._entity_id}:{timestamp}"
        return hashlib.sha256(marker_content.encode()).hexdigest()
        
    def add_exclusive_knowledge(self, knowledge: LogicalState) -> None:
        """Add knowledge that exists only in this separate realm."""
        # Ensure knowledge is marked as exclusive
        exclusive_content = {
            'original': knowledge.content,
            'realm': self._entity_id,
            'marker': self._separation_marker
        }
        exclusive_state = LogicalState(content=exclusive_content)
        self._exclusive_knowledge = self._exclusive_knowledge | {exclusive_state}
        
    def create_boundary_proof(self, challenge: str) -> LogicalState:
        """
        Create proof of separation without revealing content.
        
        This demonstrates knowledge of exclusive information without
        actually sharing that information.
        """
        # Apply exclusive knowledge to challenge
        proof_elements = []
        for knowledge in self._exclusive_knowledge:
            # Transform challenge using exclusive knowledge
            combined = f"{challenge}:{knowledge.content}"
            proof_hash = hashlib.sha256(str(combined).encode()).hexdigest()
            proof_elements.append(proof_hash)
            
        # Combine all proofs into single boundary proof
        combined_proof = reduce(lambda a, b: a + b, proof_elements, "")
        final_proof = hashlib.sha256(combined_proof.encode()).hexdigest()
        
        proof_state = LogicalState(content={
            'proof': final_proof,
            'challenge': challenge,
            'realm': self._entity_id
        })
        
        self._boundary_proofs[challenge] = proof_state
        return proof_state
        
    def verify_ownership(self, knowledge_claim: LogicalState) -> bool:
        """Verify if claimed knowledge belongs to this realm."""
        for exclusive in self._exclusive_knowledge:
            if exclusive.content.get('original') == knowledge_claim.content:
                return True
        return False
        
    def get_separation_marker(self) -> str:
        """Return the unique separation marker."""
        return self._separation_marker
        
    def has_exclusive_knowledge(self) -> bool:
        """Check if this realm contains any exclusive knowledge."""
        return len(self._exclusive_knowledge) > 0
        
    def get_proof_for_challenge(self, challenge: str) -> Optional[LogicalState]:
        """Retrieve a previously generated proof for a challenge."""
        return self._boundary_proofs.get(challenge)