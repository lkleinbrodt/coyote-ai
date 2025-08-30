#!/bin/bash

# Test database management script for SideQuest backend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.test.yml"

case "${1:-help}" in
    start)
        echo "🚀 Starting SideQuest test database..."
        docker-compose -f "$COMPOSE_FILE" up -d
        
        echo "⏳ Waiting for database to be ready..."
        sleep 5
        
        echo "✅ Test database is ready!"
        echo "   Host: localhost"
        echo "   Port: 5434"
        echo "   Database: sidequest_test"
        echo "   User: sidequest_user"
        echo "   Password: sidequest_password"
        ;;
        
    stop)
        echo "🛑 Stopping SideQuest test database..."
        docker-compose -f "$COMPOSE_FILE" down
        echo "✅ Test database stopped."
        ;;
        
    restart)
        echo "🔄 Restarting SideQuest test database..."
        docker-compose -f "$COMPOSE_FILE" restart
        echo "✅ Test database restarted."
        ;;
        
    status)
        if docker ps --filter name=sidequest_db_test --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q sidequest_db_test; then
            echo "✅ Test database is running:"
            docker ps --filter name=sidequest_db_test --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        else
            echo "❌ Test database is not running."
        fi
        ;;
        
    logs)
        echo "📋 Test database logs:"
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
        
    clean)
        echo "🧹 Cleaning up test database..."
        docker-compose -f "$COMPOSE_FILE" down -v
        echo "✅ Test database cleaned up."
        ;;
        
    help|*)
        echo "SideQuest Test Database Management"
        echo "=================================="
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|clean|help}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the test database"
        echo "  stop    - Stop the test database"
        echo "  restart - Restart the test database"
        echo "  status  - Show database status"
        echo "  logs    - Show database logs"
        echo "  clean   - Stop and remove database volumes"
        echo "  help    - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start    # Start test database"
        echo "  $0 status   # Check if running"
        echo "  $0 stop     # Stop test database"
        ;;
esac
