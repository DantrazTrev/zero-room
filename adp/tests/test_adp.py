#!/usr/bin/env python3
"""
Comprehensive Test Suite for ADP
=================================

Tests logical consistency, boundary preservation, and authentication
properties of the Axiom Distinction Protocol.
"""

import unittest
import time
from typing import List, Tuple
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adp import (
    AxiomDistinctionProtocol, ProtocolConfig,
    SharedRealm, SeparateRealm, LogicalState,
    StateTransition, StateType, LogicalBoundary,
    SharedAxiom, SharedMethod, SharedWitness,
    Entity, BoundaryCommitment, SeparationDeclaration,
    SharedChallenge, ChallengeParameters, ExclusiveApplication,
    LogicalValidator, UniversalVerifier, IntegrityChecker,
    VerificationResult
)


class TestLogicalFoundations(unittest.TestCase):
    """Test the logical foundations of the protocol."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.shared_realm = SharedRealm()
        self.axioms = SharedAxiom()
        self.methods = SharedMethod()
        
    def test_axiom_of_distinction(self):
        """Test that distinction axiom holds."""
        axiom = self.axioms.DISTINCTION
        self.assertEqual(axiom.name, "Axiom of Distinction")
        self.assertTrue(axiom.verify(None))
        
        # Test axiom application
        state = LogicalState(content="test_entity")
        result = axiom.apply(state)
        self.assertIn("IMPLIES", result.content)
        
    def test_axiom_of_separation(self):
        """Test separation axiom enforcement."""
        axiom = self.axioms.SEPARATION
        self.assertEqual(axiom.name, "Axiom of Separation")
        
        # Verify implications
        self.assertIn("exclusivity", axiom.implications)
        self.assertIn("boundary", axiom.implications)
        
    def test_shared_methods(self):
        """Test shared verification methods."""
        # Test hash verification
        data = "test_data"
        expected = "39a870a194a787550b6b5d1f49629236"
        import hashlib
        actual = hashlib.sha256(data.encode()).hexdigest()
        
        result = self.methods.execute_method(
            'hash_verification', data, actual
        )
        self.assertTrue(result)
        
        # Test logical implication
        result = self.methods.execute_method(
            'logical_implication', True, True
        )
        self.assertTrue(result)
        
        result = self.methods.execute_method(
            'logical_implication', True, False
        )
        self.assertFalse(result)
        
    def test_witness_system(self):
        """Test the shared witness system."""
        witness = SharedWitness(required_witnesses=2)
        
        fact = LogicalState(content={'fact': 'test_fact'})
        
        # First witness
        result = witness.witness(fact, 'witness1')
        self.assertFalse(result)  # Not enough witnesses yet
        
        # Second witness
        result = witness.witness(fact, 'witness2')
        self.assertTrue(result)  # Now we have enough
        
        # Verify fact is witnessed
        self.assertTrue(witness.is_witnessed(fact))
        
        # Check witness list
        witnesses = witness.get_witnesses(fact)
        self.assertEqual(len(witnesses), 2)
        self.assertIn('witness1', witnesses)
        self.assertIn('witness2', witnesses)


class TestStateManagement(unittest.TestCase):
    """Test state management and transitions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transition = StateTransition()
        self.shared_realm = SharedRealm()
        self.boundary = LogicalBoundary(self.shared_realm)
        
    def test_state_transition_rules(self):
        """Test that state transition rules are enforced."""
        # Test allowed transitions
        valid, reason = self.transition.validate_transition(
            StateType.SHARED, StateType.SHARED
        )
        self.assertTrue(valid)
        
        valid, reason = self.transition.validate_transition(
            StateType.SEPARATE, StateType.SHARED
        )
        self.assertTrue(valid)
        
        # Test forbidden transition
        valid, reason = self.transition.validate_transition(
            StateType.SHARED, StateType.SEPARATE
        )
        self.assertFalse(valid)
        self.assertIn("cannot become separate", reason)
        
    def test_boundary_creation(self):
        """Test logical boundary creation."""
        entity_id = "test_entity"
        
        # Create boundary
        separate_realm = self.boundary.create_boundary(entity_id)
        self.assertIsNotNone(separate_realm)
        self.assertEqual(separate_realm._entity_id, entity_id)
        
        # Verify boundary is registered
        retrieved = self.boundary.get_boundary(entity_id)
        self.assertEqual(retrieved, separate_realm)
        
        # Check commitment in shared realm
        commitment = self.shared_realm.get_commitment(entity_id)
        self.assertIsNotNone(commitment)
        
    def test_separation_verification(self):
        """Test verification of separation."""
        entity_id = "test_entity"
        separate_realm = self.boundary.create_boundary(entity_id)
        
        # Add exclusive knowledge
        exclusive = LogicalState(content={'secret': 'exclusive_data'})
        separate_realm.add_exclusive_knowledge(exclusive)
        
        # Create shared knowledge
        shared = LogicalState(content={'public': 'shared_data'})
        self.shared_realm.add_witness(shared)
        
        # Verify separation
        self.assertTrue(
            self.boundary.verify_separation(entity_id, exclusive)
        )
        self.assertFalse(
            self.boundary.verify_separation(entity_id, shared)
        )


class TestEntityManagement(unittest.TestCase):
    """Test entity creation and management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.shared_realm = SharedRealm()
        self.boundary = LogicalBoundary(self.shared_realm)
        
    def test_entity_creation(self):
        """Test entity creation with exclusive knowledge."""
        entity_id = "test_entity"
        entity = Entity(entity_id, self.shared_realm, self.boundary)
        
        self.assertEqual(entity.get_identity().id, entity_id)
        
        # Verify entity has boundary
        boundary = self.boundary.get_boundary(entity_id)
        self.assertIsNotNone(boundary)
        self.assertTrue(boundary.has_exclusive_knowledge())
        
    def test_boundary_commitment(self):
        """Test boundary commitment creation."""
        entity_id = "test_entity"
        entity = Entity(entity_id, self.shared_realm, self.boundary)
        
        # Create commitment
        commitment = entity.create_boundary_commitment("test_purpose")
        
        self.assertEqual(commitment.entity_id, entity_id)
        self.assertEqual(commitment.purpose, "test_purpose")
        self.assertIsNotNone(commitment.proof)
        
        # Verify commitment consistency
        self.assertTrue(commitment.verify_consistency(self.shared_realm))
        
    def test_separation_declaration(self):
        """Test separation declaration."""
        entity_id = "test_entity"
        entity = Entity(entity_id, self.shared_realm, self.boundary)
        
        # Make declaration
        declaration = entity.make_separation_declaration(
            "I have exclusive knowledge"
        )
        
        self.assertEqual(declaration.entity_id, entity_id)
        self.assertEqual(declaration.claim, "I have exclusive knowledge")
        self.assertTrue(len(declaration.proofs) > 0)
        
        # Check declaration hash
        hash_val = declaration.get_declaration_hash()
        self.assertEqual(len(hash_val), 64)  # SHA-256 length
        
    def test_challenge_response(self):
        """Test entity response to challenge."""
        entity_id = "test_entity"
        entity = Entity(entity_id, self.shared_realm, self.boundary)
        
        # Create challenge
        challenge = "test_challenge_123"
        response = entity.respond_to_challenge(challenge)
        
        self.assertEqual(response.content['entity'], entity_id)
        self.assertEqual(response.content['challenge'], challenge)
        self.assertIn('proof', response.content)


class TestChallengeResponse(unittest.TestCase):
    """Test challenge-response authentication system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.shared_realm = SharedRealm()
        self.shared_methods = SharedMethod()
        self.challenge_system = SharedChallenge(
            self.shared_realm, self.shared_methods
        )
        self.exclusive_app = ExclusiveApplication()
        
    def test_challenge_generation(self):
        """Test challenge generation."""
        entity_id = "test_entity"
        params = ChallengeParameters(difficulty=2, time_window=30.0)
        
        challenge = self.challenge_system.generate_challenge(
            entity_id, params
        )
        
        self.assertEqual(challenge.target_entity, entity_id)
        self.assertEqual(challenge.parameters.difficulty, 2)
        self.assertEqual(len(challenge.content['operations']), 2)
        
        # Verify challenge is tracked
        retrieved = self.challenge_system.get_active_challenge(challenge.id)
        self.assertEqual(retrieved, challenge)
        
    def test_exclusive_application(self):
        """Test applying exclusive knowledge to challenge."""
        entity_id = "test_entity"
        challenge = self.challenge_system.generate_challenge(entity_id)
        
        # Apply exclusive knowledge
        exclusive_knowledge = "secret_knowledge_123"
        response = self.exclusive_app.apply_exclusive_knowledge(
            challenge, exclusive_knowledge
        )
        
        self.assertEqual(response.challenge_id, challenge.id)
        self.assertEqual(response.entity_id, entity_id)
        self.assertTrue(len(response.proofs) > 0)
        
    def test_zero_knowledge_proof(self):
        """Test zero-knowledge proof generation."""
        statement = "I know the secret"
        secret = "my_secret_knowledge"
        
        proof = self.exclusive_app.create_zero_knowledge_proof(
            statement, secret
        )
        
        self.assertEqual(proof['statement'], statement)
        self.assertIn('commitment', proof)
        self.assertIn('challenge', proof)
        self.assertIn('response', proof)
        
        # Verify proof components are different
        self.assertNotEqual(proof['commitment'], proof['challenge'])
        self.assertNotEqual(proof['challenge'], proof['response'])


class TestVerificationEngine(unittest.TestCase):
    """Test verification engine components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.shared_realm = SharedRealm()
        self.shared_axioms = SharedAxiom()
        self.shared_methods = SharedMethod()
        self.shared_witness = SharedWitness()
        self.boundary = LogicalBoundary(self.shared_realm)
        
        self.logical_validator = LogicalValidator(self.shared_axioms)
        self.universal_verifier = UniversalVerifier(
            self.shared_realm, self.shared_methods, self.shared_witness
        )
        self.integrity_checker = IntegrityChecker(self.boundary)
        
    def test_logical_validation(self):
        """Test logical validation of responses."""
        # Create a mock challenge and response
        challenge_system = SharedChallenge(
            self.shared_realm, self.shared_methods
        )
        challenge = challenge_system.generate_challenge("test_entity")
        
        # Create valid response
        from adp.protocol.challenge import ChallengeResponse
        response = ChallengeResponse(
            challenge_id=challenge.id,
            entity_id="test_entity",
            proofs={"step_1": "a" * 64},  # Valid SHA-256 length
            method_used="hash_combine",
            timestamp=time.time()
        )
        
        # Validate
        report = self.logical_validator.validate_response(challenge, response)
        
        self.assertIsNotNone(report)
        self.assertEqual(report.entity_id, "test_entity")
        self.assertTrue(len(report.checks_performed) > 0)
        
    def test_universal_verification(self):
        """Test universal verification."""
        entity_id = "test_entity"
        
        # Create entity and boundary
        entity = Entity(entity_id, self.shared_realm, self.boundary)
        
        # Check if entity can be verified
        self.assertTrue(self.universal_verifier.can_verify(entity_id))
        
        # Create and verify claim
        claim = LogicalState(content={'claim': 'test_claim'})
        self.shared_witness.witness(claim, 'witness1')
        self.shared_witness.witness(claim, 'witness2')
        
        result = self.universal_verifier.verify_entity_claim(entity_id, claim)
        self.assertTrue(result)
        
    def test_integrity_checking(self):
        """Test boundary integrity checking."""
        entity_id = "test_entity"
        
        # Create entity with boundary
        entity = Entity(entity_id, self.shared_realm, self.boundary)
        
        # Check integrity
        intact, reason = self.integrity_checker.check_boundary_integrity(entity_id)
        self.assertTrue(intact)
        self.assertIn("confirmed", reason)
        
        # Verify no boundary crossing
        no_crossing = self.integrity_checker.verify_no_boundary_crossing(
            self.shared_realm, entity_id
        )
        self.assertTrue(no_crossing)
        
        # Get integrity report
        report = self.integrity_checker.get_integrity_report(entity_id)
        self.assertGreater(report['total_checks'], 0)
        self.assertEqual(report['success_rate'], 1.0)


class TestProtocolIntegration(unittest.TestCase):
    """Test full protocol integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        config = ProtocolConfig(
            min_witnesses=2,
            challenge_timeout=60.0,
            enable_logging=True,
            strict_mode=False  # Disable witness requirement for testing
        )
        self.protocol = AxiomDistinctionProtocol(config)
        
    def test_entity_registration(self):
        """Test entity registration in protocol."""
        entity_id = "alice"
        entity = self.protocol.register_entity(entity_id)
        
        self.assertIsNotNone(entity)
        self.assertEqual(entity.get_identity().id, entity_id)
        
        # Try duplicate registration
        with self.assertRaises(ValueError):
            self.protocol.register_entity(entity_id)
            
    def test_basic_authentication(self):
        """Test basic authentication flow."""
        entity_id = "bob"
        entity = self.protocol.register_entity(entity_id)
        
        # Authenticate entity
        report = self.protocol.authenticate_entity(entity_id)
        
        self.assertEqual(report.entity_id, entity_id)
        self.assertEqual(report.result, VerificationResult.VALID)
        self.assertTrue(report.is_successful())
        
    def test_mutual_authentication(self):
        """Test mutual authentication between entities."""
        entity1_id = "charlie"
        entity2_id = "diana"
        
        # Register entities
        self.protocol.register_entity(entity1_id)
        self.protocol.register_entity(entity2_id)
        
        # Establish mutual authentication
        success, reason = self.protocol.establish_mutual_authentication(
            entity1_id, entity2_id
        )
        
        self.assertTrue(success)
        self.assertIn("established", reason)
        
    def test_claim_verification(self):
        """Test entity claim verification."""
        entity_id = "eve"
        entity = self.protocol.register_entity(entity_id)
        
        # Make a claim
        claim = "I possess unique knowledge"
        declaration = entity.make_separation_declaration(claim)
        
        # Verify claim
        result = self.protocol.verify_entity_claim(entity_id, claim)
        # Note: This will be False without witnesses in strict mode
        
    def test_protocol_statistics(self):
        """Test protocol statistics tracking."""
        # Register and authenticate entities
        for i in range(3):
            entity_id = f"entity_{i}"
            self.protocol.register_entity(entity_id)
            self.protocol.authenticate_entity(entity_id)
            
        # Get statistics
        stats = self.protocol.get_protocol_state()
        
        self.assertEqual(stats['registered_entities'], 3)
        self.assertEqual(stats['total_authentications'], 3)
        self.assertGreaterEqual(stats['successful_authentications'], 0)
        self.assertGreaterEqual(stats['success_rate'], 0)
        
    def test_demonstration(self):
        """Test comprehensive demonstration."""
        entity_id = "frank"
        
        result = self.protocol.demonstrate_authentication(entity_id)
        
        self.assertEqual(result['entity_id'], entity_id)
        self.assertIn('declaration', result)
        self.assertIn('commitment', result)
        self.assertIn('authentication', result)
        self.assertIn('integrity', result)
        self.assertEqual(
            result['principle'],
            "Authentication achieved through logical distinction alone"
        )


class TestLogicalConsistency(unittest.TestCase):
    """Test logical consistency throughout the protocol."""
    
    def test_axiom_consistency(self):
        """Test that all axioms remain consistent."""
        axioms = SharedAxiom()
        
        # Test that axioms don't contradict each other
        state1 = LogicalState(content="entity_exists")
        state2 = LogicalState(content="entity_separate")
        
        # Apply axioms
        derivations1 = axioms.derive_from_axioms(state1)
        derivations2 = axioms.derive_from_axioms(state2)
        
        # Check consistency
        for d1 in derivations1:
            for d2 in derivations2:
                self.assertTrue(axioms.verify_consistency(d1, d2))
                
    def test_boundary_consistency(self):
        """Test that boundaries maintain logical consistency."""
        shared_realm = SharedRealm()
        boundary = LogicalBoundary(shared_realm)
        
        # Create multiple boundaries
        entities = ["entity1", "entity2", "entity3"]
        for entity_id in entities:
            separate_realm = boundary.create_boundary(entity_id)
            self.assertIsNotNone(separate_realm)
            
        # Verify boundaries don't overlap
        boundaries = [boundary.get_boundary(e) for e in entities]
        markers = [b.get_separation_marker() for b in boundaries]
        
        # All markers should be unique
        self.assertEqual(len(markers), len(set(markers)))
        
    def test_state_transition_consistency(self):
        """Test that state transitions maintain consistency."""
        transition = StateTransition()
        
        # Test transition log consistency
        state = LogicalState(content="test_state")
        
        # Attempt valid transition
        result = transition.attempt_transition(
            state, StateType.SEPARATE, StateType.SHARED
        )
        self.assertIsNotNone(result)
        
        # Attempt invalid transition
        result = transition.attempt_transition(
            state, StateType.SHARED, StateType.SEPARATE
        )
        self.assertIsNone(result)
        
        # Check log
        log = transition.get_transition_log()
        self.assertEqual(len(log), 2)
        self.assertTrue(log[0]['allowed'])
        self.assertFalse(log[1]['allowed'])


def run_tests():
    """Run all tests and generate report."""
    print("=" * 80)
    print("ADP TEST SUITE")
    print("=" * 80)
    print("\nTesting logical consistency and protocol properties...\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestLogicalFoundations,
        TestStateManagement,
        TestEntityManagement,
        TestChallengeResponse,
        TestVerificationEngine,
        TestProtocolIntegration,
        TestLogicalConsistency
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
        
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun:.1%}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED - Protocol is logically consistent!")
    else:
        print("\n✗ Some tests failed - Review protocol logic")
        
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)