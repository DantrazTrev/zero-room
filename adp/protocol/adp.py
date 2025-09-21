"""
Axiom Distinction Protocol (ADP) Main Implementation
====================================================

The main protocol that orchestrates all components to provide
authentication based on pure logical principles.
"""

from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
import time
from ..core.realms import SharedRealm, SeparateRealm, LogicalState
from ..core.state import LogicalBoundary, StateTransition
from ..foundation.axioms import SharedAxiom, SharedMethod, SharedWitness
from ..entities.entity import Entity
from ..protocol.challenge import (
    SharedChallenge, ExclusiveApplication, ConsistencyVerification,
    ChallengeParameters, Challenge, ChallengeResponse
)
from ..verification.engine import (
    LogicalValidator, UniversalVerifier, IntegrityChecker,
    VerificationReport, VerificationResult
)


@dataclass
class ProtocolConfig:
    """Configuration for the ADP protocol."""
    min_witnesses: int = 2
    challenge_timeout: float = 60.0
    max_entities: int = 1000
    enable_logging: bool = True
    strict_mode: bool = True  # Enforce all logical constraints


class AxiomDistinctionProtocol:
    """
    Main protocol implementation that provides authentication
    through logical distinction between SHARED and SEPARATE.
    """
    
    def __init__(self, config: Optional[ProtocolConfig] = None):
        """
        Initialize the Axiom Distinction Protocol.
        
        Args:
            config: Optional protocol configuration
        """
        self.config = config or ProtocolConfig()
        
        # Initialize core components
        self.shared_realm = SharedRealm()
        self.logical_boundary = LogicalBoundary(self.shared_realm)
        self.state_transition = StateTransition()
        
        # Initialize foundation layer
        self.shared_axioms = SharedAxiom()
        self.shared_methods = SharedMethod()
        self.shared_witness = SharedWitness(self.config.min_witnesses)
        
        # Initialize protocol components
        self.challenge_system = SharedChallenge(self.shared_realm, self.shared_methods)
        self.exclusive_application = ExclusiveApplication()
        self.consistency_verification = ConsistencyVerification(
            self.shared_axioms, self.shared_methods
        )
        
        # Initialize verification engine
        self.logical_validator = LogicalValidator(self.shared_axioms)
        self.universal_verifier = UniversalVerifier(
            self.shared_realm, self.shared_methods, self.shared_witness
        )
        self.integrity_checker = IntegrityChecker(self.logical_boundary)
        
        # Entity registry
        self._entities: Dict[str, Entity] = {}
        
        # Protocol state
        self._protocol_state = {
            'initialized': time.time(),
            'total_authentications': 0,
            'successful_authentications': 0,
            'failed_authentications': 0,
            'active_challenges': 0
        }
        
        # Initialize protocol axioms in shared realm
        self._initialize_protocol_axioms()
        
    def _initialize_protocol_axioms(self):
        """Initialize fundamental protocol axioms in shared realm."""
        for axiom in self.shared_axioms.get_all_axioms():
            axiom_state = LogicalState(content={
                'type': 'axiom',
                'name': axiom.name,
                'statement': axiom.statement,
                'implications': axiom.implications
            })
            self.shared_realm.add_method(axiom_state)
            
    def register_entity(self, entity_id: str) -> Entity:
        """
        Register a new entity in the protocol.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            Registered Entity object
        """
        if entity_id in self._entities:
            raise ValueError(f"Entity {entity_id} already registered")
            
        if len(self._entities) >= self.config.max_entities:
            raise ValueError("Maximum entity limit reached")
            
        # Create new entity
        entity = Entity(entity_id, self.shared_realm, self.logical_boundary)
        self._entities[entity_id] = entity
        
        # Log registration
        if self.config.enable_logging:
            self._log_event('entity_registered', {'entity_id': entity_id})
            
        return entity
        
    def authenticate_entity(self, entity_id: str, 
                          challenger_id: Optional[str] = None) -> VerificationReport:
        """
        Authenticate an entity using the protocol.
        
        Args:
            entity_id: ID of entity to authenticate
            challenger_id: Optional ID of challenging entity
            
        Returns:
            VerificationReport with authentication result
        """
        # Check if entity is registered
        if entity_id not in self._entities:
            return VerificationReport(
                result=VerificationResult.INVALID,
                entity_id=entity_id,
                challenge_id=None,
                checks_performed=['registration'],
                checks_passed=[],
                checks_failed=['registration'],
                reason="Entity not registered",
                timestamp=time.time()
            )
            
        entity = self._entities[entity_id]
        
        # Generate challenge
        params = ChallengeParameters(
            difficulty=1,
            time_window=self.config.challenge_timeout,
            requires_witness=self.config.strict_mode
        )
        challenge = self.challenge_system.generate_challenge(entity_id, params)
        
        self._protocol_state['active_challenges'] += 1
        
        # Entity responds to challenge
        # In real implementation, entity would generate this internally
        # Here we simulate by accessing entity's separate realm
        boundary = self.logical_boundary.get_boundary(entity_id)
        if not boundary:
            return self._create_failed_report(entity_id, challenge.id, 
                                            "No boundary found")
            
        # Generate response using exclusive knowledge
        # This simulates what the entity would do internally
        exclusive_knowledge = boundary.get_separation_marker()  # Use marker as exclusive
        response = self.exclusive_application.apply_exclusive_knowledge(
            challenge, exclusive_knowledge
        )
        
        # Verify response
        report = self._verify_authentication(entity_id, challenge, response)
        
        # Update protocol state
        self._protocol_state['total_authentications'] += 1
        if report.is_successful():
            self._protocol_state['successful_authentications'] += 1
        else:
            self._protocol_state['failed_authentications'] += 1
            
        self._protocol_state['active_challenges'] -= 1
        
        # Add witnesses if required
        if self.config.strict_mode and challenger_id:
            response.add_witness(challenger_id)
            
        # Log authentication attempt
        if self.config.enable_logging:
            self._log_event('authentication_attempt', {
                'entity_id': entity_id,
                'challenger_id': challenger_id,
                'result': report.result.value,
                'success': report.is_successful()
            })
            
        return report
        
    def _verify_authentication(self, entity_id: str, challenge: Challenge,
                              response: ChallengeResponse) -> VerificationReport:
        """
        Perform comprehensive authentication verification.
        
        Args:
            entity_id: ID of entity being authenticated
            challenge: The challenge issued
            response: The response provided
            
        Returns:
            VerificationReport with results
        """
        # Step 1: Logical validation
        validation_report = self.logical_validator.validate_response(
            challenge, response
        )
        
        if not validation_report.is_successful():
            return validation_report
            
        # Step 2: Universal verification
        universal_report = self.universal_verifier.verify_authentication(
            entity_id, challenge, response
        )
        
        if not universal_report.is_successful():
            return universal_report
            
        # Step 3: Consistency verification
        is_consistent, reason = self.consistency_verification.verify_response_consistency(
            challenge, response
        )
        
        if not is_consistent:
            return self._create_failed_report(entity_id, challenge.id, reason)
            
        # Step 4: Integrity check
        integrity_ok, integrity_reason = self.integrity_checker.check_boundary_integrity(
            entity_id
        )
        
        if not integrity_ok:
            return self._create_failed_report(entity_id, challenge.id, 
                                            f"Integrity check failed: {integrity_reason}")
            
        # Step 5: Challenge-specific verification
        if not self.challenge_system.verify_challenge_response(challenge.id, response):
            return self._create_failed_report(entity_id, challenge.id,
                                            "Challenge verification failed")
            
        # All checks passed
        return VerificationReport(
            result=VerificationResult.VALID,
            entity_id=entity_id,
            challenge_id=challenge.id,
            checks_performed=['logical', 'universal', 'consistency', 'integrity', 'challenge'],
            checks_passed=['logical', 'universal', 'consistency', 'integrity', 'challenge'],
            checks_failed=[],
            reason="Authentication successful - all checks passed",
            timestamp=time.time()
        )
        
    def _create_failed_report(self, entity_id: str, challenge_id: Optional[str],
                             reason: str) -> VerificationReport:
        """Create a failed verification report."""
        return VerificationReport(
            result=VerificationResult.INVALID,
            entity_id=entity_id,
            challenge_id=challenge_id,
            checks_performed=['authentication'],
            checks_passed=[],
            checks_failed=['authentication'],
            reason=reason,
            timestamp=time.time()
        )
        
    def verify_entity_claim(self, entity_id: str, claim: str) -> bool:
        """
        Verify a claim made by an entity.
        
        Args:
            entity_id: ID of entity making claim
            claim: The claim to verify
            
        Returns:
            True if claim is verified
        """
        if entity_id not in self._entities:
            return False
            
        claim_state = LogicalState(content={'claim': claim, 'entity': entity_id})
        return self.universal_verifier.verify_entity_claim(entity_id, claim_state)
        
    def establish_mutual_authentication(self, entity1_id: str, 
                                       entity2_id: str) -> Tuple[bool, str]:
        """
        Establish mutual authentication between two entities.
        
        Args:
            entity1_id: First entity ID
            entity2_id: Second entity ID
            
        Returns:
            Tuple of (success, reason)
        """
        # Authenticate entity1 to entity2
        report1 = self.authenticate_entity(entity1_id, entity2_id)
        if not report1.is_successful():
            return False, f"Entity {entity1_id} authentication failed"
            
        # Authenticate entity2 to entity1
        report2 = self.authenticate_entity(entity2_id, entity1_id)
        if not report2.is_successful():
            return False, f"Entity {entity2_id} authentication failed"
            
        # Register mutual authentication in shared realm
        mutual_auth = LogicalState(content={
            'type': 'mutual_authentication',
            'entity1': entity1_id,
            'entity2': entity2_id,
            'timestamp': time.time(),
            'verified': True
        })
        
        self.shared_realm.add_witness(mutual_auth)
        
        return True, "Mutual authentication established"
        
    def get_protocol_state(self) -> Dict[str, Any]:
        """Get current protocol state and statistics."""
        # Clean up expired challenges
        expired = self.challenge_system.cleanup_expired_challenges()
        self._protocol_state['active_challenges'] -= expired
        
        return {
            **self._protocol_state,
            'registered_entities': len(self._entities),
            'boundaries_created': len(self.logical_boundary.list_boundaries()),
            'witnessed_facts': len(self.shared_witness.get_validated_facts()),
            'success_rate': (
                self._protocol_state['successful_authentications'] / 
                max(1, self._protocol_state['total_authentications'])
            )
        }
        
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log protocol events."""
        if not self.config.enable_logging:
            return
            
        # In production, this would write to a proper log
        # For now, we just track in memory
        log_entry = {
            'timestamp': time.time(),
            'event_type': event_type,
            'data': data
        }
        
        # Could extend to maintain full log history
        
    def demonstrate_authentication(self, entity_id: str) -> Dict[str, Any]:
        """
        Demonstrate the authentication process for an entity.
        
        This shows how authentication emerges from logical principles
        without relying on cryptographic assumptions.
        
        Args:
            entity_id: ID of entity to demonstrate
            
        Returns:
            Demonstration results
        """
        if entity_id not in self._entities:
            # Register entity first
            entity = self.register_entity(entity_id)
        else:
            entity = self._entities[entity_id]
            
        # Create separation declaration
        declaration = entity.make_separation_declaration(
            f"Entity {entity_id} possesses exclusive knowledge"
        )
        
        # Create boundary commitment
        commitment = entity.create_boundary_commitment("authentication_demo")
        
        # Perform authentication
        auth_report = self.authenticate_entity(entity_id)
        
        # Get integrity report
        integrity_report = self.integrity_checker.get_integrity_report(entity_id)
        
        return {
            'entity_id': entity_id,
            'declaration': {
                'claim': declaration.claim,
                'hash': declaration.get_declaration_hash(),
                'witnessed': declaration.is_witnessed()
            },
            'commitment': commitment.get_public_proof(),
            'authentication': {
                'result': auth_report.result.value,
                'success': auth_report.is_successful(),
                'checks_passed': auth_report.checks_passed,
                'reason': auth_report.reason
            },
            'integrity': integrity_report,
            'principle': "Authentication achieved through logical distinction alone"
        }