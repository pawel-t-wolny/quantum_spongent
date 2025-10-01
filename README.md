# Quantum SPONGENT

The first complete quantum circuit implementation of the SPONGENT lightweight hash function.
## Overview

This project implements SPONGENT hash family as a reversible quantum circuit using both Qiskit and a custom reversible circuit simulator. This was a part of my [bachelor thesis](https://www.cs.ru.nl/bachelors-theses/2025/Pawe%C5%82_Wolny___1092613___Design_and_Optimization_of_a_Grover's_Oracle_for_Quantum_Preimage_Attacks_on_SPONGENT_Hash_Function.pdf). SPONGENT is a family of lightweight cryptographic hash functions based on the sponge construction, making it particularly suitable for resource-constrained environments.

## Features

- **Reversible Implementation**: Full reversible circuit implementation of SPONGENT
- **Dual Framework Support**: 
  - Qiskit-based quantum circuit implementation
  - Custom reversible circuit simulator ([revsim](https://github.com/pawel-t-wolny/revsim))
- **Validation Suite**: Comprehensive testing against the reference C++ implementation
- **Configurable Parameters**

## Installation

This project used [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Install dependencies
uv sync
```

Alternatively, using pip in the root directory of the project:

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install .
```

Requirements:
- Python 3.10+
- Dependencies listed in `pyproject.toml`

**Before proceeding make sure the virtual environment is activated!**

## Usage

### Python Implementation

Hash a message using the reversible implementation:

```bash
python reversible_spongent.py "your message here"
```

Quiet mode (outputs only the hash):

```bash
python reversible_spongent.py -q "your message here"
```

### Jupyter Notebook

Explore the quantum circuit implementation interactively:

```bash
jupyter notebook quantum_spongent.ipynb
```

The notebook demonstrates:
- S-box layer construction
- P-layer (permutation) implementation
- LFSR-based round counter
- Complete absorb and squeeze phases
- Full SPONGENT quantum circuit

### Reference Implementation

The C++ reference implementation is included for validation:

```bash
cd spongent_reference
make
./bin/spongent "your message here"
```

## Testing

Validate the Python implementation against the reference:

```bash
./hash_check.sh
```

This script:
1. Generates 1000 random test words
2. Computes hashes using both implementations
3. Compares outputs for consistency

## Project Structure

```
.
├── quantum_spongent.ipynb      # Qiskit circuit implementation
├── reversible_spongent.py      # Revsim-based implementation
├── hash_check.sh               # Validation test suite
├── generate_test_words.py      # Test data generator
├── spongent_reference/         # Original C++ implementation
│   ├── main.cpp
│   ├── Spongent.h
│   └── Makefile
└── pyproject.toml              # Project dependencies
```

## Algorithm Details

SPONGENT is a sponge hash function and thus it operates in two phases:

1. **Absorb Phase**: Message blocks are XORed into the state, followed by the π permutation
2. **Squeeze Phase**: Hash values are extracted from the state with intermittent permutations

Each π permutation round consists of:
- **lCounter**: LFSR-based round constant addition
- **sBoxLayer**: 4-bit S-box applied in parallel to the entire state
- **pLayer**: Bit permutation for diffusion

## References

- [The reference SPONGENT implementation](https://asecuritysite.com/encryption/spongent)
- Original paper: Bogdanov et al., "SPONGENT: A Lightweight Hash Function"