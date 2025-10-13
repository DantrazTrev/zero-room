"""
Quantum Knowledge Distinction Demo
===================================

Demonstrates the fundamental ways of distinguishing knowledge using
quantum computing principles in the zero room framework.
"""

import math
import time
from typing import Dict, Any, List
from .quantum_distinction import (
    QuantumKnowledgeState,
    QuantumAmplitude,
    QuantumBasis,
    QuantumSuperposition,
    QuantumEntanglement,
    QuantumMeasurement,
    QuantumZeroRoom,
    QuantumKnowledgeDistinction
)
from .quantum_foundations import (
    QuantumFoundations,
    QuantumObserver,
    QuantumBoundary,
    QuantumCollapse,
    QuantumCoherence
)
from .quantum_protocol import (
    QuantumAuthenticationProtocol,
    QuantumCommitment,
    QuantumWitness,
    QuantumVerification
)


class QuantumKnowledgeDemo:
    """Comprehensive demonstration of quantum knowledge distinction."""
    
    def __init__(self):
        """Initialize demo components."""
        self.zero_room = QuantumZeroRoom()
        self.distinction = QuantumKnowledgeDistinction()
        self.protocol = QuantumAuthenticationProtocol()
        self.results = {}
    
    def run_full_demo(self):
        """Run complete demonstration of quantum knowledge distinction."""
        print("=" * 80)
        print("QUANTUM KNOWLEDGE DISTINCTION DEMONSTRATION")
        print("Exploring Fundamental Ways of Distinguishing Knowledge")
        print("Through Quantum Computing Principles")
        print("=" * 80)
        print()
        
        # 1. Demonstrate Superposition
        print("1. QUANTUM SUPERPOSITION OF KNOWLEDGE")
        print("-" * 40)
        self.demonstrate_superposition()
        print()
        
        # 2. Demonstrate Measurement and Collapse
        print("2. MEASUREMENT AND WAVE FUNCTION COLLAPSE")
        print("-" * 40)
        self.demonstrate_measurement()
        print()
        
        # 3. Demonstrate Entanglement
        print("3. QUANTUM ENTANGLEMENT OF KNOWLEDGE")
        print("-" * 40)
        self.demonstrate_entanglement()
        print()
        
        # 4. Demonstrate Zero Room
        print("4. THE QUANTUM ZERO ROOM")
        print("-" * 40)
        self.demonstrate_zero_room()
        print()
        
        # 5. Demonstrate Quantum-Classical Boundary
        print("5. QUANTUM-CLASSICAL BOUNDARY")
        print("-" * 40)
        self.demonstrate_boundary()
        print()
        
        # 6. Demonstrate Quantum Authentication
        print("6. QUANTUM AUTHENTICATION PROTOCOL")
        print("-" * 40)
        self.demonstrate_authentication()
        print()
        
        # 7. Show Fundamental Principles
        print("7. FUNDAMENTAL QUANTUM PRINCIPLES")
        print("-" * 40)
        self.show_fundamental_principles()
        print()
        
        # 8. Summary
        print("8. SUMMARY: QUANTUM DISTINCTION OF KNOWLEDGE")
        print("-" * 40)
        self.show_summary()
    
    def demonstrate_superposition(self):
        """Demonstrate how knowledge can exist in quantum superposition."""
        print("Creating knowledge in superposition...")
        
        # Create superposition of knowing and not knowing
        knowledge = self.distinction.create_knowledge_superposition(
            "The secret password is quantum123",
            uncertainty_level=0.5
        )
        
        print(f"Knowledge state: {knowledge.label}")
        print(f"Number of superposed states: {len(knowledge.amplitudes)}")
        
        for state, amp in knowledge.amplitudes.items():
            prob = amp.probability
            print(f"  State '{state}': probability = {prob:.3f}")
        
        distinctness = self.zero_room.get_knowledge_distinctness(knowledge.label)
        print(f"Distinctness (0=superposed, 1=classical): {distinctness:.3f}")
        
        # Show Hadamard transformation
        print("\nApplying Hadamard transformation...")
        hadamard = QuantumSuperposition.create_hadamard_state(False, "hadamard_demo")
        print(f"Hadamard state creates equal superposition:")
        for state, amp in hadamard.amplitudes.items():
            print(f"  |{state}⟩: amplitude = {amp.real:.3f}")
        
        self.results['superposition'] = {
            'states_created': 2,
            'max_superposition': len(hadamard.amplitudes),
            'distinctness': distinctness
        }
    
    def demonstrate_measurement(self):
        """Demonstrate measurement causing wave function collapse."""
        print("Creating superposed knowledge state...")
        
        # Create uncertain knowledge
        uncertain_knowledge = QuantumSuperposition.create_equal_superposition(
            ["fact_A", "fact_B", "fact_C"],
            label="uncertain_facts"
        )
        
        print(f"Before measurement - state is in superposition:")
        for state, amp in uncertain_knowledge.amplitudes.items():
            print(f"  {state}: probability = {amp.probability:.3f}")
        
        # Calculate entropy before measurement
        entropy_before = self._calculate_entropy(uncertain_knowledge)
        print(f"Entropy before measurement: {entropy_before:.3f}")
        
        # Perform measurement
        print("\nPerforming measurement...")
        outcome, collapsed = QuantumMeasurement.measure(uncertain_knowledge)
        
        print(f"Measurement outcome: {outcome}")
        print(f"After measurement - state has collapsed:")
        for state, amp in collapsed.amplitudes.items():
            print(f"  {state}: probability = {amp.probability:.3f}")
        
        entropy_after = self._calculate_entropy(collapsed)
        print(f"Entropy after measurement: {entropy_after:.3f}")
        print(f"Information gained: {entropy_before - entropy_after:.3f} bits")
        
        # Demonstrate weak measurement
        print("\nDemonstrating weak measurement...")
        weak_state = QuantumSuperposition.create_equal_superposition(
            ["0", "1"],
            label="weak_demo"
        )
        
        expectation, weakly_collapsed = QuantumMeasurement.weak_measurement(
            weak_state,
            strength=0.1
        )
        
        print(f"Weak measurement expectation value: {expectation:.3f}")
        print("State after weak measurement (partially collapsed):")
        for state, amp in weakly_collapsed.amplitudes.items():
            print(f"  {state}: probability = {amp.probability:.3f}")
        
        self.results['measurement'] = {
            'projective_collapse': outcome,
            'entropy_reduction': entropy_before - entropy_after,
            'weak_measurement_strength': 0.1
        }
    
    def demonstrate_entanglement(self):
        """Demonstrate quantum entanglement of knowledge."""
        print("Creating entangled knowledge states...")
        
        # Create Bell states
        bell1, bell2 = QuantumEntanglement.create_bell_state("Φ+")
        
        print("Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2 created")
        print("This represents perfect correlation between two pieces of knowledge")
        print("\nAmplitudes of entangled state:")
        for state, amp in bell1.amplitudes.items():
            print(f"  |{state}⟩: probability = {amp.probability:.3f}")
        
        print(f"\nEntangled with: {bell1.entangled_with}")
        print(f"Is maximally entangled: {bell1.is_maximally_entangled()}")
        
        # Create GHZ state for multi-party entanglement
        print("\nCreating GHZ state for 3-party entanglement...")
        ghz = QuantumEntanglement.create_ghz_state(3)
        
        print("GHZ state |GHZ⟩ = (|000⟩ + |111⟩)/√2")
        print("All three knowledge items are perfectly correlated")
        for state, amp in ghz.amplitudes.items():
            print(f"  |{state}⟩: probability = {amp.probability:.3f}")
        
        # Demonstrate entanglement of specific knowledge
        print("\nEntangling two specific knowledge items...")
        knowledge1 = self.distinction.create_knowledge_superposition("secret1", 0.3)
        knowledge2 = self.distinction.create_knowledge_superposition("secret2", 0.3)
        
        entangled = QuantumEntanglement.entangle_knowledge(
            knowledge1,
            knowledge2,
            correlation_type="positive"
        )
        
        print(f"Entangled state created with {len(entangled.amplitudes)} basis states")
        print(f"Correlation type: positive (same values are correlated)")
        
        self.results['entanglement'] = {
            'bell_state_created': True,
            'ghz_parties': 3,
            'max_entanglement': bell1.is_maximally_entangled()
        }
    
    def demonstrate_zero_room(self):
        """Demonstrate the Quantum Zero Room concept."""
        print("Initializing the Quantum Zero Room...")
        print("A space where knowledge exists in quantum superposition")
        print()
        
        # Add various knowledge to zero room
        self.zero_room.add_quantum_knowledge(
            "secret_password",
            "my_quantum_secret_2024"
        )
        
        self.zero_room.add_quantum_knowledge(
            "uncertain_fact",
            QuantumSuperposition.create_equal_superposition(
                ["hypothesis_A", "hypothesis_B", "hypothesis_C"]
            )
        )
        
        # Create entangled knowledge
        print("Creating entangled knowledge in zero room...")
        self.zero_room.add_quantum_knowledge(
            "correlated_fact1",
            QuantumSuperposition.create_hadamard_state(True)
        )
        self.zero_room.add_quantum_knowledge(
            "correlated_fact2",
            QuantumSuperposition.create_hadamard_state(False)
        )
        
        self.zero_room.entangle_knowledge_items(
            "correlated_fact1",
            "correlated_fact2",
            correlation_type="negative"
        )
        
        # Check distinctness levels
        print("\nKnowledge distinctness in zero room:")
        for knowledge_id in ["secret_password", "uncertain_fact", "correlated_fact1"]:
            if knowledge_id in self.zero_room.knowledge_states:
                distinctness = self.zero_room.get_knowledge_distinctness(knowledge_id)
                print(f"  {knowledge_id}: {distinctness:.3f}")
        
        # Demonstrate observation
        print("\nObserving uncertain_fact (causes collapse)...")
        result, collapsed = self.zero_room.observe_knowledge("uncertain_fact")
        print(f"Observation result: {result}")
        print(f"Knowledge is now classical (distinctness = 1.0)")
        
        # Show entanglement strength
        entanglement_strength = self.zero_room.get_entanglement_strength(
            "correlated_fact1",
            "correlated_fact2"
        )
        print(f"\nEntanglement strength between correlated facts: {entanglement_strength:.3f}")
        
        # Apply quantum gate
        print("\nApplying phase gate to secret_password...")
        transformed = self.zero_room.apply_quantum_gate(
            "secret_password",
            "phase",
            {"phase": math.pi/4}
        )
        print(f"Phase transformation applied successfully")
        
        self.results['zero_room'] = {
            'knowledge_items': len(self.zero_room.knowledge_states),
            'entangled_pairs': len(self.zero_room.entanglement_graph),
            'measurements': len(self.zero_room.measurement_history)
        }
    
    def demonstrate_boundary(self):
        """Demonstrate the quantum-classical boundary."""
        print("Creating quantum-classical boundary...")
        
        boundary = QuantumBoundary(decoherence_rate=0.1)
        observer = QuantumObserver("boundary_observer", {QuantumBasis.COMPUTATIONAL})
        
        # Add quantum knowledge
        quantum_state = QuantumSuperposition.create_equal_superposition(
            ["quantum_info_1", "quantum_info_2"],
            label="boundary_test"
        )
        
        boundary.add_quantum_knowledge("test_knowledge", quantum_state)
        
        print(f"Quantum side: {len(boundary.quantum_side)} items")
        print(f"Classical side: {len(boundary.classical_side)} items")
        print(f"Boundary width: {boundary.get_boundary_width():.3f}")
        
        # Measure across boundary
        print("\nMeasuring knowledge across boundary...")
        classical_result = boundary.measure_across_boundary("test_knowledge", observer)
        
        print(f"Measurement result: {classical_result}")
        print(f"Knowledge has crossed to classical side")
        print(f"Quantum side: {len(boundary.quantum_side)} items")
        print(f"Classical side: {len(boundary.classical_side)} items")
        
        # Demonstrate decoherence
        print("\nDemonstrating environmental decoherence...")
        
        # Add new quantum state
        decoherence_test = QuantumSuperposition.create_hadamard_state(True)
        boundary.add_quantum_knowledge("decoherence_test", decoherence_test)
        
        print("Applying decoherence over time...")
        boundary.apply_decoherence(time_elapsed=10.0)
        
        if "decoherence_test" in boundary.classical_side:
            print("State has decohered and become classical")
        else:
            print("State maintains some quantum coherence")
        
        # Create boundary proof
        print("\nCreating boundary proof...")
        boundary.add_quantum_knowledge(
            "proof_test",
            QuantumSuperposition.create_equal_superposition(["A", "B"])
        )
        
        proof = boundary.create_boundary_proof("proof_test", "challenge123")
        print(f"Boundary proof created:")
        print(f"  Expectation value: {proof.get('expectation_value', 0):.3f}")
        print(f"  Coherence remaining: {proof.get('coherence_remaining', 0):.3f}")
        print(f"  Proof hash: {proof.get('proof_hash', 'N/A')}")
        
        self.results['boundary'] = {
            'decoherence_rate': 0.1,
            'boundary_width': boundary.get_boundary_width(),
            'items_measured': len(boundary.classical_side)
        }
    
    def demonstrate_authentication(self):
        """Demonstrate quantum authentication protocol."""
        print("Demonstrating Quantum Authentication Protocol...")
        print()
        
        # Initialize identities
        print("1. Initializing quantum identities...")
        alice_identity = self.protocol.initialize_quantum_identity(
            "alice",
            "alice_secret_key_2024"
        )
        bob_identity = self.protocol.initialize_quantum_identity(
            "bob",
            "bob_secret_key_2024"
        )
        
        print(f"Alice's quantum identity initialized:")
        print(f"  Public reference: {alice_identity['public_reference']}")
        print(f"  Entanglement: {alice_identity['quantum_properties']['entanglement']:.3f}")
        print(f"  Superposition: {alice_identity['quantum_properties']['superposition']:.3f}")
        
        # Create challenge
        print("\n2. Creating quantum challenge...")
        session_id = "demo_session_001"
        challenge = self.protocol.create_quantum_challenge(
            session_id,
            "alice",
            "bob"
        )
        
        print(f"Challenge created:")
        print(f"  Session ID: {challenge['session_id']}")
        print(f"  Challenge hash: {challenge['challenge_hash']}")
        print(f"  Expires: {challenge['expires']}")
        
        # Bob responds
        print("\n3. Bob responding to challenge...")
        response = self.protocol.respond_to_challenge(
            session_id,
            "bob",
            "bob_secret_key_2024"
        )
        
        print(f"Response created:")
        print(f"  Commitment proof: {response['commitment_proof'][:16]}...")
        print(f"  Measurement basis: {response['measurement_basis']}")
        print(f"  Response hash: {response['response_hash']}")
        
        # Alice verifies
        print("\n4. Alice verifying response...")
        # For demo, we use a simplified hash
        expected_hash = "simplified_for_demo"
        verification = self.protocol.verify_response(
            session_id,
            "alice",
            expected_hash
        )
        
        print(f"Verification result:")
        print(f"  Authenticated: {verification['authenticated']}")
        print(f"  Confidence: {verification['confidence']:.2f}")
        print(f"  Session status: {self.protocol.active_sessions[session_id]['status']}")
        
        # Demonstrate quantum advantages
        print("\n5. Quantum Authentication Advantages:")
        advantages = self.protocol.demonstrate_quantum_advantage()
        
        for advantage_type, details in advantages['quantum_advantages'].items():
            print(f"\n  {advantage_type.upper()}:")
            print(f"    Principle: {details['principle']}")
            print(f"    Advantage: {details['advantage']}")
        
        self.results['authentication'] = {
            'protocol': 'quantum',
            'session_created': True,
            'authenticated': verification['authenticated'],
            'quantum_advantages': len(advantages['quantum_advantages'])
        }
    
    def show_fundamental_principles(self):
        """Display fundamental quantum principles for knowledge distinction."""
        print("FUNDAMENTAL QUANTUM AXIOMS")
        print()
        
        axioms = QuantumFoundations.get_all_axioms()
        
        for i, axiom in enumerate(axioms, 1):
            print(f"{i}. {axiom.name}")
            print(f"   Principle: {axiom.principle}")
            print(f"   Mathematical form: {axiom.mathematical_form}")
            print(f"   Key implications:")
            for implication in axiom.implications[:2]:
                print(f"     - {implication}")
            print()
        
        # Show how axioms combine
        print("DERIVED THEOREMS:")
        theorem1 = QuantumFoundations.derive_theorem([
            QuantumFoundations.SUPERPOSITION_AXIOM,
            QuantumFoundations.MEASUREMENT_AXIOM
        ])
        print(f"  • {theorem1}")
        
        theorem2 = QuantumFoundations.derive_theorem([
            QuantumFoundations.ENTANGLEMENT_AXIOM,
            QuantumFoundations.NO_CLONING_AXIOM
        ])
        print(f"  • {theorem2}")
        
        self.results['principles'] = {
            'axioms': len(axioms),
            'derived_theorems': 2
        }
    
    def show_summary(self):
        """Show summary of quantum knowledge distinction."""
        print("QUANTUM KNOWLEDGE DISTINCTION - KEY INSIGHTS")
        print()
        
        print("1. FUNDAMENTAL DISTINCTION:")
        print("   Knowledge is not binary (known/unknown) but exists on a quantum spectrum")
        print("   The act of observation creates the distinction")
        print()
        
        print("2. KEY QUANTUM PROPERTIES FOR KNOWLEDGE:")
        print("   • Superposition: Knowledge can be in multiple states simultaneously")
        print("   • Entanglement: Knowledge items can be fundamentally correlated")
        print("   • Measurement: Observation collapses quantum to classical")
        print("   • No-cloning: Unknown quantum knowledge cannot be copied")
        print("   • Uncertainty: Complementary properties cannot be simultaneously known")
        print()
        
        print("3. THE ZERO ROOM CONCEPT:")
        print("   A quantum space where knowledge exists in superposition")
        print("   Observation causes irreversible transition to classical knowledge")
        print("   Entanglement creates non-local correlations between knowledge items")
        print()
        
        print("4. PRACTICAL APPLICATIONS:")
        print("   • Quantum authentication with unconditional security")
        print("   • Knowledge verification without revelation")
        print("   • Detection of eavesdropping through measurement disturbance")
        print("   • Parallel processing of authentication paths")
        print()
        
        print("5. DEMONSTRATION RESULTS:")
        for component, metrics in self.results.items():
            print(f"   {component.upper()}:")
            for key, value in metrics.items():
                print(f"     - {key}: {value}")
        print()
        
        print("CONCLUSION:")
        print("Quantum computing provides a fundamentally different way of distinguishing")
        print("knowledge. The quantum properties of superposition, entanglement, and")
        print("measurement create new possibilities for secure authentication and")
        print("knowledge management that are impossible with classical systems.")
    
    def _calculate_entropy(self, state: QuantumKnowledgeState) -> float:
        """Calculate von Neumann entropy of quantum state."""
        entropy = 0
        for amp in state.amplitudes.values():
            p = amp.probability
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy


def main():
    """Run the quantum knowledge distinction demonstration."""
    demo = QuantumKnowledgeDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main()