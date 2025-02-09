from unittest.mock import patch

import pytest
import requests

from cdp_agentkit_core.actions.rpg.get_nft_price import GetNFTPriceInput, get_nft_price

MOCK_ID = "0xdF574c24545E5FfEcb9a659c229253D4111d87e1"


def test_get_nft_price_input_model_valid():
    """Test GetNftPriceInput accepts valid parameters."""
    valid_input = GetNFTPriceInput(
        nft_id=MOCK_ID,
    )
    assert valid_input.nft_id == MOCK_ID


def test_get_nft_price_input_model_missing_params():
    """Test GetNftPriceInput raises error when params are missing."""
    with pytest.raises(ValueError):
        GetNFTPriceInput()


def test_get_nft_price_success():
    """Test successful NFT price fetch with valid parameters."""
    mock_response = {
        "coins": {
            f"ethereum:{MOCK_ID}": {
                "decimals": 8,
                "symbol": "HUSD",
                "price": 0.02678196,
                "timestamp": 1738767037,
                "confidence": 0.99,
            }
        }
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        result = get_nft_price(MOCK_ID)

        assert result == 0.02678196


def test_get_nft_price_http_error():
    """Test NFT price fetch error with HTTP error."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error: Not Found"
        )

        with pytest.raises(requests.exceptions.HTTPError):
            get_nft_price(MOCK_ID)
