"""
Setup script for Bad Habits Tracking Node.
Handles environment variables, database setup, and node configuration.

Note: This node uses encryption for health data (messages starting with WHISPER__),
but uses the node's main wallet for encryption/decryption rather than a separate remembrancer wallet.
This is sufficient since we only need to handle encrypted messages between the node and users.
"""
import os
import sys
import json
from loguru import logger
import xrpl

from nodetools.configuration.configuration import RuntimeConfig
from nodetools.utilities.credentials import CredentialManager, get_credentials_directory


def setup_node_auto_no_remembrancer():
    """Modified version of nodetools.utilities.setup_utilities.setup_node_auto that handles optional remembrancer.
    Note: We don't use a remembrancer wallet since we handle encryption with the node's main wallet.
    """
    network = os.environ['NETWORK']
    node_name = os.environ['NODE_NAME']
    network_suffix = '_testnet' if network == 'testnet' else ''
    encryption_password = os.environ['ENCRYPTION_PASSWORD']
    
    # Create credentials dictionary
    credentials_dict = {
        f'{node_name}{network_suffix}_postgresconnstring': os.environ['PG_CONN_STRING'],
        f'{node_name}{network_suffix}__v1xrpsecret': os.environ['PFT_XRP_WALLET'],  # Used for both transactions and message encryption
        'openrouter': os.environ['OPENROUTER_API_KEY'],
        'openai': os.environ['OPENAI_API_KEY'],
        'anthropic': os.environ['ANTHROPIC_API_KEY'],
        f'discordbot{network_suffix}_secret': os.environ['DISCORD_BOT_TOKEN'],
    }

    # Create config dictionary
    config = {
        'node_name': f"{node_name}{network_suffix}",
        'auto_handshake_addresses': [],
        'discord_guild_id': os.environ['DISCORD_GUILD_ID'],
        'discord_activity_channel_id': int(os.environ['DISCORD_ACTIVITY_CHANNEL_ID']),
    }

    # Set up node address from main wallet
    node_wallet = xrpl.wallet.Wallet.from_seed(credentials_dict[f'{node_name}{network_suffix}__v1xrpsecret'])
    config['node_address'] = node_wallet.classic_address

    # Save node configuration
    config_dir = get_credentials_directory()
    config_file = config_dir / f"pft_node_{'testnet' if network == 'testnet' else 'mainnet'}_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    # Store credentials
    cm: CredentialManager = CredentialManager(encryption_password)
    cm.enter_and_encrypt_credential(credentials_dict)

def setup_badhabits_node():
    """Setup the Bad Habits Tracking Node"""
    try:
        # Get required environment variables
        required_vars = [
            'NODE_NAME',
            'PFT_XRP_SECRET',
            'DATABASE_URL',
            'OPENAI_API_KEY',
            'ENCRYPTION_PASSWORD'
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Set up environment variables for nodetools auto setup
        os.environ['NETWORK'] = 'testnet' if os.getenv('USE_TESTNET', 'false').lower() == 'true' else 'mainnet'
        os.environ['PG_CONN_STRING'] = os.getenv('DATABASE_URL')
        os.environ['PFT_XRP_WALLET'] = os.getenv('PFT_XRP_SECRET')

        # Set empty values for optional API keys
        os.environ['OPENROUTER_API_KEY'] = ''
        os.environ['ANTHROPIC_API_KEY'] = ''
        os.environ['DISCORD_BOT_TOKEN'] = ''
        os.environ['DISCORD_GUILD_ID'] = '0'
        os.environ['DISCORD_ACTIVITY_CHANNEL_ID'] = '0'

        # Configure network settings
        RuntimeConfig.USE_TESTNET = os.getenv('USE_TESTNET', 'false').lower() == 'true'
        RuntimeConfig.HAS_LOCAL_NODE = os.getenv('HAS_LOCAL_NODE', 'false').lower() == 'true'
        RuntimeConfig.USE_OPENROUTER_AUTOROUTER = False  # Disable OpenRouter requirement

        # Run our modified setup_node_auto
        setup_node_auto_no_remembrancer()

        logger.info("Bad Habits Tracking Node setup complete!")
        return True

    except Exception as e:
        logger.error(f"Error setting up Bad Habits Tracking Node: {e}")
        return False

if __name__ == "__main__":
    if not setup_badhabits_node():
        sys.exit(1) 