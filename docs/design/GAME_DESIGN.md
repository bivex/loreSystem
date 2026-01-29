# Game Design Document: Dark Fantasy Gacha RPG

> **Vision**: Create a deep gacha RPG with dark atmosphere, where every character has a dramatic story, and player choices affect the fate of the world.

---

## 🎮 CORE GAMEPLAY LOOP

### Daily Session (15-30 minutes):

```
1. Login → Daily Rewards (2 minutes)
   ├── Day 1-7: Escalating rewards
   ├── Streak bonus (consecutive days)
   └── Special reward on Day 7

2. Daily Quests (10 minutes)
   ├── Kill 20 enemies → 50 Gems
   ├── Complete 3 stages → 100 Gems
   └── Use 40 energy → Resource pack

3. Energy Consumption (10-15 minutes)
   ├── Story stages (10 energy each)
   ├── Material farming (15 energy each)
   └── Boss fights (25 energy each)

4. Character Development (5 minutes)
   ├── Level up characters
   ├── Upgrade equipment
   └── Unlock talents

5. Gacha Pull (if currency available)
   ├── Use free daily pull
   ├── Pull with gems
   └── Check collection progress
```

### Weekly Progression:

```
Monday: New weekly quests unlock
Tuesday: Special material dungeon (artifacts)
Wednesday: Double XP event
Thursday: Special material dungeon (ascension)
Friday: Character trial event
Saturday-Sunday: Limited event boss fight

Weekly Boss: Fight once per week for exclusive rewards
Guild War: Weekend competitive event
```

---

## 💰 MONETIZATION DESIGN

### Currencies:

#### 1. Gold (Soft Currency)
- **Source**: Quests, farming stages, selling items
- **Spending**: Character leveling, equipment enhancement, shop purchases
- **Balance**: 1000-5000 per stage, player needs ~50,000 daily at endgame

#### 2. Gems (Hard Currency)
- **Source**: Quests, achievements, dailies, events, purchases
- **Spending**: Gacha pulls, energy refills, premium items
- **Balance**:
  - Free: ~3000 gems/month (10 pulls)
  - Light spender: +6000 gems/month (20 pulls total)
  - Whale: Unlimited

#### 3. Premium Currency (Platinum Coins)
- **Source**: ONLY through fiat purchases
- **Spending**: Exclusive banners, limited skins, season pass
- **Conversion**: $1 = 60 platinum coins

### Gacha System:

#### Standard Banner (Permanent)
```
Pull Cost: 160 Gems (single) | 1600 Gems (10-pull)
Rates:
- SSR (5★): 0.6% (pity at 90 pulls)
- SR (4★): 5.1% (guaranteed every 10 pulls)
- R (3★): 94.3%

Pity System:
- Soft pity: 75+ pulls (rate increases to 6% per pull)
- Hard pity: 90 pulls (guaranteed SSR)
- 50/50 system: First SSR could be off-banner
- Guaranteed featured: After losing 50/50
```

#### Limited Banner (2-3 weeks)
```
Pull Cost: 160 Gems
Rates: Same as standard
Featured Character Rate: 50% (first), 100% (after losing)

Special:
- Weapon banner (75 pity)
- Rerun banners (old limited characters)
```

#### Free Pulls:
```
Daily: 1 free single pull on standard banner
Events: 10-20 free pulls per major event
Achievements: 5-10 pulls for major milestones
```

### In-App Purchases (IAP):

#### Tier 1: Beginner Packs ($0.99 - $4.99)
```
$0.99 First Time Pack:
- 300 Gems
- 100,000 Gold
- 1 Random SR Character

$4.99 Weekly Pack (renewable):
- 300 Gems immediately
- 90 Gems daily for 7 days (total 930)
- Best value for light spenders
```

#### Tier 2: Standard Packs ($9.99 - $49.99)
```
$9.99 Pack:
- 980 Gems (6 pulls)
- 1st time bonus: +980 gems

$24.99 Pack:
- 2580 Gems (16 pulls)
- 1st time bonus: +2580 gems

$49.99 Pack:
- 5480 Gems (34 pulls)
- 1st time bonus: +5480 gems
```

#### Tier 3: Whale Packs ($99.99)
```
$99.99 Pack:
- 12,960 Gems (81 pulls - almost guaranteed SSR)
- 1st time bonus: +12,960 gems
- Bonus: 1 SSR Selector Ticket
```

#### Special Offers:
```
Monthly Card ($4.99):
- 300 Gems immediately
- 90 Gems daily for 30 days (total 3000 gems)
- Best long-term value

Battle Pass ($9.99):
- Free tier: Basic rewards
- Premium tier:
  - 1680 Gems over season
  - 1 guaranteed SR character
  - Exclusive weapon
  - Avatar frame
```

---

## 📊 PROGRESSION SYSTEM

### Player Account Level (1-100):
```
Experience Sources:
- Complete stages: 50-200 XP
- Daily quests: 500 XP total
- Achievements: 1000-5000 XP

Level Rewards:
- Every 5 levels: 160 Gems (1 pull)
- Every 10 levels: 1 SSR Selector Ticket (limited pool)
- Level milestones: Unlock game features
  - Level 10: Co-op unlocked
  - Level 20: Guild system
  - Level 30: PvP arena
  - Level 50: Endgame content
```

### Character Progression:

#### Level (1-100)
```
Required Resources:
- Character XP books (obtained from farming)
- Gold

Power Curve:
- Level 1: ~100 Base ATK
- Level 50: ~500 Base ATK
- Level 80: ~1000 Base ATK
- Level 100: ~1500 Base ATK
```

#### Ascension (0-6 phases)
```
Breaks level cap:
- Phase 0: Level 1-20
- Phase 1: Level 20-40
- Phase 2: Level 40-50
- Phase 3: Level 50-60
- Phase 4: Level 60-70
- Phase 5: Level 70-80
- Phase 6: Level 80-100

Required Materials:
- Common materials (farmable)
- Elite materials (daily dungeons)
- Boss materials (weekly boss)
- Elemental crystals (event rewards)

Stat Boost per Phase: +5-10% to all stats
```

#### Talents (Skills)
```
3 Talents per character:
- Normal Attack (level 1-15)
- Elemental Skill (level 1-15)
- Ultimate Burst (level 1-15)

Required Resources:
- Talent books (daily dungeons, specific day)
- Boss materials
- Gold

Upgrade Impact:
- Damage: +5-10% per level
- Cooldown reduction: -1s at certain levels
- New effects: At levels 6, 9, 12
```

#### Equipment Enhancement (0-15)
```
Enhancement Levels:
- +0 to +5: Common materials
- +6 to +10: Uncommon materials
- +11 to +15: Rare materials + Gold

Stat Increase:
- +1: +4% stats
- +5: +20% stats + Unlock substat
- +10: +40% stats + Enhance substat
- +15: +75% stats + Maximize substat

Failure Rate:
- +0 to +10: 100% success
- +11 to +12: 90% success
- +13 to +14: 50% success
- +15: 30% success (can use protection items)
```

#### Constellations (Duplicates)
```
Pull duplicate = 1 constellation point
Max: 6 constellations

Effects:
- C1: Improve basic ability
- C2: Reduce skill cooldown
- C3: +3 levels to Normal Attack
- C4: New passive effect
- C5: +3 levels to Ultimate
- C6: Game-changing mechanic

Whale Protection:
- Can buy constellations with special currency
- 1 constellation = $30 or 6 months farming
```

---

## 🎭 CHARACTER DESIGN

### Rarity Distribution:

#### SSR (5★) - 0.6% rate
```
Total Pool: 20-30 characters
Power Level: 9-10/10
Usage Rate Target: 80% at endgame

Design:
- Complex backstory (300+ words)
- 3 unique abilities with visuals
- 2-3 relationships with other SSR
- Faction leader or key figure
- Voice acted (premium)
```

#### SR (4★) - 5.1% rate
```
Total Pool: 40-50 characters
Power Level: 6-8/10
Usage Rate Target: 50% for specific content

Design:
- Solid backstory (200+ words)
- 3 abilities with effects
- 1-2 relationships
- Faction member
- Partially voice acted
```

#### R (3★) - 94.3% rate
```
Total Pool: 30-40 characters
Power Level: 4-6/10
Usage Rate: Early game + collection

Design:
- Basic backstory (100+ words)
- 2-3 abilities
- 1 relationship
- Common NPC or recruit
- Text only
```

### Character Stats:

```
Base Stats:
- HP: 2000-8000 (tanks higher)
- ATK: 200-800 (DPS higher)
- DEF: 100-500 (tanks higher)
- SPD: 80-120 (assassins higher)
- CRIT Rate: 5-15%
- CRIT DMG: 150-200%

Derived Stats (from equipment):
- Elemental Mastery
- Energy Recharge
- Healing Bonus
- Damage Bonus (by element)
```

### Character Roles:

```
DPS (Damage Dealer):
- High ATK, moderate HP
- Focus: Deal maximum damage
- Examples: Lira, Aria

Tank:
- High HP, high DEF
- Focus: Absorb damage, protect team
- Examples: Viktor

Healer:
- Moderate HP, low ATK
- Focus: Restore team HP
- Examples: Eliza (hybrid)

Support:
- Balanced stats
- Focus: Buffs, debuffs, crowd control
- Examples: Valorian
```

### Element System:

```
Elements: 7 types
- Fire: High damage, burning DoT
- Water: Healing, cleansing
- Earth: Defense, shields
- Wind: Speed, mobility
- Lightning: Burst damage, stun
- Light: Healing, purification
- Dark: Damage over time, life steal

Reactions:
- Fire + Wind = Amplified damage (+50%)
- Water + Lightning = Electrocuted (AoE damage)
- Earth + Light = Shield + Regen
- Dark + Fire = Cursed Flames (DoT + reduced healing)
```

---

## 🗺️ CONTENT STRUCTURE

### Story Mode (Main Story):

```
Chapters: 12 (at launch) → 20+ (over 2 years)
Stages per Chapter: 8-10 stages

Chapter 1: "Awakening in Darkness"
├── Stage 1-1: Tutorial (free, no energy)
├── Stage 1-2 to 1-8: Normal stages (10 energy each)
└── Stage 1-9: Boss stage (15 energy)

Rewards per Chapter:
- 800 Gems (first clear)
- 1 SR Character Selector
- Gold, XP books, materials

Energy Cost: 10-25 per stage
First Clear Bonus: 2x rewards
3-Star Clear Bonus: 40 gems
```

### Daily Dungeons:

```
Monday/Thursday: Talent Books (Fire, Water, Earth)
Tuesday/Friday: Talent Books (Wind, Lightning, Light/Dark)
Wednesday/Saturday: Weapon Enhancement Materials
Sunday: Gold farming (2x gold)

Energy Cost: 15 per run
Rewards: 5-10 materials per run
Daily Limit: 3 runs per dungeon
```

### Weekly Boss:

```
Bosses: 3 rotating bosses
Energy Cost: 0 (but limited to 1 kill per week)
Difficulty: Normal, Hard, Expert

Rewards:
- Character ascension materials (exclusive)
- Talent materials
- 200 Gems (first clear)
- Chance for SSR artifact
```

### Events (Rotating):

#### Type 1: Character Trial Event (2 weeks)
```
Try featured SSR character
- Complete challenges for rewards
- Rewards: Gems, materials, character insights
- Motivation: "Try before you pull"
```

#### Type 2: Limited Boss Event (1 week)
```
Fight special boss for exclusive rewards
- Solo or Co-op
- Leaderboard for top damage
- Rewards:
  - Top 100: SSR Selector Ticket
  - Top 1000: 1600 Gems (10 pulls)
  - All participants: Event currency for shop
```

#### Type 3: Story Event (3 weeks)
```
Limited story chapters
- New lore and characters
- Exclusive rewards
- Can be replayed later (but rewards only once)
```

---

## 🏆 RETENTION MECHANICS

### Daily Engagement (15-30 minutes):

```
1. Daily Login (2 min)
   - Day 1: 60 Gems
   - Day 7: 300 Gems + 1 Pull Ticket
   - Day 30: 1 SSR Selector Ticket

2. Daily Quests (10 min)
   - Always achievable in one session
   - Clear visual progress bars
   - Instant dopamine hit

3. Energy Management (15 min)
   - Max energy: 120 (refills 1 per 8 minutes)
   - 1 full refill per day (takes 16 hours)
   - Push notification when full
```

### Weekly Goals:

```
Weekly Quests:
- Complete 10 daily quests: 500 Gems
- Spend 500 energy: 300 Gems
- Clear weekly boss: 200 Gems
- Participate in events: 400 Gems
Total: 1400 Gems/week (almost 10 pulls/month)

Weekly Boss:
- Can only fight once
- Resets Monday 00:00 UTC
- Push notification on Sunday if not completed
```

### Monthly Goals:

```
Monthly Card:
- For $4.99, gives 3000 gems over 30 days
- Must login daily to claim
- Creates strong daily habit

Battle Pass:
- 50 tier progression over 6 weeks
- Tier up by playing any content
- Visual progress bar = dopamine
- Premium tier has exclusive rewards
```

### Long-term Goals:

```
Collection Milestones:
- Collect 10 SSR: 1600 Gems
- Collect 50 characters total: SSR Selector
- Max out 5 characters: Exclusive title

Achievement System:
- 500+ achievements
- Categories: Story, Combat, Collection, Social
- Some achievements take months (long-term goals)
```

---

## 👥 SOCIAL SYSTEMS

### Guild System (Level 20+):

```
Guild Size: 30 members max

Guild Benefits:
- Guild shop (exclusive items)
- Guild bonuses (+10% gold, +5% XP)
- Guild quests (cooperative goals)
- Guild chat

Guild Activities:
- Weekly Guild Boss (defeat together)
- Guild War (vs other guilds, weekend)
- Guild donations (contribute resources)

Guild Ranks:
- Master (1): Full control
- Officers (5): Manage members
- Members (24): Participate
```

### Friend System:

```
Friend Limit: 50 friends

Friend Benefits:
- Send/receive friend points daily
- Use friend's support character
- Co-op content easier with friends

Friend Points Shop:
- Low-tier materials
- Small gem packs
- Common characters
```

### Co-op Raids (Level 10+):

```
2-4 players cooperative bosses
Energy Cost: 25 per player
Rewards:
- Shared loot pool
- Bonus for playing with friends
- Leaderboard for fastest clears

Communication:
- Quick chat (emotes, pre-set phrases)
- No toxic chat possible
```

### Leaderboards:

```
Categories:
- Story progression (Chapter cleared)
- Arena ranking (PvP)
- Boss damage (weekly boss)
- Collection count

Rewards:
- Top 10: Special title + 1000 Gems
- Top 100: 500 Gems
- Top 1000: 200 Gems
- All: Participation rewards
```

---

## ⚔️ COMBAT SYSTEM

### Team Composition:

```
Team Size: 4 characters
Formation Positions:
- Front Row (2): Takes more damage
- Back Row (2): Takes less damage, harder to target

Team Building:
- Element synergy important
- Role balance (1-2 DPS, 1 Tank, 1 Support/Healer)
- Character relationships = bonus stats
```

### Battle Flow:

```
Turn-Based Combat:
- Turn order: Based on SPD stat
- Each character acts in order
- Actions: Attack, Skill, Ultimate, Item, Defend

Action Points (AP):
- Each character has max 3 AP per turn
- Normal Attack: 1 AP
- Skill: 2 AP
- Ultimate: 3 AP (requires full energy bar)

Energy System:
- Energy bar: 0-100
- Gain energy: +20 per normal attack, +10 when hit
- Spend energy: Ultimate costs 80-100 energy
```

### Combat Mechanics:

```
Damage Formula:
Base Damage = ATK * Skill Multiplier
Critical = Base Damage * CRIT DMG (if crit)
Defense Reduction = Final Damage / (DEF + 100)
Element Bonus = +50% if advantage

Status Effects:
- Burn: DoT (5% max HP per turn)
- Freeze: Skip turn (1 turn)
- Stun: Cannot act (1 turn)
- Poison: DoT (3% max HP per turn, stackable)
- Shield: Absorb damage (HP amount)
- Buff: +ATK/DEF/SPD (%)
- Debuff: -ATK/DEF/SPD (%)
```

### Auto-Battle:

```
Unlocked: After clearing stage once manually
AI Behavior:
- Use skills on cooldown
- Prioritize ultimates
- Target lowest HP enemy (DPS)
- Protect lowest HP ally (healer)

Speed Options:
- 1x: Normal speed
- 2x: Double speed (unlocked at level 20)
- 3x: Triple speed (unlocked at level 50)
```

---

## 🎨 UI/UX FLOW

### Onboarding (First 10 minutes):

```
Step 1: Opening Cutscene (1 min)
- Dark, atmospheric intro
- Hook: "The world is dying, only you can save it"

Step 2: Tutorial Combat (3 min)
- Simple 3-stage combat tutorial
- Teach: Attack, Skill, Ultimate
- Give: 1 SR character as tutorial reward

Step 3: First Gacha Pull (2 min)
- 10-pull guaranteed SR
- Explain gacha system
- Celebrate: Big animations, voice lines

Step 4: Character Customization (1 min)
- Choose player name
- Pick favorite element
- Set avatar

Step 5: Story Hook (3 min)
- Chapter 1-1 (free, no energy cost)
- Introduce main antagonist
- Reward: 300 Gems + Energy refill
```

### Main Menu Structure:

```
Bottom Nav Bar:
├── Home: Daily quests, news, events
├── Story: Chapter selection
├── Characters: Team management, upgrades
├── Shop: Gem packs, bundles, refresh
└── Profile: Settings, friends, guild

Top Bar:
├── Player Info: Level, XP progress
├── Currencies: Gold, Gems, Premium
└── Energy: Current/Max, refill timer

Quick Access:
├── Gacha Button: Always visible, pulsing when pull available
├── Inbox: Collect rewards
└── Settings: Sound, notifications, account
```

### Screen Flow (User Journey):

```
New Player Journey:
Login → Tutorial → First Pull → Story Mode → Daily Quests → Logout

Daily Player Journey:
Login → Collect dailies → Auto-farm stages → Do daily quests
→ Check events → Pull if possible → Upgrade characters → Logout

Engaged Player Journey:
Login → Collect rewards → Farm materials (auto)
→ Try new team comp → Guild activities → Events
→ Check leaderboards → Co-op with friends → Logout

Whale Journey:
Login → Check shop for new packs → Purchase → Pull on banner
→ Max new character → Push leaderboards → Guild activities → Logout
```

---

## 📈 MONETIZATION PSYCHOLOGY

### FOMO (Fear of Missing Out):

```
Limited Banners:
- "Only 14 days left!"
- Countdown timer always visible
- Limited character = status symbol

Daily Deals:
- "Today only: 50% bonus gems"
- Refresh at midnight UTC
- Push notification at reset

Event Rewards:
- "Complete event for exclusive skin"
- "Top 100 get SSR ticket"
- Leaderboards create competition
```

### Sunk Cost Fallacy:

```
Pity Counter:
- Show progress: "72/90 pulls until guaranteed SSR"
- Player thinks: "I'm so close, just need 18 more pulls"
- Buy gems to complete pity

Battle Pass:
- Player progresses to tier 40/50
- Think: "I'm so close to finishing, should buy premium"
- Buy pass to not "waste" free progress

Character Investment:
- Player levels character to 80
- Need rare materials for level 100
- Already invested so much, buy resource pack
```

### Social Proof:

```
Guild System:
- See other members' progress
- Want to keep up
- Buy to stay relevant

Leaderboards:
- Top players have maxed SSR
- Want same status
- Pull more to compete

Friend Support:
- Friend has new SSR with strong abilities
- Want same character to help back
- Pull on banner
```

### Reward Schedules:

```
Variable Ratio (Gacha):
- Don't know when SSR will come
- Most addictive schedule type
- "Just one more pull"

Fixed Interval (Daily Login):
- Predictable rewards
- Creates habit
- Come back every day

Variable Interval (Events):
- Random timing of good events
- Keep checking game
- Don't want to miss out
```

---

## 🎯 KPI TARGETS

### Retention:
```
D1: 45-50%
D7: 20-25%
D30: 8-12%
```

### Monetization:
```
ARPU: $5-8
ARPPU: $50-80
Conversion: 4-6%
Whale Conversion (>$100): 0.5-1%
```

### Engagement:
```
Session Length: 15-25 minutes
Sessions per Day: 3-5
Daily Active Users (DAU): 50% of installs
Monthly Active Users (MAU): 30% of installs
```

### Gacha:
```
Avg Pulls per Player: 30/month (free players)
Avg Pulls per Spender: 100-200/month
Banner Conversion: 15-20% try new banner
```

---

## 🚀 LAUNCH PLAN

### Soft Launch (Month 1):
```
Content:
- 6 chapters
- 15 SSR characters
- 30 SR characters
- 3 events

Goals:
- Test monetization
- Balance progression
- Fix critical bugs
- Gather feedback
```

### Global Launch (Month 2-3):
```
Content:
- 10 chapters
- 20 SSR characters
- 40 SR characters
- 5 events
- Guild system
- PvP arena

Marketing:
- Social media campaign
- Influencer partnerships
- Launch event (double rewards)
- Special launch banner (limited SSR)
```

### Post-Launch (Monthly):
```
New Content Every Month:
- 2 new SSR characters
- 1 new chapter
- 2-3 events
- 1 rerun banner
- Balance patches

Seasonal Events:
- Summer event (beach theme)
- Halloween event (spooky)
- Christmas event (snowy)
- Anniversary (big rewards)
```

---

## ✅ SUCCESS CRITERIA

### Technical:
- [ ] All entities have game value (stats, rewards, etc.)
- [ ] All characters have 2+ relationships
- [ ] All events have consequences
- [ ] Economy is balanced (no infinite loops)
- [ ] Progression curve is smooth (no walls)

### Business:
- [ ] D7 retention > 20%
- [ ] ARPU > $5
- [ ] Conversion > 4%
- [ ] Session length > 15 minutes
- [ ] Positive user reviews (>4.0 rating)

### Creative:
- [ ] Lore depth score > 8/10
- [ ] Player engagement with story > 60%
- [ ] Character popularity spread (no dead characters)
- [ ] World feels cohesive and interconnected

---

**Document Version**: 1.0  
**Date**: 2026-01-18  
**Author**: Game Design Expert  
**Status**: Ready for Implementation
