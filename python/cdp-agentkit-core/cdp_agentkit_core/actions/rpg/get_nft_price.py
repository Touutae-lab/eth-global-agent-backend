from collections.abc import Callable
from pydantic import BaseModel, Field
import requests

from cdp_agentkit_core.actions.cdp_action import CdpAction


GET_NFT_PRICE_PROMPT = """
Get the current market price of an NFT on the Ethereum blockchain, denominated in HUSD.

    Input:
        - **NFT ID (`nft_id`)** – The unique identifier (contract address or token ID) of the NFT.

    Output:
        - **Price (`float`)** – The latest market price of the NFT in HUSD.

This function queries the Coins.Llama.fi API for real-time NFT price data.
"""


class GetNFTPriceInput(BaseModel):
    """
    Schema for retrieving NFT price.

    Attributes:
        nft_id (str): The unique identifier of the NFT (contract address or token ID).
    """

    nft_id: str = Field(
        ...,
        description="The ID of the NFT to retrieve the price for.",
    )


def get_nft_price(nft_id: str) -> float:
    """
    Fetch the current market price of an NFT in HUSD.

    Args:
        nft_id (str): The unique identifier (contract address or token ID) of the NFT.

    Returns:
        float: The current market price of the NFT in HUSD.

    Raises:
        ValueError: If no price data is found for the given NFT.
        requests.HTTPError: If the API request fails.
    """
    url = f"https://coins.llama.fi/prices/current/ethereum:{nft_id}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if the request fails
    data = response.json()

    # Ensure expected structure exists in response
    key = f"ethereum:{nft_id}"
    if "coins" not in data or key not in data["coins"] or "price" not in data["coins"][key]:
        raise ValueError(f"No price feed found for NFT: {nft_id}")

    return float(data["coins"][key]["price"])


class GetNFTPriceAction(CdpAction):
    """Action to fetch NFT price from market data."""

    name: str = "get_nft_price"
    description: str = GET_NFT_PRICE_PROMPT
    args_schema: type[BaseModel] | None = GetNFTPriceInput
    func: Callable[..., float] = get_nft_price
