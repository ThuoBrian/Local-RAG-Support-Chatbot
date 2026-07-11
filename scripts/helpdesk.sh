#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear_screen() {
    printf '\033[2J\033[H'
}

print_header() {
    clear_screen
    echo ""
    echo -e "${BLUE}${BOLD}  Helpdesk RAG — Knowledge Assistant${NC}"
    echo -e "${BLUE}  Local chatbot for IT support documents${NC}"
    echo ""
}

press_enter() {
    echo ""
    echo -e "${YELLOW}Press Enter to return to the menu...${NC}"
    read -r
}

check_ollama() {
    if curl -s http://localhost:11434 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is running${NC}"
        return 0
    else
        echo -e "${RED}✗ Ollama is not running${NC}"
        echo "   Please start Ollama first: https://ollama.com/download"
        return 1
    fi
}

check_models() {
    echo ""
    echo -e "${BOLD}Checking required models...${NC}"
    local missing=0
    for model in nomic-embed-text glm-5.1:cloud; do
        if ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$model"; then
            echo -e "  ${GREEN}✓${NC} $model"
        else
            echo -e "  ${RED}✗${NC} $model (missing)"
            missing=1
        fi
    done
    return $missing
}

do_setup() {
    print_header
    echo -e "${BOLD}Step 1: Project Setup${NC}"
    echo "This will create the virtual environment and install dependencies."
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read -r
    ./scripts/setup.sh
    echo ""
    echo -e "${GREEN}Setup complete.${NC}"
    press_enter
}

do_ollama() {
    print_header
    echo -e "${BOLD}Ollama Status${NC}"
    echo ""
    if check_ollama; then
        check_models || {
            echo ""
            echo -e "${YELLOW}Would you like to pull the missing models now? (y/n)${NC}"
            read -r answer
            if [[ "$answer" =~ ^[Yy]$ ]]; then
                ollama pull nomic-embed-text
                ollama pull glm-5.1:cloud
                echo -e "${GREEN}Models ready.${NC}"
            fi
        }
    fi
    press_enter
}

do_ingest() {
    print_header
    echo -e "${BOLD}Step 2: Add / Update Documents${NC}"
    echo ""

    if [ ! -d ".venv" ]; then
        echo -e "${RED}Project is not set up yet.${NC}"
        echo "Please run 'Setup Project' first."
        press_enter
        return
    fi

    if ! check_ollama; then
        press_enter
        return
    fi

    echo -e "Documents should be placed in: ${BOLD}data/documents/${NC}"
    echo ""
    echo -n "Supported files: "
    find data/documents -maxdepth 1 -type f \( -name '*.pdf' -o -name '*.docx' -o -name '*.md' -o -name '*.txt' \) 2>/dev/null | wc -l | tr -d ' '
    echo " found"
    echo ""
    echo -e "${YELLOW}Press Enter to ingest documents...${NC}"
    read -r
    ./scripts/ingest.sh
    press_enter
}

do_start() {
    print_header
    echo -e "${BOLD}Step 3: Start Chat Server${NC}"
    echo ""

    if [ ! -d ".venv" ]; then
        echo -e "${RED}Project is not set up yet.${NC}"
        echo "Please run 'Setup Project' first."
        press_enter
        return
    fi

    if ! check_ollama; then
        press_enter
        return
    fi

    echo -e "The chat interface will open at: ${GREEN}http://localhost:8000${NC}"
    echo ""
    echo -e "${YELLOW}Press Enter to start the server...${NC}"
    read -r
    echo -e "${GREEN}Starting server. Press Ctrl+C to stop.${NC}"
    echo ""
    ./scripts/start.sh
}

do_test() {
    print_header
    echo -e "${BOLD}Run Project Tests${NC}"
    echo ""

    if [ ! -d ".venv" ]; then
        echo -e "${RED}Project is not set up yet.${NC}"
        press_enter
        return
    fi

    echo -e "${YELLOW}Press Enter to run tests...${NC}"
    read -r
    .venv/bin/pytest -m "not integration"
    press_enter
}

do_status() {
    print_header
    echo -e "${BOLD}Project Status${NC}"
    echo ""

    if [ -d ".venv" ]; then
        echo -e "  ${GREEN}✓${NC} Virtual environment exists"
    else
        echo -e "  ${RED}✗${NC} Virtual environment missing — run Setup"
    fi

    if [ -f "config/config.yaml" ]; then
        echo -e "  ${GREEN}✓${NC} Config file exists"
    else
        echo -e "  ${RED}✗${NC} Config file missing"
    fi

    if [ -f ".env" ]; then
        echo -e "  ${GREEN}✓${NC} .env file exists"
    else
        echo -e "  ${RED}✗${NC} .env file missing"
    fi

    check_ollama

    local doc_count
    doc_count=$(find data/documents -maxdepth 1 -type f \( -name '*.pdf' -o -name '*.docx' -o -name '*.md' -o -name '*.txt' \) 2>/dev/null | wc -l | tr -d ' ')
    echo -e "  ${BLUE}ℹ${NC} Documents in data/documents/: $doc_count"

    if [ -d ".venv" ]; then
        local chunk_count
        chunk_count=$(.venv/bin/python -c "from helpdesk_rag.config import load_config; from helpdesk_rag.vector_store import VectorStore; print(VectorStore(load_config().vector_store).count())" 2>/dev/null || echo "0")
        echo -e "  ${BLUE}ℹ${NC} Indexed chunks in vector store: $chunk_count"
    fi

    press_enter
}

while true; do
    print_header
    echo -e "${BOLD}What would you like to do?${NC}"
    echo ""
    echo -e "  ${BOLD}1.${NC} Setup Project (one-time)"
    echo -e "  ${BOLD}2.${NC} Check Ollama Status"
    echo -e "  ${BOLD}3.${NC} Add / Update Documents"
    echo -e "  ${BOLD}4.${NC} Start Chat Server"
    echo -e "  ${BOLD}5.${NC} Run Tests"
    echo -e "  ${BOLD}6.${NC} View Project Status"
    echo -e "  ${BOLD}0.${NC} Exit"
    echo ""
    echo -n "Enter choice [0-6]: "
    read -r choice

    case "$choice" in
        1) do_setup ;;
        2) do_ollama ;;
        3) do_ingest ;;
        4) do_start ;;
        5) do_test ;;
        6) do_status ;;
        0)
            echo ""
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please enter a number between 0 and 6.${NC}"
            sleep 1
            ;;
    esac
done
