import random
from collections.abc import Callable
from pydantic import BaseModel, Field
from cdp_agentkit_core.actions.cdp_action import CdpAction

BATTLE_ARENA_PROMPT = """
Welcome to the **NFT Fighting Arena**! ⚔️🔥

Two NFTs enter the battlefield, and only **one** will emerge victorious. 
Fights are determined based on **Attack, Defense, Speed, and HP**, but random events can influence the outcome.

### Combat Rules:
1. **Each turn**, one NFT attacks while the other defends.
2. **Damage Calculation**: 
   - `Damage = Attacker's Attack - Defender's Defense`
   - **Critical Hits** (10% chance) deal **double damage**!
   - **Dodge Mechanic**: If the defender has higher speed, they may **avoid the attack**.
3. **Random Events**:
   - "Your NFT slips and misses the attack!"
   - "The opponent counter-attacks!"
   - "A mysterious force heals your NFT!"

The battle continues until one NFT’s **HP reaches 0**.

### Input:
- **NFT 1 (`nft1_price`)** *(float)* – Price of NFT 1 in USD.
- **NFT 2 (`nft2_price`)** *(float)* – Price of NFT 2 in USD.

### Output:
- **Battle Story (Text-based)** – A narrated fight sequence.
- **Winner** – The NFT that survives.
"""

class BattleArenaInput(BaseModel):
    """
    Schema for simulating an NFT battle.

    Attributes:
        nft1_price (float): Price of NFT 1 in USD.
        nft2_price (float): Price of NFT 2 in USD.
    """

    nft1_price: float = Field(..., description="Price of NFT 1 in USD.")
    nft2_price: float = Field(..., description="Price of NFT 2 in USD.")


def generate_nft_stats(nft_price: float) -> dict:
    """Generate stats based on NFT price with a bit of randomness."""
    
    base_attack = 50
    base_defense = 40
    base_speed = 30
    base_hp = 450

    attack = base_attack + (nft_price * 0.5) + random.randint(-5, 5)  # Small randomness
    defense = base_defense + (nft_price * 0.3) + random.randint(-3, 3)
    speed = base_speed + (nft_price * 0.2) + random.randint(-2, 2)
    hp = base_hp + (nft_price * 0.7) + random.randint(-20, 20)

    return {
        "Attack": round(attack, 2),
        "Defense": round(defense, 2),
        "Speed": round(speed, 2),
        "HP": round(hp, 2)
    }


def battle_arena(nft1_price: float, nft2_price: float) -> dict:
    """Simulate an NFT battle and return the winner along with a battle log."""
    
    nft1 = generate_nft_stats(nft1_price)
    nft2 = generate_nft_stats(nft2_price)

    battle_log = [f"🏆 **NFT Battle Begins!** 🏆"]
    battle_log.append(f"🔹 **NFT 1 Stats:** {nft1}")
    battle_log.append(f"🔸 **NFT 2 Stats:** {nft2}")

    turn = 1
    while nft1["HP"] > 0 and nft2["HP"] > 0:
        attacker, defender = (nft1, nft2) if turn % 2 != 0 else (nft2, nft1)

        battle_log.append(f"\n🎭 **Turn {turn}:** {('NFT 1' if turn % 2 != 0 else 'NFT 2')} attacks!")

        # RNG for special battle events
        event_chance = random.randint(1, 100)
        if event_chance < 10:  # 10% chance to miss attack
            battle_log.append("💨 The attacker **misses the attack** completely!")
            turn += 1
            continue
        elif event_chance > 90:  # 10% chance for counterattack
            battle_log.append("⚡ The defender **counters the attack**, striking back!")
            attacker["HP"] -= max(1, defender["Attack"] - attacker["Defense"])
            turn += 1
            continue

        # Calculate damage
        damage = max(1, attacker["Attack"] - defender["Defense"])
        
        # Critical hit chance
        if random.randint(1, 10) == 1:  # 10% chance
            damage *= 2
            battle_log.append("💥 **CRITICAL HIT!** Damage is doubled!")

        # Dodge chance
        if defender["Speed"] > attacker["Speed"] and random.randint(1, 100) < 15:  # 15% dodge chance
            battle_log.append("🌀 The defender **dodges the attack** effortlessly!")
        else:
            defender["HP"] -= damage
            battle_log.append(f"🔥 The attack hits! **{damage} damage dealt!**")

        # Check for defeat
        if defender["HP"] <= 0:
            battle_log.append(f"\n💀 **NFT {('2' if turn % 2 != 0 else '1')} has fallen!**")
            battle_log.append(f"🏆 **NFT {('1' if turn % 2 != 0 else '2')} wins the battle!**")
            return {
                "battle_log": "\n".join(battle_log),
                "winner": "NFT 1" if turn % 2 != 0 else "NFT 2"
            }

        turn += 1

    return {
        "battle_log": "\n".join(battle_log),
        "winner": "Draw (Unexpected outcome)"
    }


class BattleArenaAction(CdpAction):
    """Action to simulate an NFT battle with dynamic combat events."""

    name: str = "battle_arena"
    description: str = BATTLE_ARENA_PROMPT
    args_schema: type[BaseModel] | None = BattleArenaInput
    func: Callable[..., dict] = battle_arena
