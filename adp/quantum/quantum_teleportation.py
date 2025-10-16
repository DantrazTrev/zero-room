"""
Quantum Knowledge Teleportation and Compression
================================================

Implements quantum teleportation protocols for transferring knowledge states
and quantum compression algorithms for efficient storage.
"""

from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
import math
import hashlib
import time
import random
from .quantum_distinction import (
    QuantumKnowledgeState,
    QuantumAmplitude,
    QuantumBasis,
    QuantumSuperposition,
    QuantumEntanglement,
    QuantumMeasurement
)


@dataclass
class TeleportationChannel:
    """Represents a quantum teleportation channel using entangled pairs."""
    channel_id: str
    alice_qubit: QuantumKnowledgeState
    bob_qubit: QuantumKnowledgeState
    entanglement_fidelity: float = 1.0
    created_time: float = field(default_factory=time.time)
    
    def is_valid(self) -> bool:
        """Check if channel is still valid for teleportation."""
        # Check entanglement is maintained
        return (self.alice_qubit.is_maximally_entangled() and 
                self.entanglement_fidelity > 0.5)


class QuantumTeleportation:
    """
    Implements quantum teleportation protocol for knowledge states.
    
    Allows transfer of quantum knowledge without physical transmission
    of the quantum state itself.
    """
    
    def __init__(self):
        """Initialize teleportation system."""
        self.channels: Dict[str, TeleportationChannel] = {}
        self.teleportation_history: List[Dict[str, Any]] = []
        self.classical_channel: List[Tuple[int, int]] = []
    
    def create_entangled_channel(
        self,
        channel_id: str,
        bell_type: str = "Φ+"
    ) -> TeleportationChannel:
        """
        Create entangled channel for teleportation.
        
        Args:
            channel_id: Unique identifier for channel
            bell_type: Type of Bell state to use
        
        Returns:
            Teleportation channel with entangled pair
        """
        # Create Bell pair
        bell1, bell2 = QuantumEntanglement.create_bell_state(bell_type)
        
        # Create channel
        channel = TeleportationChannel(
            channel_id=channel_id,
            alice_qubit=bell1,
            bob_qubit=bell2,
            entanglement_fidelity=1.0
        )
        
        self.channels[channel_id] = channel
        
        return channel
    
    def teleport_knowledge(
        self,
        knowledge_state: QuantumKnowledgeState,
        channel_id: str
    ) -> Tuple[QuantumKnowledgeState, List[int]]:
        """
        Teleport quantum knowledge state through entangled channel.
        
        Protocol:
        1. Alice has knowledge state to send
        2. Alice and Bob share entangled pair
        3. Alice performs Bell measurement on her state and her half of pair
        4. Alice sends classical measurement results to Bob
        5. Bob applies corrections based on measurement results
        
        Returns:
            Teleported state at Bob's location and classical bits sent
        """
        if channel_id not in self.channels:
            raise ValueError(f"Channel {channel_id} not found")
        
        channel = self.channels[channel_id]
        if not channel.is_valid():
            raise ValueError("Channel is not valid for teleportation")
        
        # Step 1: Alice performs Bell measurement on knowledge + her entangled qubit
        bell_measurement = self._bell_measurement(knowledge_state, channel.alice_qubit)
        
        # Step 2: Extract classical bits from measurement
        classical_bits = self._extract_classical_bits(bell_measurement)
        self.classical_channel.append((classical_bits[0], classical_bits[1]))
        
        # Step 3: Bob applies corrections based on classical bits
        teleported_state = self._apply_teleportation_corrections(
            channel.bob_qubit,
            classical_bits
        )
        
        # Record teleportation
        self.teleportation_history.append({
            'timestamp': time.time(),
            'original_state': knowledge_state.label,
            'channel_id': channel_id,
            'classical_bits': classical_bits,
            'success': True
        })
        
        # Channel is consumed after use
        del self.channels[channel_id]
        
        return teleported_state, classical_bits
    
    def _bell_measurement(
        self,
        state1: QuantumKnowledgeState,
        state2: QuantumKnowledgeState
    ) -> Tuple[int, int]:
        """
        Perform Bell measurement on two qubits.
        
        Returns measurement result as two classical bits.
        """
        # Create combined state
        combined = state1.tensor_product(state2)
        
        # Project onto Bell basis
        bell_basis = self._create_bell_basis()
        
        # Measure in Bell basis (simplified)
        measurement = random.randint(0, 3)
        
        return measurement // 2, measurement % 2
    
    def _create_bell_basis(self) -> List[QuantumKnowledgeState]:
        """Create the four Bell states for measurement basis."""
        # |Φ+⟩ = (|00⟩ + |11⟩)/√2
        phi_plus = QuantumKnowledgeState(
            label="Φ+",
            amplitudes={
                "00": QuantumAmplitude(1/math.sqrt(2)),
                "11": QuantumAmplitude(1/math.sqrt(2))
            }
        )
        
        # |Φ-⟩ = (|00⟩ - |11⟩)/√2
        phi_minus = QuantumKnowledgeState(
            label="Φ-",
            amplitudes={
                "00": QuantumAmplitude(1/math.sqrt(2)),
                "11": QuantumAmplitude(-1/math.sqrt(2))
            }
        )
        
        # |Ψ+⟩ = (|01⟩ + |10⟩)/√2
        psi_plus = QuantumKnowledgeState(
            label="Ψ+",
            amplitudes={
                "01": QuantumAmplitude(1/math.sqrt(2)),
                "10": QuantumAmplitude(1/math.sqrt(2))
            }
        )
        
        # |Ψ-⟩ = (|01⟩ - |10⟩)/√2
        psi_minus = QuantumKnowledgeState(
            label="Ψ-",
            amplitudes={
                "01": QuantumAmplitude(1/math.sqrt(2)),
                "10": QuantumAmplitude(-1/math.sqrt(2))
            }
        )
        
        return [phi_plus, phi_minus, psi_plus, psi_minus]
    
    def _extract_classical_bits(self, measurement: Tuple[int, int]) -> List[int]:
        """Extract classical bits from Bell measurement."""
        return list(measurement)
    
    def _apply_teleportation_corrections(
        self,
        bob_state: QuantumKnowledgeState,
        classical_bits: List[int]
    ) -> QuantumKnowledgeState:
        """
        Apply Pauli corrections based on classical bits.
        
        00: I (identity)
        01: X (bit flip)
        10: Z (phase flip)
        11: XZ (both)
        """
        corrected_amplitudes = {}
        
        for basis_state, amp in bob_state.amplitudes.items():
            new_state = basis_state
            new_amp = amp
            
            # Apply X gate if first bit is 1
            if classical_bits[0] == 1:
                new_state = ''.join('1' if bit == '0' else '0' 
                                   for bit in basis_state)
            
            # Apply Z gate if second bit is 1
            if classical_bits[1] == 1 and '1' in new_state:
                new_amp = QuantumAmplitude(-amp.real, -amp.imaginary)
            
            corrected_amplitudes[new_state] = new_amp
        
        return QuantumKnowledgeState(
            label=f"teleported_{bob_state.label}",
            amplitudes=corrected_amplitudes,
            basis=bob_state.basis
        )
    
    def calculate_teleportation_fidelity(
        self,
        original: QuantumKnowledgeState,
        teleported: QuantumKnowledgeState
    ) -> float:
        """Calculate fidelity of teleportation."""
        fidelity = 0.0
        
        for basis_state in set(original.amplitudes.keys()) | set(teleported.amplitudes.keys()):
            orig_amp = original.amplitudes.get(basis_state, QuantumAmplitude(0))
            tele_amp = teleported.amplitudes.get(basis_state, QuantumAmplitude(0))
            
            overlap = (orig_amp.conjugate() * tele_amp).real
            fidelity += overlap
        
        return abs(fidelity) ** 2
    
    def teleport_with_verification(
        self,
        knowledge_state: QuantumKnowledgeState,
        channel_id: str,
        verify_fidelity_threshold: float = 0.95
    ) -> Dict[str, Any]:
        """
        Teleport with verification of success.
        
        Returns detailed results including fidelity check.
        """
        # Perform teleportation
        teleported, classical_bits = self.teleport_knowledge(knowledge_state, channel_id)
        
        # Calculate fidelity (in practice, would need tomography)
        fidelity = self.calculate_teleportation_fidelity(knowledge_state, teleported)
        
        success = fidelity >= verify_fidelity_threshold
        
        return {
            'success': success,
            'original_state': knowledge_state.label,
            'teleported_state': teleported,
            'classical_bits_sent': classical_bits,
            'fidelity': fidelity,
            'channel_id': channel_id,
            'timestamp': time.time()
        }


class QuantumCompression:
    """
    Implements quantum compression algorithms for knowledge states.
    
    Compresses quantum information using Schmidt decomposition and
    other quantum information theoretic techniques.
    """
    
    def __init__(self):
        """Initialize compression system."""
        self.compression_history: List[Dict[str, Any]] = []
        self.compression_codebook: Dict[str, Dict[str, Any]] = {}
    
    def schmidt_decomposition(
        self,
        entangled_state: QuantumKnowledgeState
    ) -> Tuple[List[float], List[QuantumKnowledgeState], List[QuantumKnowledgeState]]:
        """
        Perform Schmidt decomposition of entangled state.
        
        |ψ⟩ = Σᵢ λᵢ |uᵢ⟩ ⊗ |vᵢ⟩
        
        Returns:
            Schmidt coefficients and basis states
        """
        # Simplified Schmidt decomposition
        schmidt_coefficients = []
        alice_basis = []
        bob_basis = []
        
        # Extract coefficients from amplitudes
        for basis_state, amp in entangled_state.amplitudes.items():
            coefficient = math.sqrt(amp.probability)
            schmidt_coefficients.append(coefficient)
            
            # Split basis state (assuming tensor product structure)
            mid = len(basis_state) // 2
            alice_state = QuantumKnowledgeState(
                label=f"alice_{basis_state[:mid]}",
                amplitudes={basis_state[:mid]: QuantumAmplitude(1.0)}
            )
            bob_state = QuantumKnowledgeState(
                label=f"bob_{basis_state[mid:]}",
                amplitudes={basis_state[mid:]: QuantumAmplitude(1.0)}
            )
            
            alice_basis.append(alice_state)
            bob_basis.append(bob_state)
        
        return schmidt_coefficients, alice_basis, bob_basis
    
    def compress_knowledge(
        self,
        knowledge_state: QuantumKnowledgeState,
        compression_level: float = 0.5
    ) -> Tuple[QuantumKnowledgeState, Dict[str, Any]]:
        """
        Compress quantum knowledge state.
        
        Args:
            knowledge_state: State to compress
            compression_level: 0 (no compression) to 1 (maximum compression)
        
        Returns:
            Compressed state and compression metadata
        """
        # Calculate von Neumann entropy (incompressible information)
        entropy = self._calculate_entropy(knowledge_state)
        
        # Determine number of terms to keep
        num_terms = len(knowledge_state.amplitudes)
        keep_terms = max(1, int(num_terms * (1 - compression_level)))
        
        # Sort amplitudes by probability
        sorted_amps = sorted(
            knowledge_state.amplitudes.items(),
            key=lambda x: x[1].probability,
            reverse=True
        )
        
        # Keep only most significant terms
        compressed_amplitudes = {}
        truncated_probability = 0
        
        for i, (basis_state, amp) in enumerate(sorted_amps):
            if i < keep_terms:
                compressed_amplitudes[basis_state] = amp
            else:
                truncated_probability += amp.probability
        
        # Create compressed state
        compressed = QuantumKnowledgeState(
            label=f"{knowledge_state.label}_compressed",
            amplitudes=compressed_amplitudes,
            basis=knowledge_state.basis,
            entangled_with=knowledge_state.entangled_with
        )
        compressed.normalize()
        
        # Calculate compression ratio
        original_size = num_terms * 2  # Real and imaginary parts
        compressed_size = keep_terms * 2
        compression_ratio = 1 - (compressed_size / original_size)
        
        # Create compression metadata
        metadata = {
            'original_terms': num_terms,
            'compressed_terms': keep_terms,
            'compression_ratio': compression_ratio,
            'truncated_probability': truncated_probability,
            'original_entropy': entropy,
            'compression_level': compression_level
        }
        
        # Store in codebook for decompression
        self.compression_codebook[compressed.label] = metadata
        
        # Record compression
        self.compression_history.append({
            'timestamp': time.time(),
            'original_state': knowledge_state.label,
            'compressed_state': compressed.label,
            'metadata': metadata
        })
        
        return compressed, metadata
    
    def decompress_knowledge(
        self,
        compressed_state: QuantumKnowledgeState,
        use_interpolation: bool = True
    ) -> QuantumKnowledgeState:
        """
        Decompress quantum knowledge state.
        
        Args:
            compressed_state: Compressed state
            use_interpolation: Whether to interpolate missing amplitudes
        
        Returns:
            Decompressed state (approximate)
        """
        # Get compression metadata
        metadata = self.compression_codebook.get(compressed_state.label, {})
        
        decompressed_amplitudes = compressed_state.amplitudes.copy()
        
        if use_interpolation and metadata:
            # Interpolate missing basis states
            original_terms = metadata.get('original_terms', len(compressed_state.amplitudes))
            truncated_prob = metadata.get('truncated_probability', 0)
            
            if truncated_prob > 0:
                # Distribute truncated probability among new random states
                num_missing = original_terms - len(compressed_state.amplitudes)
                if num_missing > 0:
                    prob_per_state = truncated_prob / num_missing
                    amp_per_state = math.sqrt(prob_per_state)
                    
                    # Add interpolated states
                    for i in range(num_missing):
                        # Generate new basis state
                        new_state = f"interpolated_{i}"
                        decompressed_amplitudes[new_state] = QuantumAmplitude(amp_per_state)
        
        decompressed = QuantumKnowledgeState(
            label=f"{compressed_state.label}_decompressed",
            amplitudes=decompressed_amplitudes,
            basis=compressed_state.basis,
            entangled_with=compressed_state.entangled_with
        )
        decompressed.normalize()
        
        return decompressed
    
    def _calculate_entropy(self, state: QuantumKnowledgeState) -> float:
        """Calculate von Neumann entropy."""
        entropy = 0
        for amp in state.amplitudes.values():
            p = amp.probability
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    def schumacher_compression(
        self,
        knowledge_states: List[QuantumKnowledgeState],
        error_tolerance: float = 0.01
    ) -> Tuple[List[QuantumKnowledgeState], float]:
        """
        Implement Schumacher compression for ensemble of states.
        
        Quantum analog of Shannon's source coding theorem.
        
        Args:
            knowledge_states: Ensemble of quantum states
            error_tolerance: Acceptable error rate
        
        Returns:
            Compressed ensemble and achieved compression rate
        """
        # Calculate typical subspace
        typical_subspace = self._find_typical_subspace(knowledge_states, error_tolerance)
        
        compressed_states = []
        total_original_dims = 0
        total_compressed_dims = 0
        
        for state in knowledge_states:
            # Project onto typical subspace
            projected_amplitudes = {}
            for basis_state, amp in state.amplitudes.items():
                if basis_state in typical_subspace:
                    projected_amplitudes[basis_state] = amp
            
            if projected_amplitudes:
                compressed = QuantumKnowledgeState(
                    label=f"{state.label}_schumacher",
                    amplitudes=projected_amplitudes,
                    basis=state.basis
                )
                compressed.normalize()
                compressed_states.append(compressed)
                
                total_original_dims += len(state.amplitudes)
                total_compressed_dims += len(compressed.amplitudes)
            else:
                compressed_states.append(state)
                total_original_dims += len(state.amplitudes)
                total_compressed_dims += len(state.amplitudes)
        
        compression_rate = total_compressed_dims / total_original_dims if total_original_dims > 0 else 1.0
        
        return compressed_states, compression_rate
    
    def _find_typical_subspace(
        self,
        states: List[QuantumKnowledgeState],
        error_tolerance: float
    ) -> Set[str]:
        """Find typical subspace for Schumacher compression."""
        # Count frequency of basis states
        frequency = {}
        total_states = len(states)
        
        for state in states:
            for basis_state, amp in state.amplitudes.items():
                if basis_state not in frequency:
                    frequency[basis_state] = 0
                frequency[basis_state] += amp.probability
        
        # Normalize frequencies
        for basis_state in frequency:
            frequency[basis_state] /= total_states
        
        # Sort by frequency
        sorted_states = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Find typical subspace (states that cover 1-error_tolerance probability)
        typical_subspace = set()
        cumulative_prob = 0
        
        for basis_state, prob in sorted_states:
            typical_subspace.add(basis_state)
            cumulative_prob += prob
            if cumulative_prob >= 1 - error_tolerance:
                break
        
        return typical_subspace


class QuantumSwapping:
    """
    Implements entanglement swapping for extending quantum communication range.
    
    Allows creation of entanglement between particles that never interacted.
    """
    
    def __init__(self):
        """Initialize swapping system."""
        self.swapping_history: List[Dict[str, Any]] = []
    
    def entanglement_swapping(
        self,
        pair1: Tuple[QuantumKnowledgeState, QuantumKnowledgeState],
        pair2: Tuple[QuantumKnowledgeState, QuantumKnowledgeState]
    ) -> Tuple[QuantumKnowledgeState, QuantumKnowledgeState]:
        """
        Perform entanglement swapping.
        
        Given: A-B entangled, C-D entangled
        Result: A-D entangled (B and C measured)
        
        Args:
            pair1: First entangled pair (A, B)
            pair2: Second entangled pair (C, D)
        
        Returns:
            New entangled pair (A, D)
        """
        # Extract individual states
        alice_state, bob_state = pair1
        charlie_state, diana_state = pair2
        
        # Perform Bell measurement on Bob and Charlie
        measurement = self._bell_measurement_swapping(bob_state, charlie_state)
        
        # Apply corrections to create A-D entanglement
        corrected_alice = self._apply_swapping_correction(alice_state, measurement, 'alice')
        corrected_diana = self._apply_swapping_correction(diana_state, measurement, 'diana')
        
        # Create new entangled pair
        new_entangled = QuantumEntanglement.entangle_knowledge(
            corrected_alice,
            corrected_diana,
            correlation_type="positive"
        )
        
        # Record swapping
        self.swapping_history.append({
            'timestamp': time.time(),
            'measurement_result': measurement,
            'new_entanglement': f"{corrected_alice.label}-{corrected_diana.label}"
        })
        
        return corrected_alice, corrected_diana
    
    def _bell_measurement_swapping(
        self,
        state1: QuantumKnowledgeState,
        state2: QuantumKnowledgeState
    ) -> int:
        """Perform Bell measurement for swapping."""
        # Simplified - returns Bell state index (0-3)
        return random.randint(0, 3)
    
    def _apply_swapping_correction(
        self,
        state: QuantumKnowledgeState,
        measurement: int,
        party: str
    ) -> QuantumKnowledgeState:
        """Apply corrections based on Bell measurement for swapping."""
        # Apply appropriate Pauli correction based on measurement
        corrections = {
            0: (False, False),  # I
            1: (True, False),   # X
            2: (False, True),   # Z
            3: (True, True)     # XZ
        }
        
        apply_x, apply_z = corrections[measurement]
        corrected_amplitudes = {}
        
        for basis_state, amp in state.amplitudes.items():
            new_state = basis_state
            new_amp = amp
            
            if apply_x:
                new_state = ''.join('1' if bit == '0' else '0' for bit in basis_state)
            
            if apply_z and '1' in new_state:
                new_amp = QuantumAmplitude(-amp.real, -amp.imaginary)
            
            corrected_amplitudes[new_state] = new_amp
        
        return QuantumKnowledgeState(
            label=f"{state.label}_swapped_{party}",
            amplitudes=corrected_amplitudes,
            basis=state.basis
        )


class QuantumRepeater:
    """
    Implements quantum repeater for long-distance quantum communication.
    
    Uses entanglement swapping and purification to extend range.
    """
    
    def __init__(self, num_segments: int = 3):
        """
        Initialize quantum repeater.
        
        Args:
            num_segments: Number of segments in repeater chain
        """
        self.num_segments = num_segments
        self.swapping_protocol = QuantumSwapping()
        self.segments: List[TeleportationChannel] = []
    
    def create_repeater_chain(self) -> List[TeleportationChannel]:
        """Create chain of entangled pairs for repeater."""
        self.segments = []
        
        for i in range(self.num_segments):
            # Create entangled pair for each segment
            bell1, bell2 = QuantumEntanglement.create_bell_state("Φ+")
            
            channel = TeleportationChannel(
                channel_id=f"segment_{i}",
                alice_qubit=bell1,
                bob_qubit=bell2,
                entanglement_fidelity=0.95 - i * 0.05  # Decreasing fidelity
            )
            
            self.segments.append(channel)
        
        return self.segments
    
    def extend_entanglement(self) -> Tuple[QuantumKnowledgeState, QuantumKnowledgeState]:
        """
        Extend entanglement across entire repeater chain.
        
        Returns:
            End-to-end entangled pair
        """
        if len(self.segments) < 2:
            raise ValueError("Need at least 2 segments for repeater")
        
        # Start with first segment
        current_left = self.segments[0].alice_qubit
        current_right = self.segments[0].bob_qubit
        
        # Perform swapping through chain
        for i in range(1, len(self.segments)):
            next_segment = self.segments[i]
            
            # Swap to extend entanglement
            current_left, current_right = self.swapping_protocol.entanglement_swapping(
                (current_left, current_right),
                (next_segment.alice_qubit, next_segment.bob_qubit)
            )
        
        return current_left, current_right
    
    def purify_entanglement(
        self,
        noisy_pairs: List[Tuple[QuantumKnowledgeState, QuantumKnowledgeState]]
    ) -> Tuple[QuantumKnowledgeState, QuantumKnowledgeState]:
        """
        Purify noisy entangled pairs to get higher fidelity.
        
        Uses entanglement distillation protocol.
        """
        if len(noisy_pairs) < 2:
            return noisy_pairs[0] if noisy_pairs else (None, None)
        
        # Simplified purification - take best pair
        best_pair = noisy_pairs[0]
        best_fidelity = 0
        
        for pair in noisy_pairs:
            # Estimate fidelity (simplified)
            if pair[0].is_maximally_entangled():
                return pair
        
        return best_pair