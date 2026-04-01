#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory this script is in
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

DB_FILE="roger.db"
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/roger_${TIMESTAMP}.db"

echo -e "${YELLOW}🔄 Starting Roger AI Database Reset...${NC}"
echo ""

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    echo -e "${GREEN}✓ Created backups directory${NC}"
fi

# Backup existing database if it exists
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✓ Backed up existing database to: $BACKUP_FILE${NC}"
else
    echo -e "${YELLOW}ℹ No existing database found${NC}"
fi

# Delete the database file to force complete schema recreation
if [ -f "$DB_FILE" ]; then
    rm "$DB_FILE"
    echo -e "${GREEN}✓ Removed old database file${NC}"
fi

# Reinitialize the database via Python
echo ""
echo -e "${YELLOW}📊 Reinitializing database schema...${NC}"

python3 << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from database import init_db
    init_db()
    print("\033[32m✓ Database schema created successfully\033[0m")
except Exception as e:
    print(f"\033[31m✗ Error initializing database: {e}\033[0m")
    sys.exit(1)
EOF

echo ""
echo -e "${GREEN}✅ Database reset complete!${NC}"
echo ""
echo -e "${YELLOW}Summary:${NC}"
echo -e "  • Database file: $DB_FILE"
echo -e "  • Backup location: $BACKUP_FILE"
echo -e "  • All tables recreated with fresh schema"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Restart the server: ${GREEN}./start_roger.sh${NC}"
echo -e "  2. New users will auto-initialize core skills on registration"
echo ""


