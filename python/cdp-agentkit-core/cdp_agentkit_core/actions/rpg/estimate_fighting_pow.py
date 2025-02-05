from collections.abc import Callable
from pydantic import BaseModel, Field

from cdp_agentkit_core.actions.cdp_action import CdpAction

ESTIMATE_NFT_FIGHTING_POWER_PROMPT = """
Estimate the fighting power attributes of an NFT based on its market price (USD).

    Input:
        - NFT Price (`nft_price`) (float) – The price of the NFT in USD.

    Output:
        - Attack (`float`) – The offensive power of the NFT.
        - Defense (`float`) – The resistance/durability of the NFT.
        - Speed (`float`) – The agility of the NFT.

    Important Notes:
        The attributes are **dynamically scaled** based on the NFT price using the following calculations
        - Attack = `50 + (nft_price * 0.5)`
        - Defense = `40 + (nft_price * 0.3)`
        - Speed = `30 + (nft_price * 0.2)`
        - HP = `450 + (nft_price * 0.7)`

    This function provides a **game-like evaluation** of NFT fighting power.
"""

class EstimateNFTFightPowerInput(BaseModel):
    """
    Schema for estimating NFT fighting power.

    Attributes:
        nft_price (float): The price of the NFT in USD.
    """

    nft_price: float = Field(
        ...,
        description="The price of the NFT in USD.",
    )


def estimate_fighting_pow(nft_price: float) -> dict:
    """
    Estimate the fighting power attributes of an NFT based on its price.

    Args:
        nft_price (float): The price of the NFT in USD.

    Returns:
        dict: Estimated fighting power attributes (Attack, Defense, Speed).

    Raises:
        ValueError: If the NFT price is invalid (negative or zero).
    """
    if nft_price <= 0:
        raise ValueError("NFT price must be greater than zero.")

    # Base attributes
    base_attack = 50
    base_defense = 40
    base_speed = 30

    # Scaling calculations
    attack = base_attack + (nft_price * 0.5)
    defense = base_defense + (nft_price * 0.3)
    speed = base_speed + (nft_price * 0.2)

    return {
        "Attack": round(attack, 2),
        "Defense": round(defense, 2),
        "Speed": round(speed, 2),
    }


class EstimateNFTFightPowerAction(CdpAction):
    """Action to estimate NFT fighting power attributes."""

    name: str = "estimate_fighting_pow"
    description: str = ESTIMATE_NFT_FIGHTING_POWER_PROMPT
    args_schema: type[BaseModel] | None = EstimateNFTFightPowerInput
    func: Callable[..., dict] = estimate_fighting_pow
