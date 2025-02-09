from collections.abc import Callable
from pydantic import BaseModel, Field
import requests

from cdp_agentkit_core.actions import CdpAction

GET_NFT_PRICE_PROMPT = """
This tool retrieves the current market price of an NFT on the Ethereum blockchain, denominated in HUSD.
It takes the NFT's unique identifier (contract address or token ID) as input and queries the Coins.Llama.fi API for real-time price data.
"""


class GetNFTPriceInput(BaseModel):
    """Input argument schema for retrieving NFT price."""

    nft_id: str = Field(
        ..., description="The unique identifier (contract address or token ID) of the NFT."
    )


def get_nft_price(nft_id: str) -> float:
    """Fetch the current market price of an NFT in HUSD.

    Args:
        nft_id (str): The unique identifier (contract address or token ID) of the NFT.

    Returns:
        float: The latest market price of the NFT in HUSD.

    Raises:
        ValueError: If no price data is found for the given NFT.
        requests.RequestException: If the API request fails.
    """
    url = f"https://coins.llama.fi/prices/current/ethereum:{nft_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        key = f"ethereum:{nft_id}"
        if "coins" in data and key in data["coins"] and "price" in data["coins"][key]:
            return float(data["coins"][key]["price"])

        raise ValueError(f"No price feed found for NFT: {nft_id}")

    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to retrieve NFT price: {e}") from e


class GetNFTPriceAction(CdpAction):
    """Fetch the current market price of an NFT."""

    name: str = "get_nft_price"
    description: str = GET_NFT_PRICE_PROMPT
    args_schema: type[BaseModel] | None = GetNFTPriceInput
    func: Callable[..., float] = get_nft_price
