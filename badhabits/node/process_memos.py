"""
Core business logic for the Bad Habits Tracking Node.
Handles memo processing, habit tracking, and user interactions.
"""
from typing import Dict, Any, Optional
import re
from datetime import datetime
from loguru import logger

from nodetools.models.models import (
    InteractionGraph,
    MemoPattern,
    ResponseQuery,
    BusinessLogicProvider,
    RequestRule,
    ResponseRule,
    StandaloneRule,
    InteractionType,
    ResponseGenerator,
    ResponseParameters,
    Dependencies
)
from nodetools.configuration.constants import SystemMemoType
from nodetools.ai.openai import OpenAIRequestTool
from nodetools.protocols.generic_pft_utilities import GenericPFTUtilities
from nodetools.protocols.credentials import CredentialManager
from nodetools.configuration.configuration import NodeConfig
from badhabits.prompts.habit_tracking import habit_tracking_prompt

# Define memo patterns
BAD_HABITS_REQUEST_PATTERN = MemoPattern(
    memo_type=re.compile(r'(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}(?:__[A-Z0-9]{4})?)'),
    memo_data=re.compile(r'.*BAD_HABITS_REQUEST.*')
)

BAD_HABITS_RESPONSE_PATTERN = MemoPattern(
    memo_type=re.compile(r'(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}(?:__[A-Z0-9]{4})?_response)')
)

class BadHabitsRules(BusinessLogicProvider):
    """Business logic for bad habits tracking"""

    @classmethod
    def create(cls) -> 'BadHabitsRules':
        """Factory function to create all business logic components"""
        # Setup transaction graph
        graph = InteractionGraph()

        # Create rules
        rules = {
            "bad_habits_request": BadHabitsRequestRule(),
            "bad_habits_response": BadHabitsResponseRule(),
        }

        # Add patterns to graph
        graph.add_pattern(
            pattern_id="bad_habits_request",
            memo_pattern=BAD_HABITS_REQUEST_PATTERN,
            transaction_type=InteractionType.REQUEST,
            valid_responses={BAD_HABITS_RESPONSE_PATTERN},
            notify=True
        )
        graph.add_pattern(
            pattern_id="bad_habits_response",
            memo_pattern=BAD_HABITS_RESPONSE_PATTERN,
            transaction_type=InteractionType.RESPONSE,
            notify=True
        )

        return cls(graph, rules)

class BadHabitsRequestRule(RequestRule):
    """Rule for handling bad habits tracking requests"""

    async def validate(
        self,
        tx: Dict[str, Any],
        dependencies: Dependencies
    ) -> bool:
        """Validate the request transaction"""
        try:
            # Check if transaction is addressed to our node
            if tx['Destination'] != dependencies.node_config.node_address:
                return False

            # Get memo data
            memo_data = tx.get('Memos', [{}])[0].get('Memo', {}).get('MemoData', '')
            
            # Require encryption for health data
            if not memo_data.startswith('WHISPER__'):
                logger.error("Health data must be encrypted. Message must start with WHISPER__")
                return False

            try:
                # Get the source address for decryption
                source_address = tx['Account']
                
                # Get shared secret using ECDH with address public keys
                shared_secret = dependencies.generic_pft_utilities.message_encryption.get_shared_secret(
                    received_public_key=source_address,  # User's public key from their address
                    channel_private_key=dependencies.node_config.node_secret  # Our private key
                )
                
                # Decrypt the message
                memo_data = dependencies.generic_pft_utilities.message_encryption.process_encrypted_message(
                    memo_data, 
                    shared_secret
                )
            except Exception as e:
                logger.error(f"Error decrypting message: {e}")
                return False

            # Validate memo format
            if not memo_data.startswith('BAD_HABITS_REQUEST:'):
                return False

            return True
        except Exception as e:
            logger.error(f"Error validating bad habits request: {e}")
            return False

    async def find_response(
        self,
        request_tx: Dict[str, Any],
    ) -> Optional[ResponseQuery]:
        """Find existing response for this request"""
        # Implementation for finding existing responses
        return None

class BadHabitsResponseRule(ResponseRule):
    """Rule for handling bad habits tracking responses"""

    async def validate(self, *args, **kwargs) -> bool:
        """Validate the response transaction"""
        return True

    def get_response_generator(self, dependencies: Dependencies) -> ResponseGenerator:
        """Get the response generator"""
        return BadHabitsResponseGenerator(
            openai=dependencies.openai,
            node_config=dependencies.node_config,
            generic_pft_utilities=dependencies.generic_pft_utilities,
            credential_manager=dependencies.credential_manager
        )

class BadHabitsResponseGenerator(ResponseGenerator):
    """Generates responses for bad habits tracking requests"""

    def __init__(
        self,
        openai: OpenAIRequestTool,
        node_config: NodeConfig,
        generic_pft_utilities: GenericPFTUtilities,
        credential_manager: CredentialManager
    ):
        self.openai = openai
        self.node_config = node_config
        self.generic_pft_utilities = generic_pft_utilities
        self.credential_manager = credential_manager

    async def evaluate_request(self, request_tx: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the request and prepare response data"""
        try:
            # Extract the habit tracking request
            memo_data = request_tx['Memos'][0]['Memo']['MemoData']
            habit_request = memo_data.replace('BAD_HABITS_REQUEST:', '').strip()

            # Process with OpenAI using our prompt
            response = await self.openai.create_chat_completion(
                messages=[
                    {"role": "system", "content": habit_tracking_prompt.replace('___USER_HABIT_DATA___', habit_request)},
                    {"role": "user", "content": "Please analyze my habit data and provide insights and recommendations."}
                ]
            )

            return {
                "habit_request": habit_request,
                "ai_response": response.choices[0].message.content
            }
        except Exception as e:
            logger.error(f"Error evaluating bad habits request: {e}")
            raise

    async def construct_response(
        self,
        request_tx: Dict[str, Any],
        evaluation_result: Dict[str, Any]
    ) -> ResponseParameters:
        """Construct the response parameters"""
        try:
            # Get the source address
            source_address = request_tx['Account']

            # Construct response memo
            response_memo = self.generic_pft_utilities.construct_memo(
                memo_format="BAD_HABITS",
                memo_type=f"{request_tx['Memos'][0]['Memo']['MemoType']}_response",
                memo_data=evaluation_result['ai_response']
            )

            return ResponseParameters(
                destination=source_address,
                memo=response_memo,
                encrypt=True
            )
        except Exception as e:
            logger.error(f"Error constructing bad habits response: {e}")
            raise 