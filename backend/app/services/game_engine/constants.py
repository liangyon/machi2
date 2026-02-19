"""
Game constants and configuration values.
"""

# Combat constants
HEAVY_ATTACK_MULTIPLIER = 1.8
DEFEND_DAMAGE_REDUCTION = 0.5   # 50% damage reduction when defending
EXTRA_ACTION_SPEED_RATIO = 1.5  # player speed must be >= enemy speed * this for extra action
BASE_MANA_REGEN = 5

# Exploration constants
DANGER_PER_ACTION = 7           # danger meter points per normal action
DANGER_EXTRA_PER_OVERACTION = 15  # extra danger per action beyond the pool
ACTION_POOL_BASE = 12           # base exploration actions per floor

# XP curve: XP needed to reach levels 2-10 (index 0 = level 1 threshold)
XP_CURVE = [0, 50, 120, 220, 350, 520, 730, 990, 1300, 1700]