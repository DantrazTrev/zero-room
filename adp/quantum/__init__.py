"""
Quantum Knowledge Distinction Module
=====================================

This module explores the fundamental ways of distinguishing knowledge
using principles from quantum computing, building on the zero room concept.
"""

from .quantum_distinction import (
    QuantumKnowledgeState,
    QuantumSuperposition,
    QuantumEntanglement,
    QuantumMeasurement,
    QuantumZeroRoom,
    QuantumKnowledgeDistinction
)
from .quantum_foundations import (
    QuantumAxiom,
    QuantumObserver,
    QuantumBoundary,
    QuantumCollapse,
    QuantumCoherence
)
from .quantum_protocol import (
    QuantumAuthenticationProtocol,
    QuantumWitness,
    QuantumCommitment,
    QuantumVerification
)

__all__ = [
    'QuantumKnowledgeState',
    'QuantumSuperposition',
    'QuantumEntanglement',
    'QuantumMeasurement',
    'QuantumZeroRoom',
    'QuantumKnowledgeDistinction',
    'QuantumAxiom',
    'QuantumObserver',
    'QuantumBoundary',
    'QuantumCollapse',
    'QuantumCoherence',
    'QuantumAuthenticationProtocol',
    'QuantumWitness',
    'QuantumCommitment',
    'QuantumVerification'
]