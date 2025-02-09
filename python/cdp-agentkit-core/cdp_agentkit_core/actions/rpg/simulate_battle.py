import random
from collections.abc import Callable
from pydantic import BaseModel, Field
from cdp_agentkit_core.actions.cdp_action import CdpAction

SIMULATION_BATTLE_PROMPT = """
This tool simulates a battle between two NFTs based on their price or randomly generated stats.
It takes the price of two NFTs as inputs and generates attributes such as attack, defense, speed, and HP.
The battle proceeds turn by turn until one NFT is defeated.

If prices are not provided, random values will be assigned to the NFTs.
"""


class SimulationBattleInput(BaseModel):
    """Input argument schema for simulating an NFT battle."""

    nft1_price: float = Field(
        ..., description="The price of NFT 1 in USD."
    )
    nft2_price: float = Field(
        ..., description="The price of NFT 2 in USD."
    )


def generate_nft_stats(nft_price: float) -> dict:
    """Generate stats based on NFT price with a small random variance."""
    
    base_attack = 50
    base_defense = 40
    base_speed = 30
    base_hp = 450

    attack = base_attack + (nft_price * 0.5) + random.randint(-5, 5)
    defense = base_defense + (nft_price * 0.3) + random.randint(-3, 3)
    speed = base_speed + (nft_price * 0.2) + random.randint(-2, 2)
    hp = base_hp + (nft_price * 0.7) + random.randint(-20, 20)

    return {
        "Attack": round(attack, 2),
        "Defense": round(defense, 2),
        "Speed": round(speed, 2),
        "HP": round(hp, 2),
    }


def simulate_battle(nft1_price: float, nft2_price: float) -> str:
    """Simulate an NFT battle and return the battle log."""
    
    nft1 = generate_nft_stats(nft1_price)
    nft2 = generate_nft_stats(nft2_price)

    battle_log = [f"🏆 **NFT Battle Begins!** 🏆"]
    battle_log.append(f"🔹 **NFT 1 Stats:** {nft1}")
    battle_log.append(f"🔸 **NFT 2 Stats:** {nft2}")

    turn = 1
    while nft1["HP"] > 0 and nft2["HP"] > 0:
        attacker, defender = (nft1, nft2) if turn % 2 != 0 else (nft2, nft1)
        battle_log.append(f"\n🎭 **Turn {turn}:** {('NFT 1' if turn % 2 != 0 else 'NFT 2')} attacks!")

        # RNG for special events
        event_chance = random.randint(1, 100)
        if event_chance < 10:
            battle_log.append("💨 The attacker **misses the attack** completely!")
            turn += 1
            continue
        elif event_chance > 90:
            battle_log.append("⚡ The defender **counters the attack**, striking back!")
            attacker["HP"] -= max(1, defender["Attack"] - attacker["Defense"])
            turn += 1
            continue

        # Calculate damage
        damage = max(1, attacker["Attack"] - defender["Defense"])

        # Critical hit
        if random.randint(1, 10) == 1:
            damage *= 2
            battle_log.append("💥 **CRITICAL HIT!**")

        # Dodge chance
        if defender["Speed"] > attacker["Speed"] and random.randint(1, 100) < 15:
            battle_log.append("🌀 The defender **dodges the attack** effortlessly!")
        else:
            defender["HP"] -= damage
            battle_log.append(f"🔥 The attack hits! **{damage} damage dealt!**")

        # Check for defeat
        if defender["HP"] <= 0:
            battle_log.append(f"\n💀 **NFT {('2' if turn % 2 != 0 else '1')} has fallen!**")
            battle_log.append(f"🏆 **NFT {('1' if turn % 2 != 0 else '2')} wins the battle!**")
            return "\n".join(battle_log)

        turn += 1

    return "\n".join(battle_log)


class SimulationBattleAction(CdpAction):
    """Simulate an NFT battle action."""

    name: str = "simulate_battle"
    description: str = SIMULATION_BATTLE_PROMPT
    args_schema: type[BaseModel] | None = SimulationBattleInput
    func: Callable[..., str] = simulate_battle
