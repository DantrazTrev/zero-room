"""
Quantum Knowledge Distinction
==============================

Implements fundamental ways of distinguishing knowledge using quantum computing
principles. This module explores how quantum properties like superposition,
entanglement, and measurement create fundamental distinctions in knowledge.
"""

from typing import Any, Dict, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import numpy as np
from abc import ABC, abstractmethod
import time
import math


class QuantumBasis(Enum):
    """Fundamental measurement bases for quantum knowledge states."""
    COMPUTATIONAL = "computational"  # |0⟩, |1⟩ basis
    HADAMARD = "hadamard"  # |+⟩, |-⟩ basis
    PHASE = "phase"  # |i⟩, |-i⟩ basis
    ENTANGLED = "entangled"  # Bell basis


@dataclass(frozen=True)
class QuantumAmplitude:
    """Complex amplitude for quantum states."""
    real: float
    imaginary: float = 0.0
    
    @property
    def probability(self) -> float:
        """Calculate probability from amplitude (|ψ|²)."""
        return self.real**2 + self.imaginary**2
    
    @property
    def phase(self) -> float:
        """Calculate phase of the amplitude."""
        return math.atan2(self.imaginary, self.real)
    
    def conjugate(self) -> 'QuantumAmplitude':
        """Return complex conjugate."""
        return QuantumAmplitude(self.real, -self.imaginary)
    
    def __mul__(self, other: Union[float, 'QuantumAmplitude']) -> 'QuantumAmplitude':
        """Multiply amplitudes."""
        if isinstance(other, (int, float)):
            return QuantumAmplitude(self.real * other, self.imaginary * other)
        # Complex multiplication: (a+bi)(c+di) = (ac-bd) + (ad+bc)i
        return QuantumAmplitude(
            self.real * other.real - self.imaginary * other.imaginary,
            self.real * other.imaginary + self.imaginary * other.real
        )


@dataclass
class QuantumKnowledgeState:
    """
    Represents knowledge in a quantum superposition state.
    
    Unlike classical knowledge which is either known or unknown,
    quantum knowledge can exist in superposition - simultaneously
    known and unknown until measured.
    """
    
    label: str
    amplitudes: Dict[str, QuantumAmplitude]  # basis_state -> amplitude
    basis: QuantumBasis = QuantumBasis.COMPUTATIONAL
    entangled_with: Optional[Set[str]] = None
    coherence_time: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Ensure state is normalized."""
        self.normalize()
        if self.entangled_with is None:
            self.entangled_with = set()
    
    def normalize(self):
        """Normalize the quantum state so total probability = 1."""
        total_prob = sum(amp.probability for amp in self.amplitudes.values())
        if total_prob > 0:
            norm_factor = 1.0 / math.sqrt(total_prob)
            self.amplitudes = {
                state: QuantumAmplitude(
                    amp.real * norm_factor,
                    amp.imaginary * norm_factor
                )
                for state, amp in self.amplitudes.items()
            }
    
    def get_probability(self, basis_state: str) -> float:
        """Get probability of measuring a specific basis state."""
        if basis_state in self.amplitudes:
            return self.amplitudes[basis_state].probability
        return 0.0
    
    def is_pure_state(self) -> bool:
        """Check if this is a pure state (single basis state with probability 1)."""
        probabilities = [amp.probability for amp in self.amplitudes.values()]
        return any(abs(p - 1.0) < 1e-10 for p in probabilities)
    
    def is_maximally_entangled(self) -> bool:
        """Check if state is maximally entangled (equal superposition)."""
        if len(self.amplitudes) < 2:
            return False
        probabilities = [amp.probability for amp in self.amplitudes.values()]
        expected_prob = 1.0 / len(self.amplitudes)
        return all(abs(p - expected_prob) < 1e-10 for p in probabilities)
    
    def apply_phase_shift(self, phase: float) -> 'QuantumKnowledgeState':
        """Apply a phase shift to the quantum state."""
        phase_factor = QuantumAmplitude(math.cos(phase), math.sin(phase))
        new_amplitudes = {
            state: amp * phase_factor
            for state, amp in self.amplitudes.items()
        }
        return QuantumKnowledgeState(
            label=f"{self.label}_phase_shifted",
            amplitudes=new_amplitudes,
            basis=self.basis,
            entangled_with=self.entangled_with.copy()
        )
    
    def tensor_product(self, other: 'QuantumKnowledgeState') -> 'QuantumKnowledgeState':
        """Create tensor product of two quantum states."""
        new_amplitudes = {}
        for state1, amp1 in self.amplitudes.items():
            for state2, amp2 in other.amplitudes.items():
                combined_state = f"{state1}⊗{state2}"
                new_amplitudes[combined_state] = amp1 * amp2
        
        return QuantumKnowledgeState(
            label=f"{self.label}⊗{other.label}",
            amplitudes=new_amplitudes,
            basis=QuantumBasis.ENTANGLED,
            entangled_with=self.entangled_with | other.entangled_with | {self.label, other.label}
        )


class QuantumSuperposition:
    """
    Creates and manages quantum superposition of knowledge states.
    
    In the zero room, knowledge can exist in superposition - neither
    fully known nor fully unknown, but in a coherent combination of both.
    """
    
    @staticmethod
    def create_equal_superposition(states: List[str], label: str = "superposition") -> QuantumKnowledgeState:
        """Create equal superposition of multiple states."""
        amplitude = 1.0 / math.sqrt(len(states))
        amplitudes = {state: QuantumAmplitude(amplitude) for state in states}
        return QuantumKnowledgeState(label=label, amplitudes=amplitudes)
    
    @staticmethod
    def create_weighted_superposition(
        state_weights: Dict[str, float],
        label: str = "weighted_superposition"
    ) -> QuantumKnowledgeState:
        """Create weighted superposition with specific probabilities."""
        # Convert weights to amplitudes (sqrt of probabilities)
        total_weight = sum(state_weights.values())
        amplitudes = {
            state: QuantumAmplitude(math.sqrt(weight / total_weight))
            for state, weight in state_weights.items()
        }
        return QuantumKnowledgeState(label=label, amplitudes=amplitudes)
    
    @staticmethod
    def create_hadamard_state(classical_bit: bool, label: str = "hadamard") -> QuantumKnowledgeState:
        """Apply Hadamard gate to create superposition from classical bit."""
        if classical_bit:  # |1⟩ -> (|0⟩ - |1⟩)/√2
            amplitudes = {
                "0": QuantumAmplitude(1/math.sqrt(2)),
                "1": QuantumAmplitude(-1/math.sqrt(2))
            }
        else:  # |0⟩ -> (|0⟩ + |1⟩)/√2
            amplitudes = {
                "0": QuantumAmplitude(1/math.sqrt(2)),
                "1": QuantumAmplitude(1/math.sqrt(2))
            }
        return QuantumKnowledgeState(
            label=label,
            amplitudes=amplitudes,
            basis=QuantumBasis.HADAMARD
        )
    
    @staticmethod
    def interfere_states(
        state1: QuantumKnowledgeState,
        state2: QuantumKnowledgeState,
        phase_difference: float = 0
    ) -> QuantumKnowledgeState:
        """
        Create interference between two quantum states.
        
        Quantum interference allows for constructive and destructive
        combination of knowledge states.
        """
        # Apply phase to second state
        state2_phased = state2.apply_phase_shift(phase_difference)
        
        # Combine amplitudes with interference
        combined_amplitudes = {}
        all_basis_states = set(state1.amplitudes.keys()) | set(state2_phased.amplitudes.keys())
        
        for basis_state in all_basis_states:
            amp1 = state1.amplitudes.get(basis_state, QuantumAmplitude(0))
            amp2 = state2_phased.amplitudes.get(basis_state, QuantumAmplitude(0))
            
            # Add amplitudes (quantum interference)
            combined = QuantumAmplitude(
                amp1.real + amp2.real,
                amp1.imaginary + amp2.imaginary
            )
            if combined.probability > 1e-10:  # Filter out near-zero amplitudes
                combined_amplitudes[basis_state] = combined
        
        return QuantumKnowledgeState(
            label=f"interference({state1.label},{state2.label})",
            amplitudes=combined_amplitudes,
            basis=state1.basis
        )


class QuantumEntanglement:
    """
    Creates and manages entangled knowledge states.
    
    Entanglement represents fundamental correlation between pieces of knowledge
    that cannot be described independently - measuring one instantly determines the other.
    """
    
    @staticmethod
    def create_bell_state(bell_type: str = "Φ+") -> Tuple[QuantumKnowledgeState, QuantumKnowledgeState]:
        """
        Create Bell states - maximally entangled two-qubit states.
        
        Bell states represent perfect correlation between knowledge:
        - |Φ+⟩ = (|00⟩ + |11⟩)/√2  (both same)
        - |Φ-⟩ = (|00⟩ - |11⟩)/√2  (both same, phase difference)
        - |Ψ+⟩ = (|01⟩ + |10⟩)/√2  (always different)
        - |Ψ-⟩ = (|01⟩ - |10⟩)/√2  (always different, phase difference)
        """
        if bell_type == "Φ+":
            amplitudes = {
                "00": QuantumAmplitude(1/math.sqrt(2)),
                "11": QuantumAmplitude(1/math.sqrt(2))
            }
        elif bell_type == "Φ-":
            amplitudes = {
                "00": QuantumAmplitude(1/math.sqrt(2)),
                "11": QuantumAmplitude(-1/math.sqrt(2))
            }
        elif bell_type == "Ψ+":
            amplitudes = {
                "01": QuantumAmplitude(1/math.sqrt(2)),
                "10": QuantumAmplitude(1/math.sqrt(2))
            }
        else:  # Ψ-
            amplitudes = {
                "01": QuantumAmplitude(1/math.sqrt(2)),
                "10": QuantumAmplitude(-1/math.sqrt(2))
            }
        
        entangled_state = QuantumKnowledgeState(
            label=f"Bell_{bell_type}",
            amplitudes=amplitudes,
            basis=QuantumBasis.ENTANGLED,
            entangled_with={"qubit_A", "qubit_B"}
        )
        
        # Return two entangled references (both point to same entangled state)
        return entangled_state, entangled_state
    
    @staticmethod
    def create_ghz_state(num_qubits: int = 3) -> QuantumKnowledgeState:
        """
        Create GHZ state - multi-party entangled state.
        
        GHZ states represent all-or-nothing correlation:
        |GHZ⟩ = (|000...0⟩ + |111...1⟩)/√2
        """
        all_zeros = "0" * num_qubits
        all_ones = "1" * num_qubits
        
        amplitudes = {
            all_zeros: QuantumAmplitude(1/math.sqrt(2)),
            all_ones: QuantumAmplitude(1/math.sqrt(2))
        }
        
        return QuantumKnowledgeState(
            label=f"GHZ_{num_qubits}",
            amplitudes=amplitudes,
            basis=QuantumBasis.ENTANGLED,
            entangled_with={f"qubit_{i}" for i in range(num_qubits)}
        )
    
    @staticmethod
    def entangle_knowledge(
        knowledge1: QuantumKnowledgeState,
        knowledge2: QuantumKnowledgeState,
        correlation_type: str = "positive"
    ) -> QuantumKnowledgeState:
        """
        Entangle two knowledge states with specified correlation.
        
        Args:
            knowledge1: First knowledge state
            knowledge2: Second knowledge state
            correlation_type: "positive" (same values), "negative" (opposite values)
        """
        entangled_amplitudes = {}
        
        for state1, amp1 in knowledge1.amplitudes.items():
            for state2, amp2 in knowledge2.amplitudes.items():
                if correlation_type == "positive" and state1 == state2:
                    # Correlated: both have same value
                    combined_state = f"{state1}{state2}"
                    entangled_amplitudes[combined_state] = amp1 * amp2
                elif correlation_type == "negative" and state1 != state2:
                    # Anti-correlated: always have opposite values
                    combined_state = f"{state1}{state2}"
                    entangled_amplitudes[combined_state] = amp1 * amp2
        
        return QuantumKnowledgeState(
            label=f"entangled({knowledge1.label},{knowledge2.label})",
            amplitudes=entangled_amplitudes,
            basis=QuantumBasis.ENTANGLED,
            entangled_with=knowledge1.entangled_with | knowledge2.entangled_with | {knowledge1.label, knowledge2.label}
        )


class QuantumMeasurement:
    """
    Implements quantum measurement and collapse of knowledge states.
    
    Measurement is the fundamental act that distinguishes quantum knowledge
    from classical - it irreversibly collapses superposition into definite states.
    """
    
    @staticmethod
    def measure(state: QuantumKnowledgeState, basis: Optional[QuantumBasis] = None) -> Tuple[str, QuantumKnowledgeState]:
        """
        Measure a quantum state, causing collapse.
        
        Returns:
            Measured outcome and collapsed state
        """
        if basis is None:
            basis = state.basis
        
        # Calculate measurement probabilities
        probabilities = {
            basis_state: amp.probability
            for basis_state, amp in state.amplitudes.items()
        }
        
        # Handle empty state
        if not probabilities:
            # Return a default collapsed state
            return "undefined", QuantumKnowledgeState(
                label=f"{state.label}_collapsed",
                amplitudes={"undefined": QuantumAmplitude(1.0)},
                basis=basis
            )
        
        # Randomly select outcome based on probabilities
        import random
        outcome = random.choices(
            list(probabilities.keys()),
            weights=list(probabilities.values())
        )[0]
        
        # Collapse state to measured outcome
        collapsed_amplitudes = {outcome: QuantumAmplitude(1.0)}
        collapsed_state = QuantumKnowledgeState(
            label=f"{state.label}_collapsed",
            amplitudes=collapsed_amplitudes,
            basis=basis,
            entangled_with=state.entangled_with
        )
        
        return outcome, collapsed_state
    
    @staticmethod
    def weak_measurement(
        state: QuantumKnowledgeState,
        strength: float = 0.1
    ) -> Tuple[float, QuantumKnowledgeState]:
        """
        Perform weak measurement that partially collapses the state.
        
        Weak measurements extract partial information while preserving
        some quantum coherence.
        """
        # Calculate expectation value
        expectation = sum(
            float(basis_state) * amp.probability
            for basis_state, amp in state.amplitudes.items()
            if basis_state.isdigit()
        )
        
        # Partially collapse based on measurement strength
        new_amplitudes = {}
        for basis_state, amp in state.amplitudes.items():
            # Bias towards measured value
            if basis_state.isdigit():
                bias = 1 + strength * (float(basis_state) - expectation)
            else:
                bias = 1
            
            new_amp = QuantumAmplitude(
                amp.real * math.sqrt(bias),
                amp.imaginary * math.sqrt(bias)
            )
            new_amplitudes[basis_state] = new_amp
        
        partially_collapsed = QuantumKnowledgeState(
            label=f"{state.label}_weakly_measured",
            amplitudes=new_amplitudes,
            basis=state.basis,
            entangled_with=state.entangled_with
        )
        
        return expectation, partially_collapsed
    
    @staticmethod
    def measure_in_basis(
        state: QuantumKnowledgeState,
        measurement_basis: List[QuantumKnowledgeState]
    ) -> Tuple[int, QuantumKnowledgeState]:
        """
        Measure state in an arbitrary basis.
        
        This allows measurement of knowledge in different "contexts"
        or "perspectives".
        """
        # Project state onto measurement basis
        projections = []
        for basis_vector in measurement_basis:
            # Calculate inner product ⟨basis|state⟩
            overlap = 0
            for basis_state in state.amplitudes:
                if basis_state in basis_vector.amplitudes:
                    overlap += (
                        state.amplitudes[basis_state].conjugate() *
                        basis_vector.amplitudes[basis_state]
                    ).real
            projections.append(abs(overlap)**2)
        
        # Choose outcome based on projection probabilities
        import random
        outcome_index = random.choices(
            range(len(measurement_basis)),
            weights=projections
        )[0]
        
        # Collapse to chosen basis state
        collapsed_state = measurement_basis[outcome_index]
        
        return outcome_index, collapsed_state


class QuantumZeroRoom:
    """
    The Quantum Zero Room - a space where knowledge exists in fundamental
    quantum superposition until observed.
    
    In this room, the distinction between known and unknown is not binary
    but exists on a quantum continuum. Knowledge can be:
    - Superposed (both known and unknown)
    - Entangled (correlated with other knowledge)
    - Coherent (maintaining quantum phase relationships)
    - Collapsed (classical after measurement)
    """
    
    def __init__(self):
        """Initialize the Quantum Zero Room."""
        self.knowledge_states: Dict[str, QuantumKnowledgeState] = {}
        self.entanglement_graph: Dict[str, Set[str]] = {}
        self.measurement_history: List[Dict[str, Any]] = []
        self.coherence_threshold = 1e-6  # Minimum coherence before decoherence
        
    def add_quantum_knowledge(
        self,
        knowledge_id: str,
        initial_state: Union[QuantumKnowledgeState, str]
    ):
        """Add quantum knowledge to the zero room."""
        if isinstance(initial_state, str):
            # Create simple superposition from classical knowledge
            state = QuantumSuperposition.create_equal_superposition(
                ["unknown", initial_state],
                label=knowledge_id
            )
        else:
            state = initial_state
        
        self.knowledge_states[knowledge_id] = state
        self.entanglement_graph[knowledge_id] = state.entangled_with
    
    def entangle_knowledge_items(
        self,
        id1: str,
        id2: str,
        correlation_type: str = "positive"
    ):
        """Create entanglement between two knowledge items."""
        if id1 not in self.knowledge_states or id2 not in self.knowledge_states:
            raise ValueError("Both knowledge items must exist")
        
        state1 = self.knowledge_states[id1]
        state2 = self.knowledge_states[id2]
        
        # Create entangled state
        entangled = QuantumEntanglement.entangle_knowledge(
            state1, state2, correlation_type
        )
        
        # Update both states to reference the entanglement
        self.knowledge_states[f"{id1}_{id2}_entangled"] = entangled
        self.entanglement_graph[id1].add(id2)
        self.entanglement_graph[id2].add(id1)
    
    def observe_knowledge(
        self,
        knowledge_id: str,
        basis: Optional[QuantumBasis] = None,
        weak: bool = False
    ) -> Tuple[Any, QuantumKnowledgeState]:
        """
        Observe knowledge, causing quantum collapse.
        
        This is the fundamental act of distinction - transforming
        quantum superposition into classical knowledge.
        """
        if knowledge_id not in self.knowledge_states:
            raise ValueError(f"Knowledge {knowledge_id} not found")
        
        state = self.knowledge_states[knowledge_id]
        
        if weak:
            result, collapsed = QuantumMeasurement.weak_measurement(state)
        else:
            result, collapsed = QuantumMeasurement.measure(state, basis)
        
        # Record measurement
        self.measurement_history.append({
            'knowledge_id': knowledge_id,
            'result': result,
            'basis': basis,
            'timestamp': time.time(),
            'weak': weak,
            'entangled_items': list(state.entangled_with)
        })
        
        # Update state
        self.knowledge_states[knowledge_id] = collapsed
        
        # Handle entanglement collapse
        if not weak and state.entangled_with:
            self._collapse_entangled_states(knowledge_id, result)
        
        return result, collapsed
    
    def _collapse_entangled_states(self, measured_id: str, measurement_result: str):
        """Collapse all entangled states after measurement."""
        entangled_items = self.entanglement_graph.get(measured_id, set())
        
        for item_id in entangled_items:
            if item_id in self.knowledge_states:
                # Collapse entangled state based on measurement
                # This is simplified - real entanglement collapse is more complex
                state = self.knowledge_states[item_id]
                
                # Find correlated outcome
                correlated_amplitudes = {}
                for basis_state, amp in state.amplitudes.items():
                    if measurement_result in basis_state:
                        # This basis state is consistent with measurement
                        correlated_amplitudes[basis_state] = amp
                
                if correlated_amplitudes:
                    collapsed = QuantumKnowledgeState(
                        label=f"{item_id}_correlated_collapse",
                        amplitudes=correlated_amplitudes,
                        basis=state.basis,
                        entangled_with=state.entangled_with - {measured_id}
                    )
                    self.knowledge_states[item_id] = collapsed
    
    def get_knowledge_distinctness(self, knowledge_id: str) -> float:
        """
        Calculate how distinct (classical) vs superposed (quantum) knowledge is.
        
        Returns value between 0 (maximally superposed) and 1 (completely distinct).
        """
        if knowledge_id not in self.knowledge_states:
            return 0.0
        
        state = self.knowledge_states[knowledge_id]
        
        # Pure states are maximally distinct
        if state.is_pure_state():
            return 1.0
        
        # Calculate von Neumann entropy as measure of superposition
        entropy = 0
        for amp in state.amplitudes.values():
            p = amp.probability
            if p > 0:
                entropy -= p * math.log2(p)
        
        # Normalize entropy (max entropy = log2(num_states))
        max_entropy = math.log2(len(state.amplitudes))
        if max_entropy > 0:
            distinctness = 1 - (entropy / max_entropy)
        else:
            distinctness = 1.0
        
        return distinctness
    
    def get_entanglement_strength(self, id1: str, id2: str) -> float:
        """
        Calculate entanglement strength between two knowledge items.
        
        Returns value between 0 (not entangled) and 1 (maximally entangled).
        """
        if id1 not in self.entanglement_graph or id2 not in self.entanglement_graph:
            return 0.0
        
        if id2 not in self.entanglement_graph[id1]:
            return 0.0
        
        # Check if there's a combined entangled state
        entangled_key = f"{id1}_{id2}_entangled"
        if entangled_key in self.knowledge_states:
            state = self.knowledge_states[entangled_key]
            return 1.0 if state.is_maximally_entangled() else 0.5
        
        return 0.5  # Default partial entanglement
    
    def apply_quantum_gate(
        self,
        knowledge_id: str,
        gate_type: str,
        parameters: Optional[Dict] = None
    ) -> QuantumKnowledgeState:
        """
        Apply quantum gate to transform knowledge state.
        
        Gates represent logical operations that preserve quantum properties.
        """
        if knowledge_id not in self.knowledge_states:
            raise ValueError(f"Knowledge {knowledge_id} not found")
        
        state = self.knowledge_states[knowledge_id]
        
        if gate_type == "hadamard":
            # Apply Hadamard to create superposition
            new_state = QuantumSuperposition.create_hadamard_state(
                state.is_pure_state(),
                label=f"{knowledge_id}_H"
            )
        elif gate_type == "phase":
            # Apply phase gate
            phase = parameters.get('phase', math.pi/2) if parameters else math.pi/2
            new_state = state.apply_phase_shift(phase)
        elif gate_type == "cnot":
            # Controlled-NOT for entanglement
            target_id = parameters.get('target') if parameters else None
            if target_id and target_id in self.knowledge_states:
                target = self.knowledge_states[target_id]
                new_state = state.tensor_product(target)
            else:
                new_state = state
        else:
            new_state = state
        
        self.knowledge_states[knowledge_id] = new_state
        return new_state


class QuantumKnowledgeDistinction:
    """
    Framework for fundamental distinction of knowledge using quantum principles.
    
    This class implements the core insight: knowledge distinction is not binary
    but exists on a quantum spectrum. The act of observation (measurement) is
    what creates the distinction between known and unknown.
    """
    
    def __init__(self):
        """Initialize the quantum knowledge distinction framework."""
        self.zero_room = QuantumZeroRoom()
        self.distinction_principles = self._initialize_principles()
        
    def _initialize_principles(self) -> Dict[str, str]:
        """Initialize fundamental principles of quantum knowledge distinction."""
        return {
            "superposition": "Knowledge can exist in multiple states simultaneously until observed",
            "entanglement": "Knowledge items can be fundamentally correlated beyond classical correlation",
            "measurement": "Observation creates distinction by collapsing superposition",
            "complementarity": "Complete knowledge of one property precludes knowledge of complementary property",
            "uncertainty": "There exists a fundamental limit to simultaneous knowledge of conjugate properties",
            "no_cloning": "Unknown quantum knowledge cannot be perfectly copied",
            "decoherence": "Interaction with environment gradually destroys quantum properties",
            "contextuality": "Knowledge meaning depends on measurement context"
        }
    
    def create_knowledge_superposition(
        self,
        knowledge_content: str,
        uncertainty_level: float = 0.5
    ) -> QuantumKnowledgeState:
        """
        Create quantum superposition of knowledge with specified uncertainty.
        
        Args:
            knowledge_content: The knowledge content
            uncertainty_level: 0 (certain) to 1 (maximally uncertain)
        """
        if uncertainty_level <= 0:
            # Certain knowledge - pure state
            amplitudes = {knowledge_content: QuantumAmplitude(1.0)}
        elif uncertainty_level >= 1:
            # Maximally uncertain - equal superposition
            amplitudes = {
                knowledge_content: QuantumAmplitude(1/math.sqrt(2)),
                "unknown": QuantumAmplitude(1/math.sqrt(2))
            }
        else:
            # Partial uncertainty
            known_amp = math.sqrt(1 - uncertainty_level)
            unknown_amp = math.sqrt(uncertainty_level)
            amplitudes = {
                knowledge_content: QuantumAmplitude(known_amp),
                "unknown": QuantumAmplitude(unknown_amp)
            }
        
        return QuantumKnowledgeState(
            label=f"knowledge_{knowledge_content}",
            amplitudes=amplitudes
        )
    
    def establish_knowledge_correlation(
        self,
        knowledge_items: List[str],
        correlation_matrix: Optional[np.ndarray] = None
    ) -> List[QuantumKnowledgeState]:
        """
        Establish quantum correlations between multiple knowledge items.
        
        This creates an entangled state where measuring one item affects all others.
        """
        if correlation_matrix is None:
            # Default to GHZ-like state (all correlated)
            ghz = QuantumEntanglement.create_ghz_state(len(knowledge_items))
            return [ghz]
        
        # Create custom correlation based on matrix
        correlated_states = []
        for i, item1 in enumerate(knowledge_items):
            for j, item2 in enumerate(knowledge_items):
                if i < j and correlation_matrix[i, j] > 0.5:
                    # Create entangled pair
                    state1 = self.create_knowledge_superposition(item1, 0.5)
                    state2 = self.create_knowledge_superposition(item2, 0.5)
                    
                    correlation_type = "positive" if correlation_matrix[i, j] > 0 else "negative"
                    entangled = QuantumEntanglement.entangle_knowledge(
                        state1, state2, correlation_type
                    )
                    correlated_states.append(entangled)
        
        return correlated_states
    
    def measure_knowledge_distinction(
        self,
        state: QuantumKnowledgeState,
        measurement_type: str = "projective"
    ) -> Dict[str, Any]:
        """
        Measure the distinction level of quantum knowledge.
        
        Different measurement types reveal different aspects of knowledge:
        - projective: Complete measurement, full collapse
        - weak: Partial information extraction
        - interaction-free: Determine knowledge without direct measurement
        """
        if measurement_type == "projective":
            outcome, collapsed = QuantumMeasurement.measure(state)
            distinctness = 1.0  # Projective measurement creates full distinction
        elif measurement_type == "weak":
            value, partial_collapse = QuantumMeasurement.weak_measurement(state, strength=0.1)
            outcome = value
            collapsed = partial_collapse
            distinctness = 0.1  # Weak measurement creates partial distinction
        elif measurement_type == "interaction-free":
            # Quantum Zeno effect - repeated weak measurements
            current_state = state
            for _ in range(10):
                _, current_state = QuantumMeasurement.weak_measurement(current_state, strength=0.01)
            outcome = "detected without collapse"
            collapsed = current_state
            distinctness = 0.01  # Minimal distinction
        else:
            outcome = None
            collapsed = state
            distinctness = 0.0
        
        return {
            'outcome': outcome,
            'collapsed_state': collapsed,
            'distinctness': distinctness,
            'measurement_type': measurement_type,
            'original_entropy': self._calculate_entropy(state),
            'final_entropy': self._calculate_entropy(collapsed)
        }
    
    def _calculate_entropy(self, state: QuantumKnowledgeState) -> float:
        """Calculate von Neumann entropy of quantum state."""
        entropy = 0
        for amp in state.amplitudes.values():
            p = amp.probability
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    def demonstrate_complementarity(
        self,
        knowledge_content: str
    ) -> Dict[str, QuantumKnowledgeState]:
        """
        Demonstrate complementarity principle - measuring one property
        destroys information about complementary property.
        """
        # Create state in superposition
        state = QuantumSuperposition.create_hadamard_state(False, knowledge_content)
        
        # Prepare two copies (hypothetically - violates no-cloning)
        computational_copy = QuantumKnowledgeState(
            label=f"{knowledge_content}_computational",
            amplitudes=state.amplitudes.copy(),
            basis=QuantumBasis.COMPUTATIONAL
        )
        
        hadamard_copy = QuantumKnowledgeState(
            label=f"{knowledge_content}_hadamard",
            amplitudes=state.amplitudes.copy(),
            basis=QuantumBasis.HADAMARD
        )
        
        # Measure in different bases
        comp_outcome, comp_collapsed = QuantumMeasurement.measure(
            computational_copy,
            QuantumBasis.COMPUTATIONAL
        )
        
        had_outcome, had_collapsed = QuantumMeasurement.measure(
            hadamard_copy,
            QuantumBasis.HADAMARD
        )
        
        return {
            'original': state,
            'computational_measurement': comp_collapsed,
            'hadamard_measurement': had_collapsed,
            'complementarity_demonstrated': comp_outcome != had_outcome
        }
    
    def create_quantum_authentication(
        self,
        secret_knowledge: str,
        public_challenge: str
    ) -> Dict[str, Any]:
        """
        Create quantum authentication protocol using knowledge distinction.
        
        This demonstrates how quantum properties enable authentication
        without revealing the secret knowledge.
        """
        # Create quantum state from secret
        secret_state = self.create_knowledge_superposition(secret_knowledge, 0.3)
        
        # Entangle with challenge
        challenge_state = self.create_knowledge_superposition(public_challenge, 0.5)
        entangled = QuantumEntanglement.entangle_knowledge(
            secret_state,
            challenge_state,
            "positive"
        )
        
        # Create commitment (measurement basis choice)
        commitment_basis = QuantumBasis.HADAMARD if hash(secret_knowledge) % 2 == 0 else QuantumBasis.COMPUTATIONAL
        
        # Measure challenge in committed basis
        outcome, collapsed = QuantumMeasurement.measure(entangled, commitment_basis)
        
        return {
            'protocol': 'quantum_authentication',
            'commitment_basis': commitment_basis.value,
            'measurement_outcome': outcome,
            'collapsed_state': collapsed,
            'verification': hashlib.sha256(
                f"{secret_knowledge}{public_challenge}{outcome}".encode()
            ).hexdigest()[:16]
        }