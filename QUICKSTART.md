# Quick Start Guide - Axiom Distinction Protocol

## Installation

No external dependencies required - ADP uses only Python standard library.

```bash
# Clone or download the repository
cd /path/to/adp

# Verify Python version (3.8+ required)
python3 --version
```

## Running the Demo

```bash
# Run the interactive demonstration
python3 -m adp.demo

# Run the test suite
python3 -m adp.tests.test_adp

# Run performance analysis
python3 -m adp.analysis
```

## Basic Usage Example

```python
#!/usr/bin/env python3
from adp import AxiomDistinctionProtocol

# Initialize the protocol
protocol = AxiomDistinctionProtocol()

# Register entities
alice = protocol.register_entity("Alice")
bob = protocol.register_entity("Bob")

# Alice declares she has exclusive knowledge
alice.make_separation_declaration("I possess unique knowledge")

# Authenticate Alice
report = protocol.authenticate_entity("Alice")
print(f"Authentication successful: {report.is_successful()}")

# Establish mutual authentication
success, reason = protocol.establish_mutual_authentication("Alice", "Bob")
print(f"Mutual authentication: {reason}")
```

## Key Concepts

### 1. SHARED vs SEPARATE
- **SHARED**: Knowledge available to all entities (axioms, methods, witnesses)
- **SEPARATE**: Knowledge exclusive to one entity (secrets, private data)

### 2. Authentication Without Revelation
The protocol proves you have exclusive knowledge without revealing what it is.

### 3. Logical Boundaries
Boundaries maintain separation between shared and exclusive realms.

### 4. Universal Verification
Any entity can verify authentication using only shared principles.

## Protocol Flow

```
1. Entity Registration
   └─> Creates logical boundary
   └─> Generates exclusive knowledge
   
2. Separation Declaration
   └─> Public claim of exclusive knowledge
   └─> Creates proof without revelation
   
3. Authentication Challenge
   └─> Challenge from shared information
   └─> Response requires exclusive knowledge
   
4. Verification
   └─> Logical validation
   └─> Universal verification
   └─> Integrity checking
```

## Understanding the Output

When you run the demo, you'll see:

- **✓** indicates successful operations
- **✗** indicates failed operations
- **VALID** means authentication succeeded
- **INVALID** means authentication failed

## Philosophical Insight

The protocol demonstrates that authentication is not a technological problem requiring complex cryptography, but a logical one that emerges from the fundamental distinction between what is shared and what is separate.

## Next Steps

1. Explore the source code in `/workspace/adp/`
2. Read the full documentation in `README.md`
3. Experiment with the protocol in Python
4. Consider the philosophical implications

Remember: This protocol operates on pure logical necessity - no cryptographic assumptions required!