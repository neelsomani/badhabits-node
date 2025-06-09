"""
Setup script for Bad Habits Tracking Node.
Handles environment variables, database setup, and node configuration.
"""
import os
import sys
from loguru import logger

from nodetools.cli import setup_node as nodetools_setup
from nodetools.configuration.configuration import NodeConfig, RuntimeConfig
from nodetools.configuration.constants import NetworkType

def setup_badhabits_node():
    """Setup the Bad Habits Tracking Node"""
    try:
        # Get required environment variables
        required_vars = [
            'NODE_NAME',           # Node identifier
            'PFT_XRP_WALLET',      # Node's XRP wallet address
            'DATABASE_URL',        # PostgreSQL connection string
            'OPENAI_API_KEY',      # For AI responses
            'ENCRYPTION_PASSWORD'  # For secure storage
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Set up node configuration
        node_config = NodeConfig(
            node_name=os.getenv('NODE_NAME'),
            network=NetworkType('mainnet'),
            node_address=os.getenv('PFT_XRP_WALLET'),
            encryption_password=os.getenv('ENCRYPTION_PASSWORD')
        )

        # Set up runtime configuration
        runtime_config = RuntimeConfig(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            postgres_conn_string=os.getenv('DATABASE_URL')
        )

        # Run nodetools setup
        nodetools_setup(
            node_config=node_config,
            runtime_config=runtime_config,
            auto=True
        )

        logger.info("Bad Habits Tracking Node setup complete!")
        return True

    except Exception as e:
        logger.error(f"Error setting up Bad Habits Tracking Node: {e}")
        return False

if __name__ == "__main__":
    if not setup_badhabits_node():
        sys.exit(1) 