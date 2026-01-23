# Lore-Based Progression Simulator

A formal verification system for character progression in RPGs, ensuring all outcomes are derivable from immutable lore axioms.

## Overview

This simulator implements a **lore-driven progression system** with:
- **Full Observability**: Every state change is logged with cause, rule, and time
- **Formal Verifiability**: Exports to First-Order Logic for Prover9/Mace4 verification
- **Causal Consistency**: All changes must be justified by explicit events
- **Lore Enforcement**: No state changes bypass immutable world rules

## Architecture

```
Lore Layer (Static Axioms)
├── Classes, Stats, Constraints
├── Forbidden Combinations
├── Maximum Bounds
└── Progression Rules

State Layer (Time-Indexed Facts)
├── Character states at each time point
├── Immutable progression history
└── FOL-exportable facts

Event Layer (Causality)
├── Explicit causal events
├── Rule references for justification
└── Effect descriptions

Observation Layer (Explainability)
├── Why/How/When logs
├── Rule traceability
└── Human-readable explanations
```

## Key Principles

### Lore is Law
- All progression must follow immutable axioms
- No procedural overrides or exceptions
- Axioms define possibility, not execution

### No Implicit State Changes
- State evolution only through explicit events
- Every fact has a causal chain
- Time is discrete and explicit

### Full Observability
- Every derived fact has cause + rule + time boundary
- Complete audit trail
- Reproducible simulations

## Usage

### Basic Simulation

```python
from application.use_cases.progression_simulation import create_sample_simulation

# Create simulator with default fantasy lore
simulator = create_sample_simulation()

# Gain experience
simulator.simulate_experience_gain(character_id, 100, "quest_complete")

# Level up (if requirements met)
result = simulator.simulate_level_up(character_id)

# Increase stats (if allowed by class)
simulator.simulate_stat_increase(character_id, StatType.STRENGTH, 5, "training")
```

### Formal Verification

```python
# Export simulation for Prover9/Mace4
files = simulator.export_to_fol(Path("verification_output"))

# Check invariants with Prover9
# prover9 verification_output/axioms.in verification_output/invariants.in

# Find counterexamples with Mace4
# mace4 -f verification_output/state.in verification_output/axioms.in
```

## Sample Lore Axioms

```prolog
% Class definitions
class(warrior).
class(mage).
class(rogue).

% Stat definitions and bounds
stat(strength). max_stat(strength, 100).
stat(intellect). max_stat(intellect, 120).
stat(agility). max_stat(agility, 90).

% Class-stat relationships
uses_stat(warrior, strength).
uses_stat(mage, intellect).
uses_stat(rogue, agility).

% Forbidden combinations
false :- has_class(C, mage), equip(C, heavy_armor, T).

% Progression rules
required_xp(1, 0).
required_xp(2, 100).
required_xp(3, 250).

can_level_up(C, T) :-
    level(C, L, T),
    experience(C, XP, T),
    required_xp(L, R),
    XP >= R.
```

## Invariants Verified

```prolog
% Stat bounds
false :- stat_value(C, S, V, T), max_stat(S, M), V > M.

% Causality - all changes must have events
false :-
    stat_value(C, S, V2, T2),
    stat_value(C, S, V1, T1),
    T2 > T1,
    not exists E (
        effect(E, stat_value(C, S, V2, T2)),
        from_time(E, T1),
        to_time(E, T2)
    ).

% Lore consistency
false :- has_class(C, mage), equip(C, heavy_armor, T).
```

## Running the Demo

```bash
python demo_progression_simulator.py
```

This demonstrates:
1. Experience gain events
2. Level up progression
3. Stat increases with class restrictions
4. Formal verification export

## Formal Verification Setup

### Install Prover9/Mace4

```bash
# Download from University of Miami
# http://www.cs.unm.edu/~mccune/prover9/

# Or on macOS with Homebrew
brew install prover9
```

### Verify Simulation

```bash
# Export simulation
python demo_progression_simulator.py

# Check if invariants hold
prover9 simulation_output/axioms.in simulation_output/invariants.in

# Look for counterexamples
mace4 -f simulation_output/state.in simulation_output/axioms.in
```

## Extensions

- **Lore DSL**: Convert natural language lore to FOL axioms
- **Branching Exploration**: Try all valid progression paths
- **CI Integration**: Automatic lore consistency checks
- **Counterexample Analysis**: Identify unintended valid builds
- **Temporal Logic**: Verify progression sequences over time

## Benefits

✅ **Provable Consistency**: Prover9 guarantees no lore contradictions
✅ **Full Traceability**: Every stat change has documented cause
✅ **Reproducible**: Deterministic simulation from same axioms
✅ **Extensible**: Add new lore rules without breaking existing logic
✅ **Testable**: CI can catch lore violations before deployment</content>
<parameter name="filePath">/Volumes/External/Code/loreSystem/PROGRESSION_SIMULATOR_README.md