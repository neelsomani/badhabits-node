# Bad Habits Tracking Node

A Post Fiat node for tracking and analyzing personal habits, built on the nodetools framework. The node provides encrypted, private analysis of habit data using AI to help users break bad habits.

## System Requirements

- Ubuntu 22.04 LTS or later
- Python 3.12 or later
- PostgreSQL 14 or later
- 2GB RAM minimum
- 20GB storage minimum

## Setup Instructions

1. **Install System Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3.12 python3.12-venv python3-pip postgresql postgresql-contrib
   ```

2. **Set Up PostgreSQL**
In production, set up an actual Postgres instance. To set it up locally at localhost:5432:
   ```bash
   # Start PostgreSQL service
   sudo systemctl start postgresql
   sudo systemctl enable postgresql

   # Create database and user
   sudo -u postgres psql -c "CREATE DATABASE badhabits;"
   sudo -u postgres psql -c "CREATE USER badhabits WITH ENCRYPTED PASSWORD 'your_password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE badhabits TO badhabits;"
   ```

3. **Clone the Repository**
   ```bash
   git clone https://github.com/neelsomani/badhabits-node.git
   cd badhabits-node
   ```

4. **Create and Activate Virtual Environment**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

5. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Set Up Environment Variables**
   Create a `.env` file in the project root:
   ```bash
   # Required variables
   NODE_NAME=badhabits
   PFT_XRP_SECRET=your_xrp_private_key
   DATABASE_URL=postgresql://badhabits:your_password@localhost:5432/badhabits
   OPENAI_API_KEY=your_openai_api_key
   ENCRYPTION_PASSWORD=your_encryption_password

   # Network configuration (optional)
   USE_TESTNET=false  # Set to true to use testnet instead of mainnet
   HAS_LOCAL_NODE=false  # Set to true if running a local rippled node
   LOCAL_NODE_RPC_URL=http://127.0.0.1:5005  # Only needed if HAS_LOCAL_NODE=true
   LOCAL_NODE_WS_URL=ws://127.0.0.1:6006     # Only needed if HAS_LOCAL_NODE=true
   ```

7. **Set Up Node and Initialize Database**
   First, run the setup script to configure credentials:
   ```bash
   python -m badhabits.cli --setup
   ```
   Then initialize the database:
   ```bash
   nodetools init-db --create-db
   ```

## Running the Node

1. **Start the Node**
   ```bash
   python -m badhabits.cli
   ```

2. **Monitor Logs**
   ```bash
   tail -f badhabits.log
   ```

## Usage

Users can interact with the node by sending XRPL transactions with encrypted memos. The memo format is:

```
WHISPER__<encrypted_message>
```

Where the encrypted message contains:
```
BAD_HABITS_REQUEST: <habit_data>
```

The node will:
1. Decrypt the message using ECDH with the user's public key
2. Process the habit data
3. Generate personalized recommendations
4. Send an encrypted response using the same ECDH encryption
