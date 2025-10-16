#!/usr/bin/env python3
"""
Advanced Quantum Knowledge Distinction Demo
============================================

Demonstrates advanced quantum computing features for knowledge management
including error correction, teleportation, compression, and hybrid systems.
"""

import math
import time
import json
from typing import Dict, Any
from quantum_distinction import (
    QuantumKnowledgeState,
    QuantumAmplitude,
    QuantumBasis,
    QuantumSuperposition,
    QuantumEntanglement,
    QuantumMeasurement,
    QuantumZeroRoom,
    QuantumKnowledgeDistinction
)
from quantum_error_correction import (
    QuantumError,
    QuantumRepetitionCode,
    ShorCode,
    SurfaceCode,
    QuantumKnowledgeProtection
)
from quantum_teleportation import (
    QuantumTeleportation,
    QuantumCompression,
    QuantumSwapping,
    QuantumRepeater
)
from quantum_hybrid import (
    HybridKnowledgeState,
    ProcessingMode,
    QuantumOracleDatabase,
    HybridProcessor,
    QuantumEncryption,
    HybridAuthenticationSystem
)


class AdvancedQuantumDemo:
    """Advanced demonstration of quantum knowledge capabilities."""
    
    def __init__(self):
        """Initialize demo systems."""
        self.results = {}
        
    def run_complete_demo(self):
        """Run complete advanced quantum demonstration."""
        print("=" * 80)
        print("ADVANCED QUANTUM KNOWLEDGE DISTINCTION")
        print("Demonstrating Practical Quantum Computing Applications")
        print("=" * 80)
        print()
        
        print("1. QUANTUM ERROR CORRECTION")
        print("-" * 40)
        self.demonstrate_error_correction()
        print()
        
        print("2. QUANTUM TELEPORTATION")
        print("-" * 40)
        self.demonstrate_teleportation()
        print()
        
        print("3. QUANTUM COMPRESSION")
        print("-" * 40)
        self.demonstrate_compression()
        print()
        
        print("4. QUANTUM DATABASE SEARCH")
        print("-" * 40)
        self.demonstrate_quantum_search()
        print()
        
        print("5. HYBRID QUANTUM-CLASSICAL SYSTEM")
        print("-" * 40)
        self.demonstrate_hybrid_system()
        print()
        
        print("6. QUANTUM ENCRYPTION")
        print("-" * 40)
        self.demonstrate_quantum_encryption()
        print()
        
        print("7. COMPLETE AUTHENTICATION PROTOCOL")
        print("-" * 40)
        self.demonstrate_full_authentication()
        print()
        
        print("8. PERFORMANCE COMPARISON")
        print("-" * 40)
        self.show_performance_comparison()
        
    def demonstrate_error_correction(self):
        """Demonstrate quantum error correction protecting knowledge."""
        print("Creating quantum knowledge state...")
        
        # Create knowledge in superposition
        knowledge = QuantumSuperposition.create_equal_superposition(
            ["secret_data_A", "secret_data_B", "secret_data_C"],
            label="sensitive_knowledge"
        )
        
        print(f"Original state has {len(knowledge.amplitudes)} superposed values")
        
        # Apply protection
        print("\nApplying quantum error correction...")
        protector = QuantumKnowledgeProtection(protection_level='high')
        
        # Simulate storage with errors
        simulation = protector.simulate_storage(
            knowledge,
            storage_time=100,
            noise_model={
                'bit_flip': 0.05,
                'phase_flip': 0.03,
                'amplitude_damping': 0.02
            }
        )
        
        print(f"Protection level: {simulation['protection_level']}")
        print(f"Errors applied: {', '.join(simulation['errors_applied'])}")
        print(f"Fidelity after recovery: {simulation['fidelity']:.4f}")
        print(f"Success: {simulation['success']}")
        
        # Test different codes
        print("\nComparing error correction codes:")
        
        codes = {
            'repetition_3': QuantumRepetitionCode(3),
            'repetition_5': QuantumRepetitionCode(5),
            'shor_9': ShorCode(),
            'surface_3': SurfaceCode(3)
        }
        
        for code_name, code in codes.items():
            # Encode
            if hasattr(code, 'encode_logical'):
                encoded = code.encode_logical(knowledge)
            else:
                encoded = code.encode(knowledge)
            
            encoding_rate = len(knowledge.amplitudes) / len(encoded.amplitudes)
            print(f"  {code_name}: encoding rate = {encoding_rate:.3f}")
        
        self.results['error_correction'] = {
            'fidelity': simulation['fidelity'],
            'codes_tested': list(codes.keys())
        }
    
    def demonstrate_teleportation(self):
        """Demonstrate quantum teleportation of knowledge."""
        print("Setting up quantum teleportation...")
        
        teleporter = QuantumTeleportation()
        
        # Create entangled channel
        channel = teleporter.create_entangled_channel("demo_channel", "Φ+")
        print(f"Entangled channel created: {channel.channel_id}")
        print(f"Entanglement fidelity: {channel.entanglement_fidelity}")
        
        # Create knowledge to teleport
        secret_knowledge = QuantumSuperposition.create_weighted_superposition(
            {"quantum_secret": 0.8, "decoy_data": 0.2},
            label="alice_secret"
        )
        
        print(f"\nTeleporting knowledge: {secret_knowledge.label}")
        
        # Perform teleportation
        result = teleporter.teleport_with_verification(
            secret_knowledge,
            "demo_channel"
        )
        
        print(f"Teleportation success: {result['success']}")
        print(f"Classical bits sent: {result['classical_bits_sent']}")
        print(f"Fidelity: {result['fidelity']:.4f}")
        
        # Demonstrate quantum repeater
        print("\nQuantum repeater for long-distance communication:")
        repeater = QuantumRepeater(num_segments=4)
        segments = repeater.create_repeater_chain()
        
        print(f"Repeater chain with {len(segments)} segments created")
        
        # Extend entanglement
        end_to_end = repeater.extend_entanglement()
        print("End-to-end entanglement established through swapping")
        
        self.results['teleportation'] = {
            'fidelity': result['fidelity'],
            'classical_bits': result['classical_bits_sent'],
            'repeater_segments': len(segments)
        }
    
    def demonstrate_compression(self):
        """Demonstrate quantum compression algorithms."""
        print("Demonstrating quantum compression...")
        
        compressor = QuantumCompression()
        
        # Create knowledge with redundancy
        knowledge = QuantumKnowledgeState(
            label="compressible_knowledge",
            amplitudes={
                "data_000": QuantumAmplitude(0.5),
                "data_001": QuantumAmplitude(0.1),
                "data_010": QuantumAmplitude(0.1),
                "data_011": QuantumAmplitude(0.05),
                "data_100": QuantumAmplitude(0.5),
                "data_101": QuantumAmplitude(0.1),
                "data_110": QuantumAmplitude(0.1),
                "data_111": QuantumAmplitude(0.05)
            }
        )
        knowledge.normalize()
        
        print(f"Original state: {len(knowledge.amplitudes)} terms")
        
        # Compress at different levels
        compression_levels = [0.3, 0.5, 0.7]
        
        for level in compression_levels:
            compressed, metadata = compressor.compress_knowledge(knowledge, level)
            print(f"\nCompression level {level}:")
            print(f"  Compressed terms: {metadata['compressed_terms']}")
            print(f"  Compression ratio: {metadata['compression_ratio']:.2%}")
            print(f"  Truncated probability: {metadata['truncated_probability']:.4f}")
        
        # Demonstrate Schumacher compression
        print("\nSchumacher compression for ensemble:")
        
        ensemble = [knowledge] * 10
        compressed_ensemble, rate = compressor.schumacher_compression(
            ensemble,
            error_tolerance=0.05
        )
        
        print(f"Ensemble compression rate: {rate:.3f}")
        
        self.results['compression'] = {
            'original_terms': len(knowledge.amplitudes),
            'best_compression': min(metadata['compression_ratio'] for level in compression_levels),
            'schumacher_rate': rate
        }
    
    def demonstrate_quantum_search(self):
        """Demonstrate Grover's search in quantum database."""
        print("Initializing quantum database...")
        
        db = QuantumOracleDatabase(database_size=64)
        
        # Populate database
        for i in range(32):
            knowledge = HybridKnowledgeState(
                knowledge_id=f"item_{i}",
                classical_data={"value": i, "type": "even" if i % 2 == 0 else "odd"}
            )
            db.store_knowledge(i, knowledge)
        
        print(f"Database populated with {len(db.database)} items")
        
        # Define search predicate
        def find_special_item(knowledge):
            return (knowledge.classical_data.get("value", 0) == 17)
        
        print("\nSearching for item with value=17...")
        
        start_time = time.time()
        result = db.grover_search(find_special_item)
        quantum_time = time.time() - start_time
        
        if result:
            index, found_item = result
            print(f"Found at index {index}: {found_item.knowledge_id}")
            print(f"Oracle calls: {db.oracle_calls}")
            print(f"Search time: {quantum_time:.4f}s")
        
        # Compare with classical
        classical_steps = 64 / 2  # Average case
        quantum_steps = db.oracle_calls
        speedup = classical_steps / quantum_steps if quantum_steps > 0 else 1
        
        print(f"\nClassical would need ~{classical_steps:.0f} steps")
        print(f"Quantum needed {quantum_steps} steps")
        print(f"Speedup factor: {speedup:.2f}x")
        
        self.results['search'] = {
            'database_size': 64,
            'quantum_steps': quantum_steps,
            'speedup': speedup
        }
    
    def demonstrate_hybrid_system(self):
        """Demonstrate hybrid quantum-classical processing."""
        print("Initializing hybrid processor...")
        
        processor = HybridProcessor()
        
        # Create hybrid knowledge
        hybrid_knowledge = HybridKnowledgeState(
            knowledge_id="hybrid_data",
            classical_data={"user": "alice", "timestamp": time.time()},
            quantum_state=QuantumSuperposition.create_equal_superposition(
                ["quantum_bit_0", "quantum_bit_1"]
            ),
            processing_mode=ProcessingMode.AUTO
        )
        
        print(f"Hybrid knowledge created with complexity: {hybrid_knowledge.get_complexity()}")
        
        # Test different operations
        operations = ['hash', 'search', 'optimize']
        
        for op in operations:
            print(f"\nProcessing operation: {op}")
            result = processor.process_knowledge(hybrid_knowledge, op)
            
            # Check which mode was used
            last_processing = processor.processing_history[-1]
            print(f"  Mode used: {last_processing['mode']}")
            print(f"  Processing time: {last_processing['processing_time']:.4f}s")
        
        # Show performance metrics
        print("\nPerformance metrics:")
        for metric, value in processor.performance_metrics.items():
            if value > 0:
                print(f"  {metric}: {value:.3f}")
        
        self.results['hybrid'] = {
            'operations_tested': operations,
            'modes_available': ['quantum', 'classical', 'hybrid']
        }
    
    def demonstrate_quantum_encryption(self):
        """Demonstrate quantum encryption with one-time pads."""
        print("Quantum encryption demonstration...")
        
        encryption = QuantumEncryption()
        
        # Generate quantum key
        key_id, key_state = encryption.generate_quantum_key(key_length=128)
        print(f"Quantum key generated: {key_id[:8]}...")
        print(f"Key has {len(key_state.amplitudes)} quantum states")
        
        # Create message
        message = HybridKnowledgeState(
            knowledge_id="secret_message",
            classical_data={"content": "Top secret information"},
            quantum_state=QuantumSuperposition.create_hadamard_state(True, "secret_qubit")
        )
        
        print("\nEncrypting message...")
        encrypted = encryption.quantum_one_time_pad(message, key_id)
        
        print(f"Message encrypted: {encrypted.knowledge_id}")
        print(f"Encryption metadata: {encrypted.metadata}")
        
        # Demonstrate perfect secrecy
        print("\nQuantum one-time pad provides perfect secrecy:")
        print("  - Key is truly random (quantum generated)")
        print("  - Key length equals message length")
        print("  - Key used only once (enforced by system)")
        print("  - Result: Information-theoretic security")
        
        self.results['encryption'] = {
            'key_length': 128,
            'security_level': 'information_theoretic',
            'key_reuse_prevented': True
        }
    
    def demonstrate_full_authentication(self):
        """Demonstrate complete hybrid authentication system."""
        print("Complete quantum-classical authentication...")
        
        auth_system = HybridAuthenticationSystem()
        
        # Create identity
        print("\nCreating hybrid identity for Alice...")
        alice_identity = auth_system.create_hybrid_identity(
            entity_id="alice_quantum",
            classical_attributes={
                "name": "Alice",
                "role": "quantum_researcher",
                "clearance": "top_secret"
            },
            quantum_secret="alice_quantum_key_2024"
        )
        
        print(f"Identity created: {alice_identity.knowledge_id}")
        print(f"Has classical component: {alice_identity.is_classical()}")
        print(f"Has quantum component: {alice_identity.is_quantum()}")
        
        # Attempt authentication with quantum proof
        print("\nAuthenticating with quantum proof...")
        quantum_proof = QuantumSuperposition.create_weighted_superposition(
            {"alice_quantum_key_2024": 0.9, "wrong_key": 0.1}
        )
        
        auth_result = auth_system.authenticate("alice_quantum", quantum_proof)
        
        print(f"Authentication result:")
        print(f"  Authenticated: {auth_result['authenticated']}")
        print(f"  Confidence: {auth_result['confidence']:.2%}")
        print(f"  Verification type: {auth_result['verification_type']}")
        print(f"  Grover oracle calls: {auth_result['oracle_calls']}")
        
        # Show advantages
        print("\nHybrid system advantages:")
        advantages = auth_system.demonstrate_hybrid_advantages()
        
        for category, details in advantages.items():
            print(f"\n{category.upper()}:")
            for key, value in details.items():
                print(f"  {key}: {value}")
        
        self.results['authentication'] = {
            'identity_created': True,
            'authentication_success': auth_result['authenticated'],
            'confidence': auth_result['confidence']
        }
    
    def show_performance_comparison(self):
        """Show performance comparison between classical and quantum."""
        print("PERFORMANCE COMPARISON")
        print()
        
        # Database search
        print("Database Search (64 items):")
        print("  Classical: O(N) = 64 operations worst case")
        print("  Quantum: O(√N) ≈ 8 operations")
        print("  Speedup: 8x")
        print()
        
        # Error correction
        print("Error Correction:")
        print("  Classical: Reed-Solomon, LDPC")
        print("  Quantum: Shor code, Surface code")
        print("  Advantage: Protects superposition and entanglement")
        print()
        
        # Encryption
        print("Encryption Security:")
        print("  Classical: Computational security (RSA, AES)")
        print("  Quantum: Information-theoretic security (QKD, OTP)")
        print("  Advantage: Unconditional security")
        print()
        
        # Knowledge capacity
        print("Knowledge Representation:")
        print("  Classical: N bits for N states")
        print("  Quantum: log₂(N) qubits for N superposed states")
        print("  Advantage: Exponential state space")
        print()
        
        # Summary
        print("SUMMARY OF RESULTS:")
        for component, metrics in self.results.items():
            print(f"\n{component.upper()}:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")


def main():
    """Run advanced quantum demonstration."""
    demo = AdvancedQuantumDemo()
    demo.run_complete_demo()


if __name__ == "__main__":
    # Fix imports for standalone execution
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from quantum.quantum_distinction import (
        QuantumKnowledgeState,
        QuantumAmplitude,
        QuantumBasis,
        QuantumSuperposition,
        QuantumEntanglement,
        QuantumMeasurement,
        QuantumZeroRoom,
        QuantumKnowledgeDistinction
    )
    from quantum.quantum_error_correction import (
        QuantumError,
        QuantumRepetitionCode,
        ShorCode,
        SurfaceCode,
        QuantumKnowledgeProtection
    )
    from quantum.quantum_teleportation import (
        QuantumTeleportation,
        QuantumCompression,
        QuantumSwapping,
        QuantumRepeater
    )
    from quantum.quantum_hybrid import (
        HybridKnowledgeState,
        ProcessingMode,
        QuantumOracleDatabase,
        HybridProcessor,
        QuantumEncryption,
        HybridAuthenticationSystem
    )
    
    main()