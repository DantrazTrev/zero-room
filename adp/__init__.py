"""
Axiom of Distinction Protocol (ADP)
====================================

A foundational authentication system based on pure logical principles.

The protocol operates on the fundamental distinction between:
- SHARED: Information that exists simultaneously for all entities
- SEPARATE: Information that exists exclusively for one entity

This implementation proves that authentication can emerge from pure
philosophical foundations rather than technological complexity.
"""

from .core.realms import SharedRealm, SeparateRealm, LogicalState
from .core.state import StateTransition, LogicalBoundary, StateType
from .foundation.axioms import SharedAxiom, SharedMethod, SharedWitness
from .entities.entity import Entity, BoundaryCommitment, SeparationDeclaration
from .protocol.challenge import (
    SharedChallenge, ExclusiveApplication, ConsistencyVerification,
    ChallengeParameters, Challenge, ChallengeResponse
)
from .verification.engine import (
    LogicalValidator, UniversalVerifier, IntegrityChecker,
    VerificationResult, VerificationReport
)
from .protocol.adp import AxiomDistinctionProtocol, ProtocolConfig

__version__ = "1.0.0"
__author__ = "ADP Foundation"

__all__ = [
    'SharedRealm', 'SeparateRealm', 'LogicalState', 'StateTransition', 'LogicalBoundary', 'StateType',
    'SharedAxiom', 'SharedMethod', 'SharedWitness',
    'Entity', 'BoundaryCommitment', 'SeparationDeclaration',
    'SharedChallenge', 'ExclusiveApplication', 'ConsistencyVerification',
    'ChallengeParameters', 'Challenge', 'ChallengeResponse',
    'LogicalValidator', 'UniversalVerifier', 'IntegrityChecker',
    'VerificationResult', 'VerificationReport',
    'AxiomDistinctionProtocol', 'ProtocolConfig'
]