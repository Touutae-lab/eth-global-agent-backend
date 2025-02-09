from collections.abc import Callable
from pydantic import BaseModel, Field

from cdp_agentkit_core.actions.cdp_action import CdpAction

ESTIMATE_NFT_FIGHTING_POWER_PROMPT = """
This tool estimates the fighting power attributes of an NFT based on its market price (USD).
It takes the NFT price as input and dynamically calculates attack, defense, speed, and HP based on predefined scaling formulas.
"""


class EstimateNFTFightPowerInput(BaseModel):
    """Input argument schema for estimating NFT fighting power."""

    nft_price: float = Field(
        ..., description="The price of the NFT in USD."
    )


def estimate_fighting_pow(nft_price: float) -> dict:
    """Estimate the fighting power attributes of an NFT based on its price.

    Args:
        nft_price (float): The price of the NFT in USD.

    Returns:
        dict: Estimated fighting power attributes (Attack, Defense, Speed, HP).

    Raises:
        ValueError: If the NFT price is invalid (negative or zero).
    """
    if nft_price <= 0:
        raise ValueError("NFT price must be greater than zero.")

    # Base attributes
    base_attack = 50
    base_defense = 40
    base_speed = 30
    base_hp = 450

    # Scaling calculations
    attack = base_attack + (nft_price * 0.5)
    defense = base_defense + (nft_price * 0.3)
    speed = base_speed + (nft_price * 0.2)
    hp = base_hp + (nft_price * 0.7)

    return {
        "Attack": round(attack, 2),
        "Defense": round(defense, 2),
        "Speed": round(speed, 2),
        "HP": round(hp, 2),
    }


class EstimateNFTFightPowerAction(CdpAction):
    """Estimate NFT fighting power attributes."""

    name: str = "estimate_fighting_pow"
    description: str = ESTIMATE_NFT_FIGHTING_POWER_PROMPT
    args_schema: type[BaseModel] | None = EstimateNFTFightPowerInput
    func: Callable[..., dict] = estimate_fighting_pow
