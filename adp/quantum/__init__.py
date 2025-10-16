"""
Quantum Knowledge Distinction Module
=====================================

This module explores the fundamental ways of distinguishing knowledge
using principles from quantum computing, building on the zero room concept.
"""

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
    QuantumAxiom,
    QuantumFoundations,
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
from .quantum_error_correction import (
    QuantumError,
    QuantumRepetitionCode,
    ShorCode,
    SurfaceCode,
    QuantumKnowledgeProtection
)
from .quantum_teleportation import (
    QuantumTeleportation,
    TeleportationChannel,
    QuantumCompression,
    QuantumSwapping,
    QuantumRepeater
)
from .quantum_hybrid import (
    HybridKnowledgeState,
    ProcessingMode,
    QuantumOracleDatabase,
    HybridProcessor,
    QuantumEncryption,
    HybridAuthenticationSystem
)

__all__ = [
    # Core quantum states
    'QuantumKnowledgeState',
    'QuantumAmplitude',
    'QuantumBasis',
    'QuantumSuperposition',
    'QuantumEntanglement',
    'QuantumMeasurement',
    'QuantumZeroRoom',
    'QuantumKnowledgeDistinction',
    # Foundations
    'QuantumAxiom',
    'QuantumFoundations',
    'QuantumObserver',
    'QuantumBoundary',
    'QuantumCollapse',
    'QuantumCoherence',
    # Protocols
    'QuantumAuthenticationProtocol',
    'QuantumWitness',
    'QuantumCommitment',
    'QuantumVerification',
    # Error correction
    'QuantumError',
    'QuantumRepetitionCode',
    'ShorCode',
    'SurfaceCode',
    'QuantumKnowledgeProtection',
    # Teleportation and compression
    'QuantumTeleportation',
    'TeleportationChannel',
    'QuantumCompression',
    'QuantumSwapping',
    'QuantumRepeater',
    # Hybrid systems
    'HybridKnowledgeState',
    'ProcessingMode',
    'QuantumOracleDatabase',
    'HybridProcessor',
    'QuantumEncryption',
    'HybridAuthenticationSystem'
]