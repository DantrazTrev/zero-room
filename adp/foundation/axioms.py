"""
Foundational Axioms and Methods
================================

Implements the logical foundations upon which the protocol operates.
These axioms are universally true and accessible to all entities.
"""

from typing import Any, List, Callable, Optional, Dict
from dataclasses import dataclass
from abc import ABC, abstractmethod
import hashlib
from ..core.realms import LogicalState


@dataclass(frozen=True)
class Axiom:
    """Represents a fundamental truth in the system."""
    name: str
    statement: str
    implications: tuple
    
    def verify(self, context: Any) -> bool:
        """Verify the axiom holds in a given context."""
        # Axioms are always true by definition
        return True
        
    def apply(self, input_state: LogicalState) -> LogicalState:
        """Apply the axiom to derive new knowledge."""
        derived = f"{self.statement} IMPLIES {input_state.content}"
        return LogicalState(content=derived)


class SharedAxiom:
    """
    Collection of fundamental axioms that govern the protocol.
    
    These axioms are the logical foundation from which all
    authentication properties emerge.
    """
    
    # Core axioms of the protocol
    DISTINCTION = Axiom(
        name="Axiom of Distinction",
        statement="That which can be distinguished exists",
        implications=("existence", "uniqueness", "verifiability")
    )
    
    SEPARATION = Axiom(
        name="Axiom of Separation", 
        statement="That which is separate cannot be simultaneously shared",
        implications=("exclusivity", "boundary", "non-contradiction")
    )
    
    CONSISTENCY = Axiom(
        name="Axiom of Consistency",
        statement="A proposition cannot be both true and false",
        implications=("determinism", "reliability", "trust")
    )
    
    WITNESS = Axiom(
        name="Axiom of Witness",
        statement="That which is observed by all is shared by all",
        implications=("publicity", "consensus", "verification")
    )
    
    def __init__(self):
        """Initialize the axiom system."""
        self._axioms = [
            self.DISTINCTION,
            self.SEPARATION,
            self.CONSISTENCY,
            self.WITNESS
        ]
        
    def get_all_axioms(self) -> List[Axiom]:
        """Return all foundational axioms."""
        return self._axioms.copy()
        
    def derive_from_axioms(self, premise: LogicalState) -> List[LogicalState]:
        """Derive new truths from axioms and a premise."""
        derivations = []
        for axiom in self._axioms:
            derivation = axiom.apply(premise)
            derivations.append(derivation)
        return derivations
        
    def verify_consistency(self, state1: LogicalState, state2: LogicalState) -> bool:
        """Verify two states are logically consistent."""
        # Apply consistency axiom
        if state1.content == state2.content:
            return True
        
        # If both are dicts, check for contradictions in shared keys
        if isinstance(state1.content, dict) and isinstance(state2.content, dict):
            # Only check keys that exist in both
            common_keys = set(state1.content.keys()) & set(state2.content.keys())
            for key in common_keys:
                # Skip type-related keys as they describe different aspects
                if key in ['type', 'timestamp', 'method']:
                    continue
                # Check for actual contradictions
                if state1.content[key] != state2.content[key]:
                    # Only fail if it's the same entity with different values
                    if 'entity' in state1.content and 'entity' in state2.content:
                        if state1.content['entity'] == state2.content['entity']:
                            return False
        
        # Different types or non-overlapping content is consistent (no contradiction)
        return True


class SharedMethod:
    """
    Universal verification procedures available to all entities.
    
    These methods operate only on shared information and can be
    executed by any entity to verify claims.
    """
    
    def __init__(self):
        """Initialize shared methods."""
        self._methods: Dict[str, Callable] = {}
        self._register_core_methods()
        
    def _register_core_methods(self):
        """Register fundamental verification methods."""
        
        def hash_verification(input_data: str, expected_hash: str) -> bool:
            """Verify data produces expected hash."""
            computed = hashlib.sha256(input_data.encode()).hexdigest()
            return computed == expected_hash
            
        def logical_implication(premise: bool, conclusion: bool) -> bool:
            """Verify logical implication holds."""
            # P -> Q is false only when P is true and Q is false
            return not premise or conclusion
            
        def boundary_check(shared_data: Any, exclusive_claim: Any) -> bool:
            """Verify exclusive claim doesn't contradict shared data."""
            # If data is shared, it cannot be exclusive
            if shared_data == exclusive_claim:
                return False
            return True
            
        self._methods['hash_verification'] = hash_verification
        self._methods['logical_implication'] = logical_implication
        self._methods['boundary_check'] = boundary_check
        
    def register_method(self, name: str, method: Callable) -> None:
        """Register a new shared verification method."""
        if name in self._methods:
            raise ValueError(f"Method {name} already registered")
        self._methods[name] = method
        
    def execute_method(self, name: str, *args, **kwargs) -> Any:
        """Execute a shared method."""
        if name not in self._methods:
            raise ValueError(f"Method {name} not found")
        return self._methods[name](*args, **kwargs)
        
    def list_methods(self) -> List[str]:
        """List all available shared methods."""
        return list(self._methods.keys())
        
    def create_verification_procedure(self, steps: List[tuple]) -> Callable:
        """
        Create a composite verification procedure from basic methods.
        
        Args:
            steps: List of (method_name, args) tuples
        """
        def composite_procedure(input_data: Any) -> bool:
            result = input_data
            for method_name, method_args in steps:
                if method_name not in self._methods:
                    return False
                result = self._methods[method_name](result, *method_args)
                if result is False:
                    return False
            return True
            
        return composite_procedure


class SharedWitness:
    """
    Collective observation and validation system.
    
    Manages facts that have been witnessed and validated by
    multiple entities, making them part of shared knowledge.
    """
    
    def __init__(self, required_witnesses: int = 2):
        """
        Initialize the witness system.
        
        Args:
            required_witnesses: Minimum witnesses needed to establish shared fact
        """
        self._required_witnesses = required_witnesses
        self._observations: Dict[str, List[str]] = {}  # fact_id -> list of witnesses
        self._validated_facts: Dict[str, LogicalState] = {}
        
    def witness(self, fact: LogicalState, witness_id: str) -> bool:
        """
        Record a witness observation of a fact.
        
        Returns:
            True if fact is now validated (enough witnesses)
        """
        fact_id = self._generate_fact_id(fact)
        
        if fact_id not in self._observations:
            self._observations[fact_id] = []
            
        if witness_id not in self._observations[fact_id]:
            self._observations[fact_id].append(witness_id)
            
        # Check if we have enough witnesses
        if len(self._observations[fact_id]) >= self._required_witnesses:
            self._validated_facts[fact_id] = fact
            return True
            
        return False
        
    def _generate_fact_id(self, fact: LogicalState) -> str:
        """Generate unique ID for a fact."""
        content_str = str(fact.content)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
        
    def is_witnessed(self, fact: LogicalState) -> bool:
        """Check if a fact has been sufficiently witnessed."""
        fact_id = self._generate_fact_id(fact)
        return fact_id in self._validated_facts
        
    def get_witnesses(self, fact: LogicalState) -> List[str]:
        """Get list of witnesses for a fact."""
        fact_id = self._generate_fact_id(fact)
        return self._observations.get(fact_id, []).copy()
        
    def get_validated_facts(self) -> List[LogicalState]:
        """Get all validated facts."""
        return list(self._validated_facts.values())
        
    def create_witness_proof(self, fact: LogicalState) -> Optional[Dict]:
        """
        Create proof that a fact has been witnessed.
        
        Returns:
            Proof dictionary or None if not sufficiently witnessed
        """
        if not self.is_witnessed(fact):
            return None
            
        fact_id = self._generate_fact_id(fact)
        return {
            'fact': fact.content,
            'fact_id': fact_id,
            'witnesses': self._observations[fact_id].copy(),
            'witness_count': len(self._observations[fact_id]),
            'required_witnesses': self._required_witnesses,
            'validated': True
        }