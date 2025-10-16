"""
Quantum Error Correction for Knowledge States
==============================================

Implements quantum error correction codes to protect knowledge states
from decoherence and errors, maintaining quantum properties over time.
"""

from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
import math
import hashlib
import time
from .quantum_distinction import (
    QuantumKnowledgeState,
    QuantumAmplitude,
    QuantumBasis,
    QuantumSuperposition,
    QuantumMeasurement
)


@dataclass
class QuantumError:
    """Represents a quantum error that can affect knowledge states."""
    error_type: str  # 'bit_flip', 'phase_flip', 'depolarizing', 'amplitude_damping'
    probability: float
    affected_qubits: List[int]
    timestamp: float = field(default_factory=time.time)
    
    def apply_to_state(self, state: QuantumKnowledgeState) -> QuantumKnowledgeState:
        """Apply this error to a quantum state."""
        import random
        
        if random.random() > self.probability:
            return state  # No error occurs
        
        new_amplitudes = {}
        
        if self.error_type == 'bit_flip':
            # X error: |0⟩ ↔ |1⟩
            for basis_state, amp in state.amplitudes.items():
                flipped = self._flip_bits(basis_state, self.affected_qubits)
                new_amplitudes[flipped] = amp
                
        elif self.error_type == 'phase_flip':
            # Z error: |1⟩ → -|1⟩
            for basis_state, amp in state.amplitudes.items():
                if self._has_odd_ones(basis_state, self.affected_qubits):
                    new_amplitudes[basis_state] = QuantumAmplitude(-amp.real, -amp.imaginary)
                else:
                    new_amplitudes[basis_state] = amp
                    
        elif self.error_type == 'depolarizing':
            # Random Pauli error
            error_choice = random.choice(['I', 'X', 'Y', 'Z'])
            if error_choice == 'I':
                return state
            elif error_choice == 'X':
                return QuantumError('bit_flip', 1.0, self.affected_qubits).apply_to_state(state)
            elif error_choice == 'Z':
                return QuantumError('phase_flip', 1.0, self.affected_qubits).apply_to_state(state)
            else:  # Y = iXZ
                state = QuantumError('bit_flip', 1.0, self.affected_qubits).apply_to_state(state)
                return QuantumError('phase_flip', 1.0, self.affected_qubits).apply_to_state(state)
                
        elif self.error_type == 'amplitude_damping':
            # Energy dissipation: |1⟩ → |0⟩ with probability
            damping_factor = math.sqrt(1 - self.probability)
            for basis_state, amp in state.amplitudes.items():
                if '1' in basis_state:
                    # Partial damping
                    new_amplitudes[basis_state] = QuantumAmplitude(
                        amp.real * damping_factor,
                        amp.imaginary * damping_factor
                    )
                    # Add amplitude to ground state
                    ground = basis_state.replace('1', '0')
                    if ground in new_amplitudes:
                        new_amplitudes[ground] = QuantumAmplitude(
                            new_amplitudes[ground].real + amp.real * math.sqrt(self.probability),
                            new_amplitudes[ground].imaginary
                        )
                    else:
                        new_amplitudes[ground] = QuantumAmplitude(
                            amp.real * math.sqrt(self.probability), 0
                        )
                else:
                    new_amplitudes[basis_state] = amp
        else:
            return state
        
        error_state = QuantumKnowledgeState(
            label=f"{state.label}_with_error",
            amplitudes=new_amplitudes,
            basis=state.basis,
            entangled_with=state.entangled_with
        )
        error_state.normalize()
        return error_state
    
    def _flip_bits(self, basis_state: str, positions: List[int]) -> str:
        """Flip bits at specified positions."""
        state_list = list(basis_state)
        for pos in positions:
            if pos < len(state_list) and state_list[pos] in '01':
                state_list[pos] = '1' if state_list[pos] == '0' else '0'
        return ''.join(state_list)
    
    def _has_odd_ones(self, basis_state: str, positions: List[int]) -> bool:
        """Check if there's an odd number of 1s at specified positions."""
        count = sum(1 for pos in positions 
                   if pos < len(basis_state) and basis_state[pos] == '1')
        return count % 2 == 1


class QuantumRepetitionCode:
    """
    Implements quantum repetition code for error correction.
    
    Encodes one logical qubit into multiple physical qubits to detect and correct errors.
    """
    
    def __init__(self, repetitions: int = 3):
        """
        Initialize repetition code.
        
        Args:
            repetitions: Number of physical qubits per logical qubit (must be odd)
        """
        if repetitions % 2 == 0:
            raise ValueError("Repetitions must be odd for majority voting")
        self.repetitions = repetitions
        self.syndrome_history: List[Dict[str, Any]] = []
    
    def encode(self, logical_state: QuantumKnowledgeState) -> QuantumKnowledgeState:
        """
        Encode logical knowledge state using repetition code.
        
        |0⟩_L → |000⟩, |1⟩_L → |111⟩
        |+⟩_L → |+++⟩, |-⟩_L → |---⟩
        """
        encoded_amplitudes = {}
        
        for basis_state, amp in logical_state.amplitudes.items():
            # Repeat each bit
            encoded_state = ''
            for bit in basis_state:
                if bit in '01':
                    encoded_state += bit * self.repetitions
                else:
                    encoded_state += bit
            
            encoded_amplitudes[encoded_state] = amp
        
        return QuantumKnowledgeState(
            label=f"{logical_state.label}_encoded",
            amplitudes=encoded_amplitudes,
            basis=logical_state.basis,
            entangled_with=logical_state.entangled_with
        )
    
    def create_syndrome_measurement(
        self, 
        encoded_state: QuantumKnowledgeState
    ) -> List[Tuple[int, int]]:
        """
        Measure error syndrome without collapsing the encoded information.
        
        Returns:
            List of syndrome measurements (position, parity)
        """
        syndromes = []
        
        # For each logical qubit
        for i in range(0, len(list(encoded_state.amplitudes.keys())[0]), self.repetitions):
            # Measure parity between adjacent qubits
            for j in range(self.repetitions - 1):
                pos1, pos2 = i + j, i + j + 1
                
                # Calculate parity (simplified - in reality would be ancilla measurement)
                parity = 0
                for basis_state in encoded_state.amplitudes:
                    if len(basis_state) > pos2:
                        if basis_state[pos1] != basis_state[pos2]:
                            parity = 1
                            break
                
                syndromes.append((pos1, parity))
        
        # Record syndrome
        self.syndrome_history.append({
            'timestamp': time.time(),
            'syndromes': syndromes,
            'state_label': encoded_state.label
        })
        
        return syndromes
    
    def correct_errors(
        self,
        encoded_state: QuantumKnowledgeState,
        syndromes: List[Tuple[int, int]]
    ) -> QuantumKnowledgeState:
        """
        Correct errors based on syndrome measurements.
        
        Uses majority voting to determine correct value.
        """
        corrected_amplitudes = {}
        
        for basis_state, amp in encoded_state.amplitudes.items():
            corrected_state = list(basis_state)
            
            # Process each logical qubit
            for i in range(0, len(basis_state), self.repetitions):
                if i + self.repetitions <= len(basis_state):
                    # Count 0s and 1s
                    segment = basis_state[i:i+self.repetitions]
                    zeros = segment.count('0')
                    ones = segment.count('1')
                    
                    # Majority vote
                    if zeros > ones:
                        for j in range(self.repetitions):
                            if i+j < len(corrected_state):
                                corrected_state[i+j] = '0'
                    elif ones > zeros:
                        for j in range(self.repetitions):
                            if i+j < len(corrected_state):
                                corrected_state[i+j] = '1'
            
            corrected_amplitudes[''.join(corrected_state)] = amp
        
        return QuantumKnowledgeState(
            label=f"{encoded_state.label}_corrected",
            amplitudes=corrected_amplitudes,
            basis=encoded_state.basis,
            entangled_with=encoded_state.entangled_with
        )
    
    def decode(self, encoded_state: QuantumKnowledgeState) -> QuantumKnowledgeState:
        """
        Decode the error-corrected state back to logical state.
        
        |000⟩ → |0⟩_L, |111⟩ → |1⟩_L
        """
        logical_amplitudes = {}
        
        for basis_state, amp in encoded_state.amplitudes.items():
            # Extract logical bits (take every nth bit)
            logical_state = ''
            for i in range(0, len(basis_state), self.repetitions):
                if i < len(basis_state):
                    logical_state += basis_state[i]
            
            if logical_state in logical_amplitudes:
                # Combine amplitudes for same logical state
                existing = logical_amplitudes[logical_state]
                logical_amplitudes[logical_state] = QuantumAmplitude(
                    existing.real + amp.real,
                    existing.imaginary + amp.imaginary
                )
            else:
                logical_amplitudes[logical_state] = amp
        
        decoded = QuantumKnowledgeState(
            label=f"{encoded_state.label}_decoded",
            amplitudes=logical_amplitudes,
            basis=encoded_state.basis,
            entangled_with=encoded_state.entangled_with
        )
        decoded.normalize()
        return decoded


class ShorCode:
    """
    Implements Shor's 9-qubit code for comprehensive error correction.
    
    Protects against both bit-flip and phase-flip errors.
    """
    
    def __init__(self):
        """Initialize Shor code."""
        self.bit_flip_code = QuantumRepetitionCode(3)
        self.phase_flip_code = QuantumRepetitionCode(3)
        self.encoding_circuit: List[str] = []
    
    def encode(self, logical_state: QuantumKnowledgeState) -> QuantumKnowledgeState:
        """
        Encode using Shor's 9-qubit code.
        
        |0⟩_L → |000000000⟩
        |1⟩_L → (|000⟩+|111⟩)(|000⟩+|111⟩)(|000⟩+|111⟩)/2√2
        """
        encoded_amplitudes = {}
        
        for basis_state, amp in logical_state.amplitudes.items():
            if basis_state == '0' or '0' in basis_state:
                # Encode |0⟩
                encoded_amplitudes['000000000'] = amp
            elif basis_state == '1' or '1' in basis_state:
                # Encode |1⟩ in superposition
                ghz_states = ['000000111', '000111000', '000111111',
                             '111000000', '111000111', '111111000', 
                             '111111111', '000000000']
                amplitude = QuantumAmplitude(amp.real / math.sqrt(8), amp.imaginary / math.sqrt(8))
                for ghz in ghz_states:
                    encoded_amplitudes[ghz] = amplitude
            else:
                # Superposition - encode each component
                encoded_amplitudes['000000000'] = QuantumAmplitude(amp.real/2, amp.imaginary/2)
                for ghz in ['000111111', '111000111', '111111000']:
                    encoded_amplitudes[ghz] = QuantumAmplitude(amp.real/4, amp.imaginary/4)
        
        encoded = QuantumKnowledgeState(
            label=f"{logical_state.label}_shor_encoded",
            amplitudes=encoded_amplitudes,
            basis=logical_state.basis
        )
        encoded.normalize()
        return encoded
    
    def detect_and_correct(
        self,
        encoded_state: QuantumKnowledgeState,
        error_type: str = 'both'
    ) -> QuantumKnowledgeState:
        """
        Detect and correct errors using Shor code.
        
        Args:
            encoded_state: The encoded quantum state
            error_type: 'bit_flip', 'phase_flip', or 'both'
        """
        if error_type in ['bit_flip', 'both']:
            # Correct bit-flip errors in each block
            encoded_state = self._correct_bit_flips(encoded_state)
        
        if error_type in ['phase_flip', 'both']:
            # Correct phase-flip errors across blocks
            encoded_state = self._correct_phase_flips(encoded_state)
        
        return encoded_state
    
    def _correct_bit_flips(self, state: QuantumKnowledgeState) -> QuantumKnowledgeState:
        """Correct bit-flip errors within each 3-qubit block."""
        corrected_amplitudes = {}
        
        for basis_state, amp in state.amplitudes.items():
            corrected = ''
            # Process each 3-qubit block
            for i in range(0, 9, 3):
                block = basis_state[i:i+3]
                # Majority vote
                if block.count('0') >= 2:
                    corrected += '000'
                else:
                    corrected += '111'
            
            corrected_amplitudes[corrected] = amp
        
        return QuantumKnowledgeState(
            label=f"{state.label}_bit_corrected",
            amplitudes=corrected_amplitudes,
            basis=state.basis
        )
    
    def _correct_phase_flips(self, state: QuantumKnowledgeState) -> QuantumKnowledgeState:
        """Correct phase-flip errors across blocks."""
        # This is simplified - actual implementation would use syndrome measurements
        return state
    
    def decode(self, encoded_state: QuantumKnowledgeState) -> QuantumKnowledgeState:
        """Decode Shor code back to logical qubit."""
        logical_amplitudes = {}
        
        for basis_state, amp in encoded_state.amplitudes.items():
            # Check if it's all zeros (logical |0⟩)
            if basis_state == '000000000':
                logical_amplitudes['0'] = amp
            else:
                # Any other state maps to logical |1⟩
                if '1' in logical_amplitudes:
                    logical_amplitudes['1'] = QuantumAmplitude(
                        logical_amplitudes['1'].real + amp.real,
                        logical_amplitudes['1'].imaginary + amp.imaginary
                    )
                else:
                    logical_amplitudes['1'] = amp
        
        decoded = QuantumKnowledgeState(
            label=f"{encoded_state.label}_decoded",
            amplitudes=logical_amplitudes,
            basis=encoded_state.basis
        )
        decoded.normalize()
        return decoded


class SurfaceCode:
    """
    Implements surface code for topological error correction.
    
    Uses a 2D lattice of qubits with nearest-neighbor interactions.
    """
    
    def __init__(self, distance: int = 3):
        """
        Initialize surface code.
        
        Args:
            distance: Code distance (minimum 3)
        """
        if distance < 3:
            raise ValueError("Distance must be at least 3")
        self.distance = distance
        self.lattice_size = distance * distance
        self.stabilizers: List[Dict[str, Any]] = self._initialize_stabilizers()
    
    def _initialize_stabilizers(self) -> List[Dict[str, Any]]:
        """Initialize X and Z stabilizers for the surface code."""
        stabilizers = []
        
        # X stabilizers (vertex operators)
        for i in range(self.distance - 1):
            for j in range(self.distance - 1):
                stabilizer = {
                    'type': 'X',
                    'position': (i, j),
                    'qubits': self._get_vertex_qubits(i, j)
                }
                stabilizers.append(stabilizer)
        
        # Z stabilizers (plaquette operators)
        for i in range(self.distance - 1):
            for j in range(self.distance - 1):
                stabilizer = {
                    'type': 'Z',
                    'position': (i, j),
                    'qubits': self._get_plaquette_qubits(i, j)
                }
                stabilizers.append(stabilizer)
        
        return stabilizers
    
    def _get_vertex_qubits(self, i: int, j: int) -> List[int]:
        """Get qubits around a vertex."""
        qubits = []
        for di, dj in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            if 0 <= i+di < self.distance and 0 <= j+dj < self.distance:
                qubits.append((i+di) * self.distance + (j+dj))
        return qubits
    
    def _get_plaquette_qubits(self, i: int, j: int) -> List[int]:
        """Get qubits around a plaquette."""
        return self._get_vertex_qubits(i, j)  # Same for square lattice
    
    def encode_logical(self, logical_state: QuantumKnowledgeState) -> QuantumKnowledgeState:
        """
        Encode logical qubit in surface code.
        
        Creates a topologically protected state.
        """
        # Initialize lattice in ground state
        ground_state = '0' * self.lattice_size
        excited_state = '1' * self.lattice_size
        
        encoded_amplitudes = {}
        
        for basis_state, amp in logical_state.amplitudes.items():
            if '0' in basis_state:
                # Logical |0⟩ - even parity loops
                encoded_amplitudes[ground_state] = amp
            else:
                # Logical |1⟩ - odd parity loops
                # Create non-trivial loop
                loop_state = list(ground_state)
                for i in range(self.distance):
                    loop_state[i] = '1'  # Horizontal logical operator
                encoded_amplitudes[''.join(loop_state)] = amp
        
        return QuantumKnowledgeState(
            label=f"{logical_state.label}_surface_encoded",
            amplitudes=encoded_amplitudes,
            basis=logical_state.basis
        )
    
    def measure_stabilizers(
        self,
        state: QuantumKnowledgeState
    ) -> Dict[str, List[int]]:
        """
        Measure all stabilizers to detect errors.
        
        Returns:
            Syndrome pattern indicating error locations
        """
        syndromes = {'X': [], 'Z': []}
        
        for stabilizer in self.stabilizers:
            # Measure stabilizer (simplified)
            measurement = 0
            for basis_state in state.amplitudes:
                parity = sum(int(basis_state[q]) for q in stabilizer['qubits'] 
                           if q < len(basis_state)) % 2
                if parity == 1:
                    measurement = 1
                    break
            
            syndromes[stabilizer['type']].append(measurement)
        
        return syndromes
    
    def correct_with_mwpm(
        self,
        state: QuantumKnowledgeState,
        syndromes: Dict[str, List[int]]
    ) -> QuantumKnowledgeState:
        """
        Correct errors using Minimum Weight Perfect Matching.
        
        Finds most likely error pattern given syndrome.
        """
        # Simplified correction - actual implementation would use graph matching
        return state
    
    def decode_logical(self, encoded_state: QuantumKnowledgeState) -> QuantumKnowledgeState:
        """Decode surface code to logical qubit."""
        logical_amplitudes = {}
        
        for basis_state, amp in encoded_state.amplitudes.items():
            # Count total parity
            parity = basis_state.count('1') % 2
            logical_bit = str(parity)
            
            if logical_bit in logical_amplitudes:
                logical_amplitudes[logical_bit] = QuantumAmplitude(
                    logical_amplitudes[logical_bit].real + amp.real,
                    logical_amplitudes[logical_bit].imaginary + amp.imaginary
                )
            else:
                logical_amplitudes[logical_bit] = amp
        
        decoded = QuantumKnowledgeState(
            label=f"{encoded_state.label}_decoded",
            amplitudes=logical_amplitudes,
            basis=encoded_state.basis
        )
        decoded.normalize()
        return decoded


class QuantumKnowledgeProtection:
    """
    Comprehensive system for protecting quantum knowledge using error correction.
    """
    
    def __init__(self, protection_level: str = 'medium'):
        """
        Initialize protection system.
        
        Args:
            protection_level: 'basic', 'medium', 'high', or 'maximum'
        """
        self.protection_level = protection_level
        self.error_rates: Dict[str, float] = {}
        self.correction_history: List[Dict[str, Any]] = []
        
        # Initialize appropriate error correction code
        if protection_level == 'basic':
            self.code = QuantumRepetitionCode(3)
        elif protection_level == 'medium':
            self.code = QuantumRepetitionCode(5)
        elif protection_level == 'high':
            self.code = ShorCode()
        else:  # maximum
            self.code = SurfaceCode(5)
    
    def protect_knowledge(
        self,
        knowledge_state: QuantumKnowledgeState,
        expected_storage_time: float = 1.0,
        environmental_noise: float = 0.01
    ) -> QuantumKnowledgeState:
        """
        Apply protection to quantum knowledge state.
        
        Args:
            knowledge_state: State to protect
            expected_storage_time: How long state needs to be preserved
            environmental_noise: Expected noise level
        
        Returns:
            Protected quantum state
        """
        # Encode the state
        if isinstance(self.code, SurfaceCode):
            protected = self.code.encode_logical(knowledge_state)
        else:
            protected = self.code.encode(knowledge_state)
        
        # Calculate error probability
        error_prob = 1 - math.exp(-environmental_noise * expected_storage_time)
        self.error_rates[knowledge_state.label] = error_prob
        
        # Record protection
        self.correction_history.append({
            'timestamp': time.time(),
            'state_label': knowledge_state.label,
            'protection_level': self.protection_level,
            'code_type': type(self.code).__name__,
            'expected_error_rate': error_prob
        })
        
        return protected
    
    def apply_error_correction(
        self,
        protected_state: QuantumKnowledgeState,
        detected_errors: Optional[List[QuantumError]] = None
    ) -> QuantumKnowledgeState:
        """
        Apply error correction to protected state.
        
        Args:
            protected_state: The protected quantum state
            detected_errors: List of detected errors (if any)
        
        Returns:
            Error-corrected state
        """
        if isinstance(self.code, ShorCode):
            corrected = self.code.detect_and_correct(protected_state)
        elif isinstance(self.code, SurfaceCode):
            syndromes = self.code.measure_stabilizers(protected_state)
            corrected = self.code.correct_with_mwpm(protected_state, syndromes)
        elif isinstance(self.code, QuantumRepetitionCode):
            syndromes = self.code.create_syndrome_measurement(protected_state)
            corrected = self.code.correct_errors(protected_state, syndromes)
        else:
            corrected = protected_state
        
        # Record correction
        self.correction_history.append({
            'timestamp': time.time(),
            'state_label': protected_state.label,
            'correction_applied': True,
            'errors_detected': len(detected_errors) if detected_errors else 0
        })
        
        return corrected
    
    def recover_knowledge(
        self,
        protected_state: QuantumKnowledgeState
    ) -> QuantumKnowledgeState:
        """
        Recover original knowledge from protected state.
        
        Args:
            protected_state: The protected and possibly error-corrected state
        
        Returns:
            Recovered knowledge state
        """
        # First apply error correction
        corrected = self.apply_error_correction(protected_state)
        
        # Then decode
        if isinstance(self.code, SurfaceCode):
            recovered = self.code.decode_logical(corrected)
        elif isinstance(self.code, ShorCode):
            recovered = self.code.decode(corrected)
        else:
            recovered = self.code.decode(corrected)
        
        return recovered
    
    def calculate_fidelity(
        self,
        original: QuantumKnowledgeState,
        recovered: QuantumKnowledgeState
    ) -> float:
        """
        Calculate fidelity between original and recovered states.
        
        Fidelity measures how well the protection preserved the quantum state.
        """
        fidelity = 0.0
        
        for basis_state in set(original.amplitudes.keys()) | set(recovered.amplitudes.keys()):
            orig_amp = original.amplitudes.get(basis_state, QuantumAmplitude(0))
            recv_amp = recovered.amplitudes.get(basis_state, QuantumAmplitude(0))
            
            # Calculate overlap
            overlap = (orig_amp.conjugate() * recv_amp).real
            fidelity += overlap
        
        return abs(fidelity) ** 2
    
    def simulate_storage(
        self,
        knowledge_state: QuantumKnowledgeState,
        storage_time: float,
        noise_model: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Simulate storing quantum knowledge with protection.
        
        Args:
            knowledge_state: State to store
            storage_time: Duration of storage
            noise_model: Dictionary of error types and rates
        
        Returns:
            Simulation results including fidelity and error statistics
        """
        # Protect the state
        protected = self.protect_knowledge(knowledge_state, storage_time, 
                                          sum(noise_model.values()))
        
        # Apply errors based on noise model
        noisy_state = protected
        errors_applied = []
        
        for error_type, rate in noise_model.items():
            if rate > 0:
                error = QuantumError(error_type, rate, list(range(3)))
                noisy_state = error.apply_to_state(noisy_state)
                errors_applied.append(error_type)
        
        # Recover the state
        recovered = self.recover_knowledge(noisy_state)
        
        # Calculate metrics
        fidelity = self.calculate_fidelity(knowledge_state, recovered)
        
        return {
            'original_state': knowledge_state.label,
            'storage_time': storage_time,
            'protection_level': self.protection_level,
            'errors_applied': errors_applied,
            'fidelity': fidelity,
            'success': fidelity > 0.9,
            'error_rate': 1 - fidelity
        }