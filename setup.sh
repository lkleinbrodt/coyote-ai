#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to clean up background processes
cleanup() {
    echo -e "\n${BLUE}Shutting down servers...${NC}"
    pkill -P $$ || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

echo -e "${BLUE}Setting up project...${NC}"

# 1. Setup Python environment
echo -e "${GREEN}Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 2. Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install -r backend/requirements.txt

# 3. Setup database
echo -e "${GREEN}Setting up database...${NC}"
flask db upgrade

# 4. Install frontend dependencies
echo -e "${GREEN}Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# 5. Start servers
echo -e "${GREEN}Starting servers...${NC}"
echo -e "${BLUE}Starting Flask backend on http://localhost:5002${NC}"
echo -e "${BLUE}Starting React frontend on http://localhost:5173${NC}"
echo -e "${BLUE}Press Ctrl+C to stop all servers${NC}"

(cd frontend && npm run dev) &
flask run --host=0.0.0.0 --port=5002 