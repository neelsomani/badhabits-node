"""
Command line interface for the Bad Habits Tracking Node.
"""
import os
import sys
import asyncio
import argparse
from loguru import logger
from dotenv import load_dotenv

from nodetools.container.service_container import ServiceContainer
from badhabits.node.process_memos import BadHabitsRules
from badhabits.setup_node import setup_badhabits_node

load_dotenv()

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Bad Habits Tracking Node')
    parser.add_argument('--setup', action='store_true', help='Run node setup')
    return parser.parse_args()

async def main():
    """Main entry point for the Bad Habits Tracking Node"""
    try:
        args = parse_args()

        # Run setup if requested
        if args.setup:
            if not setup_badhabits_node():
                sys.exit(1)
            return

        # Initialize the service container
        container = ServiceContainer.initialize(
            business_logic=BadHabitsRules.create(),
            notifications=True
        )
        
        # Start the node
        container.start()
        
        # Keep the node running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down Bad Habits Tracking Node...")
        if 'container' in locals():
            container.stop()
    except Exception as e:
        logger.error(f"Error running Bad Habits Tracking Node: {e}")
        if 'container' in locals():
            container.stop()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 