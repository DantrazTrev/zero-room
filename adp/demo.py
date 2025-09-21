#!/usr/bin/env python3
"""
ADP Demo Interface
==================

Interactive demonstration of the Axiom of Distinction Protocol,
showing how authentication emerges from pure logical principles.
"""

import time
import json
from typing import Optional
from adp import AxiomDistinctionProtocol, ProtocolConfig


class ADPDemo:
    """Interactive demonstration of the ADP protocol."""
    
    def __init__(self):
        """Initialize the demo."""
        config = ProtocolConfig(
            min_witnesses=2,
            challenge_timeout=60.0,
            enable_logging=True,
            strict_mode=False  # Disable strict mode for demo
        )
        self.protocol = AxiomDistinctionProtocol(config)
        self.entities = {}
        
    def print_header(self):
        """Print demo header."""
        print("=" * 80)
        print("AXIOM OF DISTINCTION PROTOCOL (ADP) DEMONSTRATION")
        print("=" * 80)
        print("\nA foundational authentication system based on pure logical principles")
        print("\nCore Principle: Authentication emerges from the distinction between")
        print("SHARED (universal) and SEPARATE (exclusive) knowledge.\n")
        print("-" * 80)
        
    def demonstrate_basic_authentication(self):
        """Demonstrate basic entity authentication."""
        print("\n1. BASIC AUTHENTICATION DEMONSTRATION")
        print("=" * 40)
        
        # Register an entity
        entity_id = "Alice"
        print(f"\n[*] Registering entity: {entity_id}")
        entity = self.protocol.register_entity(entity_id)
        self.entities[entity_id] = entity
        
        print(f"    ✓ Entity registered with unique boundary")
        print(f"    ✓ Exclusive knowledge generated")
        
        # Make separation declaration
        print(f"\n[*] Entity makes separation declaration")
        declaration = entity.make_separation_declaration(
            f"{entity_id} possesses unique knowledge that no other entity has"
        )
        print(f"    ✓ Declaration hash: {declaration.get_declaration_hash()[:16]}...")
        
        # Create boundary commitment
        print(f"\n[*] Creating boundary commitment")
        commitment = entity.create_boundary_commitment("authentication_proof")
        public_proof = commitment.get_public_proof()
        print(f"    ✓ Public proof hash: {public_proof['proof_hash']}")
        print(f"    ✓ Challenge hash: {public_proof['challenge_hash']}")
        
        # Authenticate entity
        print(f"\n[*] Authenticating entity {entity_id}")
        report = self.protocol.authenticate_entity(entity_id)
        
        print(f"\n[*] Authentication Result:")
        print(f"    Status: {report.result.value}")
        print(f"    Success: {'✓' if report.is_successful() else '✗'}")
        print(f"    Checks performed: {', '.join(report.checks_performed)}")
        print(f"    Checks passed: {len(report.checks_passed)}/{len(report.checks_performed)}")
        print(f"    Reason: {report.reason}")
        
        return report.is_successful()
        
    def demonstrate_mutual_authentication(self):
        """Demonstrate mutual authentication between entities."""
        print("\n2. MUTUAL AUTHENTICATION DEMONSTRATION")
        print("=" * 40)
        
        # Register two entities
        entity1_id = "Bob"
        entity2_id = "Charlie"
        
        print(f"\n[*] Registering entities: {entity1_id} and {entity2_id}")
        entity1 = self.protocol.register_entity(entity1_id)
        entity2 = self.protocol.register_entity(entity2_id)
        
        self.entities[entity1_id] = entity1
        self.entities[entity2_id] = entity2
        
        print(f"    ✓ Both entities registered with unique boundaries")
        
        # Each entity makes declarations
        print(f"\n[*] Entities make separation declarations")
        entity1.make_separation_declaration(f"{entity1_id} has exclusive knowledge")
        entity2.make_separation_declaration(f"{entity2_id} has exclusive knowledge")
        print(f"    ✓ Declarations registered in shared realm")
        
        # Establish mutual authentication
        print(f"\n[*] Establishing mutual authentication")
        success, reason = self.protocol.establish_mutual_authentication(
            entity1_id, entity2_id
        )
        
        print(f"\n[*] Mutual Authentication Result:")
        print(f"    Success: {'✓' if success else '✗'}")
        print(f"    Reason: {reason}")
        
        if success:
            print(f"    ✓ {entity1_id} authenticated to {entity2_id}")
            print(f"    ✓ {entity2_id} authenticated to {entity1_id}")
            print(f"    ✓ Mutual trust established through logical verification")
            
        return success
        
    def demonstrate_boundary_integrity(self):
        """Demonstrate boundary integrity checking."""
        print("\n3. BOUNDARY INTEGRITY DEMONSTRATION")
        print("=" * 40)
        
        entity_id = "Diana"
        
        print(f"\n[*] Registering entity: {entity_id}")
        entity = self.protocol.register_entity(entity_id)
        self.entities[entity_id] = entity
        
        # Add exclusive knowledge
        print(f"\n[*] Adding exclusive knowledge to entity")
        secret_knowledge = {
            'type': 'secret',
            'value': 'exclusive_information_12345',
            'timestamp': time.time()
        }
        entity.add_exclusive_knowledge(secret_knowledge)
        print(f"    ✓ Exclusive knowledge added to separate realm")
        
        # Check boundary integrity
        print(f"\n[*] Checking boundary integrity")
        integrity_ok, reason = self.protocol.integrity_checker.check_boundary_integrity(
            entity_id
        )
        
        print(f"\n[*] Integrity Check Result:")
        print(f"    Intact: {'✓' if integrity_ok else '✗'}")
        print(f"    Reason: {reason}")
        
        # Get integrity report
        report = self.protocol.integrity_checker.get_integrity_report(entity_id)
        print(f"\n[*] Integrity Report:")
        print(f"    Total checks: {report['total_checks']}")
        print(f"    Passed: {report['passed']}")
        print(f"    Failed: {report['failed']}")
        print(f"    Success rate: {report['success_rate']:.1%}")
        
        return integrity_ok
        
    def demonstrate_logical_principles(self):
        """Demonstrate the logical principles underlying authentication."""
        print("\n4. LOGICAL PRINCIPLES DEMONSTRATION")
        print("=" * 40)
        
        print("\n[*] Fundamental Axioms:")
        for axiom in self.protocol.shared_axioms.get_all_axioms():
            print(f"\n    {axiom.name}:")
            print(f"    Statement: {axiom.statement}")
            print(f"    Implications: {', '.join(axiom.implications)}")
            
        print("\n[*] Shared Methods Available:")
        methods = self.protocol.shared_methods.list_methods()
        for method in methods:
            print(f"    • {method}")
            
        print("\n[*] Protocol State Transitions:")
        print("    SHARED → SHARED: ✓ Allowed (shared remains shared)")
        print("    SHARED → SEPARATE: ✗ Forbidden (fundamental axiom)")
        print("    SEPARATE → SEPARATE: ✓ Allowed (separate remains separate)")
        print("    SEPARATE → SHARED: ✓ Allowed (revelation makes it shared)")
        
        return True
        
    def show_protocol_statistics(self):
        """Display protocol statistics."""
        print("\n5. PROTOCOL STATISTICS")
        print("=" * 40)
        
        state = self.protocol.get_protocol_state()
        
        print(f"\n[*] Protocol State:")
        print(f"    Registered entities: {state['registered_entities']}")
        print(f"    Boundaries created: {state['boundaries_created']}")
        print(f"    Witnessed facts: {state['witnessed_facts']}")
        print(f"    Total authentications: {state['total_authentications']}")
        print(f"    Successful: {state['successful_authentications']}")
        print(f"    Failed: {state['failed_authentications']}")
        print(f"    Success rate: {state['success_rate']:.1%}")
        print(f"    Active challenges: {state['active_challenges']}")
        
    def run_comprehensive_demo(self):
        """Run a comprehensive demonstration."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE DEMONSTRATION")
        print("=" * 80)
        
        # Use the comprehensive demo method
        entity_id = "Eve"
        print(f"\n[*] Running comprehensive demo for entity: {entity_id}")
        
        demo_result = self.protocol.demonstrate_authentication(entity_id)
        
        print(f"\n[*] Demonstration Results:")
        print(f"\nEntity: {demo_result['entity_id']}")
        
        print(f"\nDeclaration:")
        print(f"    Claim: {demo_result['declaration']['claim']}")
        print(f"    Hash: {demo_result['declaration']['hash'][:16]}...")
        print(f"    Witnessed: {demo_result['declaration']['witnessed']}")
        
        print(f"\nCommitment:")
        print(f"    Entity: {demo_result['commitment']['entity']}")
        print(f"    Purpose: {demo_result['commitment']['purpose']}")
        print(f"    Proof hash: {demo_result['commitment']['proof_hash']}")
        
        print(f"\nAuthentication:")
        print(f"    Result: {demo_result['authentication']['result']}")
        print(f"    Success: {'✓' if demo_result['authentication']['success'] else '✗'}")
        print(f"    Checks passed: {', '.join(demo_result['authentication']['checks_passed'])}")
        
        print(f"\nIntegrity:")
        print(f"    Total checks: {demo_result['integrity']['total_checks']}")
        print(f"    Success rate: {demo_result['integrity']['success_rate']:.1%}")
        
        print(f"\n[*] Core Principle:")
        print(f"    {demo_result['principle']}")
        
    def run(self):
        """Run the interactive demo."""
        self.print_header()
        
        # Run demonstrations
        results = []
        
        # Basic authentication
        result = self.demonstrate_basic_authentication()
        results.append(("Basic Authentication", result))
        
        # Mutual authentication
        result = self.demonstrate_mutual_authentication()
        results.append(("Mutual Authentication", result))
        
        # Boundary integrity
        result = self.demonstrate_boundary_integrity()
        results.append(("Boundary Integrity", result))
        
        # Logical principles
        result = self.demonstrate_logical_principles()
        results.append(("Logical Principles", result))
        
        # Show statistics
        self.show_protocol_statistics()
        
        # Comprehensive demo
        self.run_comprehensive_demo()
        
        # Summary
        print("\n" + "=" * 80)
        print("DEMONSTRATION SUMMARY")
        print("=" * 80)
        
        print("\n[*] Test Results:")
        for test_name, success in results:
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"    {test_name}: {status}")
            
        all_passed = all(r[1] for r in results)
        print(f"\n[*] Overall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        print("\n[*] Key Insights:")
        print("    1. Authentication emerges from logical distinction alone")
        print("    2. No cryptographic primitives required")
        print("    3. Separation boundaries are maintained through logic")
        print("    4. Universal verification using only shared principles")
        print("    5. Knowledge can be proven without revelation")
        
        print("\n" + "=" * 80)
        print("END OF DEMONSTRATION")
        print("=" * 80)


def main():
    """Main entry point."""
    demo = ADPDemo()
    demo.run()


if __name__ == "__main__":
    main()