# Domain Validation Quick Reference

**Status**: ✅ Production-Ready  
**Test Coverage**: 35/35 tests passing  
**Date**: 2026-01-18

## Quick Validation Rules

### World
- ✅ Name unique per tenant
- ✅ Version monotonically increases
- ✅ updated_at >= created_at

### Character
- ✅ Backstory >= 100 characters
- ✅ Unique ability names (no duplicates)
- ✅ HP, ATK, DEF, Speed >= 0
- ✅ Power level: 1-10
- ✅ Rarity: COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHIC
- ✅ Elements: FIRE, WATER, EARTH, WIND, LIGHT, DARK, PHYSICAL
- ✅ Roles: DPS, TANK, SUPPORT, SPECIALIST

### Event
- ✅ >= 1 participant (cannot be empty)
- ✅ No duplicate participants
- ✅ Cannot remove last participant
- ✅ end_date > start_date
- ✅ Name: non-empty, <= 255 chars
- ✅ Outcomes: SUCCESS, FAILURE, ONGOING

### Banner (Gacha)
- ✅ SSR + SR + R rates = 100% (±0.1% floating point tolerance)
- ✅ SSR rate: 0-10%
- ✅ SR rate: 0-50%
- ✅ Pull costs > 0
- ✅ 10-pull cost <= 10 × single pull cost
- ✅ soft_pity < hard_pity < featured_guarantee
- ✅ Limited banners: end_date > start_date
- ✅ Featured rate: 0-100%

### Pity (Gacha Tracking)
- ✅ All counters >= 0
- ✅ Counters reset to 0 on SSR pull
- ✅ 50/50 system: guaranteed_featured_next flag on loss
- ✅ History tracking: total pulls, SSR pulled, featured pulled

### Item
- ✅ Level: 1-100
- ✅ Enhancement >= 0 (typically 0-20)
- ✅ Max enhancement >= 0
- ✅ ATK, HP, DEF >= 0
- ✅ Name: non-empty, <= 255 chars
- ✅ Types: WEAPON, ARMOR, ARTIFACT, CONSUMABLE, TOOL, OTHER

## Gacha System Guarantees

### Standard Banner
```
SSR (5★): 0.6%
SR (4★):  5.1%
R (3★):   94.3%
= 100.0% ✅

Soft pity:     75 pulls
Hard pity:     90 pulls (guaranteed SSR)
Featured pity: 180 pulls (guaranteed featured SSR)
```

### Limited Banner
```
SSR (5★): 0.6% (50% featured on pull)
SR (4★):  5.1%
R (3★):   94.3%
= 100.0% ✅

Featured rate: 50% (50/50 system)
- If lose 50/50: next SSR guaranteed featured
- If win 50/50: featured_guarantee_pity continues
```

### Pity Mechanics
```
Initial state:
- pulls_since_last_ssr = 0
- pulls_since_last_featured = 0
- guaranteed_featured_next = false

After 75 pulls (no SSR):
- Soft pity activated (increased SSR rate)

After 90 pulls (no SSR):
- Hard pity triggered (guaranteed SSR)

On SSR pull (non-featured):
- pulls_since_last_ssr = 0
- pulls_since_last_featured += 1
- guaranteed_featured_next = true

On SSR pull (featured):
- pulls_since_last_ssr = 0
- pulls_since_last_featured = 0
- guaranteed_featured_next = false
```

## Test Coverage

### Edge Case Tests (35 total)
- ✅ World: 4 tests
- ✅ Character: 8 tests
- ✅ Event: 6 tests
- ✅ Banner: 7 tests
- ✅ Pity: 5 tests
- ✅ Item: 4 tests
- ✅ Cross-entity: 3 tests

### What's Tested
1. **Boundary values**: min/max ranges (0, 1, 10, 100, 255)
2. **Negative values**: all stats, counters (must fail)
3. **Empty/null**: names, participants (must fail)
4. **Duplicates**: ability names, event participants (must fail)
5. **Rate validation**: gacha rates sum to 100%
6. **Pity mechanics**: counter resets, 50/50 system
7. **Date validation**: end > start timestamps
8. **State transitions**: event completion, pity resets

## Running Tests

```bash
# All edge case tests
pytest tests/test_domain_edge_cases_comprehensive.py -v

# Specific test class
pytest tests/test_domain_edge_cases_comprehensive.py::TestBannerEdgeCases -v

# Specific test
pytest tests/test_domain_edge_cases_comprehensive.py::TestBannerEdgeCases::test_banner_drop_rates_must_sum_to_100 -v
```

## Common Validation Errors

### Character
```python
# ❌ Backstory too short
Backstory("Short")
→ ValueError: Backstory must be at least 100 characters

# ❌ Negative stats
Character(..., base_hp=-100)
→ InvariantViolation: Base HP cannot be negative

# ❌ Duplicate abilities
Character(..., abilities=[Ability("Fire"), Ability("Fire")])
→ InvariantViolation: Character cannot have duplicate ability names
```

### Banner
```python
# ❌ Rates don't sum to 100%
Banner(..., ssr_rate=0.6, sr_rate=5.0, r_rate=90.0)
→ InvariantViolation: Drop rates must sum to 100% (got 95.6%)

# ❌ Invalid pity order
Banner(..., soft_pity=90, hard_pity=75)
→ InvariantViolation: Hard pity must be greater than soft pity
```

### Event
```python
# ❌ No participants
Event.create(..., participant_ids=[])
→ InvariantViolation: Event must have at least one participant

# ❌ Duplicate participants
Event.create(..., participant_ids=[EntityId(1), EntityId(1)])
→ InvariantViolation: Event cannot have duplicate participants
```

### Pity
```python
# ❌ Negative counter
Pity(..., pulls_since_last_ssr=-5)
→ InvariantViolation: Pulls since last SSR cannot be negative
```

## Player-Facing Implications

### What Players See
1. **Fair gacha rates**: Always 100% total, never manipulated
2. **Guaranteed pity**: Hard pity at 90 pulls, no exceptions
3. **Honest 50/50**: Guaranteed featured after losing
4. **Valid characters**: All stats positive, backstories complete
5. **Logical events**: Proper dates, valid participants

### What Players Don't See (But System Enforces)
1. **Domain validation**: Automatic checking on all entity creation
2. **Invariant enforcement**: Business rules always satisfied
3. **Edge case coverage**: 35+ tests protect against bugs
4. **Type safety**: Strong typing prevents data corruption
5. **Referential integrity**: EntityId ensures valid references

## Documentation

- **Comprehensive guide**: `docs/DOMAIN_EDGE_CASES.md`
- **Player guarantees**: `docs/PLAYER_GUARANTEES.md`
- **Test suite**: `tests/test_domain_edge_cases_comprehensive.py`
- **Domain verification**: `docs/DATABASE_DOMAIN_VERIFICATION.md`

---

**Quick Reference Last Updated**: 2026-01-18  
**All Tests Passing**: ✅ 35/35
