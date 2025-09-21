"""
Entity Management System
========================

Implements entities with unique SEPARATE_KNOWLEDGE capacity,
boundary commitments, and separation declarations.
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
import hashlib
import secrets
from ..core.realms import LogicalState, SharedRealm, SeparateRealm
from ..core.state import LogicalBoundary, StateType


@dataclass
class EntityIdentity:
    """Represents the identity of an entity in the protocol."""
    id: str
    creation_time: float
    public_marker: str
    
    def __hash__(self):
        return hash((self.id, self.creation_time, self.public_marker))


class Entity:
    """
    Represents an entity with unique SEPARATE_KNOWLEDGE capacity.
    
    Each entity can maintain exclusive knowledge while participating
    in the shared protocol through boundary commitments.
    """
    
    def __init__(self, entity_id: str, shared_realm: SharedRealm, 
                 logical_boundary: LogicalBoundary):
        """
        Initialize an entity with connection to shared and separate realms.
        
        Args:
            entity_id: Unique identifier for the entity
            shared_realm: Reference to the shared realm
            logical_boundary: System managing realm boundaries
        """
        self._identity = EntityIdentity(
            id=entity_id,
            creation_time=LogicalState(content="").timestamp,
            public_marker=self._generate_public_marker(entity_id)
        )
        
        self._shared_realm = shared_realm
        self._logical_boundary = logical_boundary
        
        # Create separate realm for this entity
        self._separate_realm = logical_boundary.create_boundary(entity_id)
        
        # Initialize knowledge stores
        self._public_declarations: List[LogicalState] = []
        self._boundary_commitments: List['BoundaryCommitment'] = []
        
        # Generate initial exclusive knowledge
        self._initialize_exclusive_knowledge()
        
    def _generate_public_marker(self, entity_id: str) -> str:
        """Generate a public marker for the entity."""
        marker_content = f"ENTITY:{entity_id}"
        return hashlib.sha256(marker_content.encode()).hexdigest()[:16]
        
    def _initialize_exclusive_knowledge(self) -> None:
        """Initialize entity with some exclusive knowledge."""
        # Generate secret that only this entity knows
        secret = secrets.token_hex(32)
        secret_state = LogicalState(content={
            'type': 'exclusive_secret',
            'value': secret,
            'entity': self._identity.id
        })
        self._separate_realm.add_exclusive_knowledge(secret_state)
        
        # Generate derived knowledge from secret
        derived = hashlib.sha256(f"{secret}:derived".encode()).hexdigest()
        derived_state = LogicalState(content={
            'type': 'derived_knowledge',
            'value': derived,
            'source': 'exclusive_secret'
        })
        self._separate_realm.add_exclusive_knowledge(derived_state)
        
    def create_boundary_commitment(self, purpose: str) -> 'BoundaryCommitment':
        """
        Create a commitment that proves separation without revealing content.
        
        Args:
            purpose: The purpose of this commitment
            
        Returns:
            BoundaryCommitment object
        """
        # Generate commitment using exclusive knowledge
        challenge = f"{self._identity.id}:{purpose}:{LogicalState('').timestamp}"
        proof = self._separate_realm.create_boundary_proof(challenge)
        
        commitment = BoundaryCommitment(
            entity_id=self._identity.id,
            purpose=purpose,
            proof=proof,
            challenge=challenge
        )
        
        self._boundary_commitments.append(commitment)
        
        # Register commitment in shared realm
        commitment_state = LogicalState(content={
            'type': 'boundary_commitment',
            'entity': self._identity.id,
            'purpose': purpose,
            'proof_hash': proof.content['proof'][:16]  # Only share partial proof
        })
        self._shared_realm.add_witness(commitment_state)
        
        return commitment
        
    def make_separation_declaration(self, claim: str) -> 'SeparationDeclaration':
        """
        Declare possession of exclusive knowledge.
        
        This is a public claim that the entity has knowledge
        that no other entity possesses.
        
        Args:
            claim: Description of the exclusive knowledge claim
            
        Returns:
            SeparationDeclaration object
        """
        # Create declaration
        declaration = SeparationDeclaration(
            entity_id=self._identity.id,
            claim=claim,
            timestamp=LogicalState(content="").timestamp
        )
        
        # Generate proof of capability
        proof = self._separate_realm.create_boundary_proof(claim)
        declaration.add_proof(proof)
        
        # Make public declaration
        declaration_state = LogicalState(content={
            'type': 'separation_declaration',
            'entity': self._identity.id,
            'claim': claim,
            'proof_exists': True
        })
        
        self._shared_realm.add_witness(declaration_state)
        self._public_declarations.append(declaration_state)
        
        return declaration
        
    def respond_to_challenge(self, challenge: str) -> LogicalState:
        """
        Respond to an authentication challenge using exclusive knowledge.
        
        Args:
            challenge: The challenge from the protocol
            
        Returns:
            Response proving exclusive knowledge
        """
        # Generate response using separate realm
        response = self._separate_realm.create_boundary_proof(challenge)
        
        # Create public response (without revealing exclusive knowledge)
        public_response = LogicalState(content={
            'type': 'challenge_response',
            'entity': self._identity.id,
            'challenge': challenge,
            'proof': response.content['proof'],
            'timestamp': response.timestamp
        })
        
        return public_response
        
    def verify_other_entity(self, other_id: str, challenge: str, 
                          response: LogicalState) -> bool:
        """
        Verify another entity's response to a challenge.
        
        This uses only shared methods and information.
        
        Args:
            other_id: ID of the entity being verified
            challenge: The challenge that was issued
            response: The entity's response
            
        Returns:
            True if verification succeeds
        """
        # Use logical boundary to verify without accessing exclusive knowledge
        return self._logical_boundary.verify_boundary_proof(
            other_id, challenge, response
        )
        
    def add_exclusive_knowledge(self, knowledge: Any) -> None:
        """Add new exclusive knowledge to the entity's separate realm."""
        knowledge_state = LogicalState(content=knowledge)
        self._separate_realm.add_exclusive_knowledge(knowledge_state)
        
    def get_identity(self) -> EntityIdentity:
        """Return the entity's identity."""
        return self._identity
        
    def get_public_declarations(self) -> List[LogicalState]:
        """Return all public declarations made by this entity."""
        return self._public_declarations.copy()
        
    def get_boundary_commitments(self) -> List['BoundaryCommitment']:
        """Return all boundary commitments made by this entity."""
        return self._boundary_commitments.copy()


@dataclass
class BoundaryCommitment:
    """
    Represents a commitment that proves separation exists without revealing content.
    
    This is the fundamental mechanism for authentication without knowledge revelation.
    """
    entity_id: str
    purpose: str
    proof: LogicalState
    challenge: str
    verified: bool = False
    
    def get_public_proof(self) -> Dict[str, Any]:
        """
        Get the public portion of the proof.
        
        This can be shared without revealing exclusive knowledge.
        """
        return {
            'entity': self.entity_id,
            'purpose': self.purpose,
            'proof_hash': self.proof.content['proof'][:16],
            'challenge_hash': hashlib.sha256(self.challenge.encode()).hexdigest()[:16]
        }
        
    def verify_consistency(self, shared_realm: SharedRealm) -> bool:
        """
        Verify the commitment is consistent with shared knowledge.
        
        Args:
            shared_realm: The shared realm to check against
            
        Returns:
            True if consistent
        """
        # Check if entity has registered boundary
        commitment = shared_realm.get_commitment(self.entity_id)
        if not commitment:
            return False
            
        # Verify commitment matches registration
        if commitment.content.get('entity') != self.entity_id:
            return False
            
        self.verified = True
        return True
        
    def combine_with(self, other: 'BoundaryCommitment') -> 'BoundaryCommitment':
        """
        Combine two commitments to create a stronger proof.
        
        Args:
            other: Another boundary commitment
            
        Returns:
            Combined commitment
        """
        if self.entity_id != other.entity_id:
            raise ValueError("Cannot combine commitments from different entities")
            
        # Combine proofs
        combined_proof_content = {
            'type': 'combined_proof',
            'proof1': self.proof.content['proof'],
            'proof2': other.proof.content['proof'],
            'combined': hashlib.sha256(
                f"{self.proof.content['proof']}:{other.proof.content['proof']}".encode()
            ).hexdigest()
        }
        
        combined_proof = LogicalState(content=combined_proof_content)
        combined_challenge = f"{self.challenge}:{other.challenge}"
        
        return BoundaryCommitment(
            entity_id=self.entity_id,
            purpose=f"{self.purpose} AND {other.purpose}",
            proof=combined_proof,
            challenge=combined_challenge
        )


@dataclass
class SeparationDeclaration:
    """
    Public declaration that an entity possesses exclusive knowledge.
    
    This establishes the entity's claim to unique information
    that can be verified through challenges.
    """
    entity_id: str
    claim: str
    timestamp: float
    proofs: List[LogicalState] = field(default_factory=list)
    witnesses: List[str] = field(default_factory=list)
    
    def add_proof(self, proof: LogicalState) -> None:
        """Add a proof supporting the declaration."""
        self.proofs.append(proof)
        
    def add_witness(self, witness_id: str) -> None:
        """Add a witness who has verified the declaration."""
        if witness_id not in self.witnesses:
            self.witnesses.append(witness_id)
            
    def is_witnessed(self, required_witnesses: int = 2) -> bool:
        """Check if declaration has sufficient witnesses."""
        return len(self.witnesses) >= required_witnesses
        
    def get_declaration_hash(self) -> str:
        """Generate a hash of the declaration for reference."""
        content = f"{self.entity_id}:{self.claim}:{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()
        
    def to_logical_state(self) -> LogicalState:
        """Convert declaration to a logical state."""
        return LogicalState(content={
            'type': 'separation_declaration',
            'entity': self.entity_id,
            'claim': self.claim,
            'timestamp': self.timestamp,
            'proof_count': len(self.proofs),
            'witness_count': len(self.witnesses),
            'declaration_hash': self.get_declaration_hash()
        })