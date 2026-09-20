#!/bin/bash
###############################################################################
# SSL Certificate Automation Installation Script
#
# This script installs and configures automated SSL certificate monitoring
# and renewal using systemd timers and custom monitoring scripts.
#
# Usage: sudo ./install.sh [--dry-run] [--uninstall]
###############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="/etc/systemd/system"
CONFIG_DIR="/etc/ssl_certificate_manager"
LOG_DIR="/var/log"
PYTHON_SCRIPT="${SCRIPT_DIR}/ssl_certificate_manager.py"
MONITOR_SCRIPT="${SCRIPT_DIR}/ssl_monitor.sh"
CONFIG_FILE="${SCRIPT_DIR}/config.json"

# Default values
DRY_RUN=false
UNINSTALL=false
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}"
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log "ERROR" "This script must be run as root"
        exit 1
    fi
}

# Function to check dependencies
check_dependencies() {
    log "INFO" "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v certbot &> /dev/null; then
        missing_deps+=("certbot")
    fi
    
    if ! command -v openssl &> /dev/null; then
        missing_deps+=("openssl")
    fi
    
    if ! command -v nginx &> /dev/null; then
        missing_deps+=("nginx")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log "ERROR" "Missing dependencies: ${missing_deps[*]}"
        log "INFO" "Install with: sudo apt update && sudo apt install -y ${missing_deps[*]}"
        exit 1
    fi
    
    log "INFO" "All dependencies are installed"
}

# Function to install Python dependencies
install_python_dependencies() {
    log "INFO" "Installing Python dependencies..."
    
    if ! python3 -c "import requests" 2>/dev/null; then
        if [ "${DRY_RUN}" = false ]; then
            apt install -y python3-requests
        else
            log "INFO" "DRY RUN: Would install python3-requests"
        fi
    fi
    
    log "INFO" "Python dependencies installed"
}

# Function to create configuration directory
setup_config_dir() {
    log "INFO" "Setting up configuration directory..."
    
    if [ "${DRY_RUN}" = false ]; then
        mkdir -p "${CONFIG_DIR}"
        mkdir -p "${LOG_DIR}"
        
        # Copy configuration file
        if [ -f "${CONFIG_FILE}" ]; then
            cp "${CONFIG_FILE}" "${CONFIG_DIR}/config.json"
            log "INFO" "Configuration file copied to ${CONFIG_DIR}/config.json"
        else
            log "WARNING" "Configuration file not found at ${CONFIG_FILE}"
            log "INFO" "Creating default configuration..."
            cat > "${CONFIG_DIR}/config.json" << EOF
{
  "domains": [
    "calendar.shatsie.fun",
    "connect.shatsie.fun",
    "gotify.shatsie.fun"
  ],
  "cert_path": "/etc/letsencrypt/live",
  "renewal_threshold_days": 30,
  "email_alerts": {
    "enabled": false,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your-email@gmail.com",
    "recipients": ["admin@shatsie.fun"]
  },
  "webhook_url": null,
  "dry_run": false
}
EOF
        fi
    else
        log "INFO" "DRY RUN: Would create ${CONFIG_DIR}"
    fi
}

# Function to install systemd services
install_systemd_services() {
    log "INFO" "Installing systemd services..."
    
    if [ "${DRY_RUN}" = false ]; then
        # Copy service files
        cp "${SCRIPT_DIR}/ssl-certificate-monitor.service" "${SERVICE_DIR}/"
        cp "${SCRIPT_DIR}/ssl-certificate-monitor.timer" "${SERVICE_DIR}/"
        cp "${SCRIPT_DIR}/certbot-renewal.service" "${SERVICE_DIR}/"
        cp "${SCRIPT_DIR}/certbot-renewal.timer" "${SERVICE_DIR}/"
        
        # Reload systemd
        systemctl daemon-reload
        
        # Enable and start timers
        systemctl enable ssl-certificate-monitor.timer
        systemctl start ssl-certificate-monitor.timer
        systemctl enable certbot-renewal.timer
        systemctl start certbot-renewal.timer
        
        log "INFO" "Systemd services installed and started"
    else
        log "INFO" "DRY RUN: Would install systemd services"
    fi
}

# Function to copy scripts to system location
install_scripts() {
    log "INFO" "Installing scripts..."
    
    if [ "${DRY_RUN}" = false ]; then
        # Copy Python script
        cp "${PYTHON_SCRIPT}" "/usr/local/bin/ssl_certificate_manager.py"
        chmod +x "/usr/local/bin/ssl_certificate_manager.py"
        
        # Copy monitor script
        cp "${MONITOR_SCRIPT}" "/usr/local/bin/ssl_monitor.sh"
        chmod +x "/usr/local/bin/ssl_monitor.sh"
        
        # Update service files to use new locations
        sed -i 's|/home/user/AI_Agents/ssl_automation|/usr/local/bin|g' "${SERVICE_DIR}/ssl-certificate-monitor.service"
        
        log "INFO" "Scripts installed to /usr/local/bin/"
    else
        log "INFO" "DRY RUN: Would install scripts to /usr/local/bin/"
    fi
}

# Function to setup log rotation
setup_log_rotation() {
    log "INFO" "Setting up log rotation..."
    
    if [ "${DRY_RUN}" = false ]; then
        cat > /etc/logrotate.d/ssl-certificate-manager << EOF
/var/log/ssl_certificate_manager.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root adm
}

/var/log/ssl_certificate_monitor.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root adm
}
EOF
        log "INFO" "Log rotation configured"
    else
        log "INFO" "DRY RUN: Would configure log rotation"
    fi
}

# Function to test the installation
test_installation() {
    log "INFO" "Testing installation..."
    
    if [ "${DRY_RUN}" = false ]; then
        # Test Python script
        if /usr/local/bin/ssl_certificate_manager.py --help > /dev/null 2>&1; then
            log "INFO" "Python script is working"
        else
            log "ERROR" "Python script test failed"
            return 1
        fi
        
        # Test monitor script
        if /usr/local/bin/ssl_monitor.sh --help > /dev/null 2>&1; then
            log "INFO" "Monitor script is working"
        else
            log "ERROR" "Monitor script test failed"
            return 1
        fi
        
        # Check systemd services
        if systemctl is-active --quiet ssl-certificate-monitor.timer; then
            log "INFO" "SSL certificate monitor timer is active"
        else
            log "WARNING" "SSL certificate monitor timer is not active"
        fi
        
        if systemctl is-active --quiet certbot-renewal.timer; then
            log "INFO" "Certbot renewal timer is active"
        else
            log "WARNING" "Certbot renewal timer is not active"
        fi
        
        log "INFO" "Installation test completed"
    else
        log "INFO" "DRY RUN: Would test installation"
    fi
}

# Function to uninstall
uninstall() {
    log "INFO" "Uninstalling SSL certificate automation..."
    
    if [ "${DRY_RUN}" = false ]; then
        # Stop and disable timers
        systemctl stop ssl-certificate-monitor.timer 2>/dev/null || true
        systemctl disable ssl-certificate-monitor.timer 2>/dev/null || true
        systemctl stop certbot-renewal.timer 2>/dev/null || true
        systemctl disable certbot-renewal.timer 2>/dev/null || true
        
        # Remove service files
        rm -f "${SERVICE_DIR}/ssl-certificate-monitor.service"
        rm -f "${SERVICE_DIR}/ssl-certificate-monitor.timer"
        rm -f "${SERVICE_DIR}/certbot-renewal.service"
        rm -f "${SERVICE_DIR}/certbot-renewal.timer"
        
        # Reload systemd
        systemctl daemon-reload
        
        # Remove scripts
        rm -f "/usr/local/bin/ssl_certificate_manager.py"
        rm -f "/usr/local/bin/ssl_monitor.sh"
        
        # Remove configuration (optional, keeping for safety)
        # rm -rf "${CONFIG_DIR}"
        
        # Remove log rotation
        rm -f /etc/logrotate.d/ssl-certificate-manager
        
        log "INFO" "Uninstallation completed"
        log "INFO" "Configuration files preserved in ${CONFIG_DIR}"
    else
        log "INFO" "DRY RUN: Would uninstall SSL certificate automation"
    fi
}

# Function to show status
show_status() {
    log "INFO" "SSL Certificate Automation Status"
    echo ""
    
    # Check systemd services
    echo "Systemd Services:"
    systemctl status ssl-certificate-monitor.timer --no-pager 2>/dev/null || echo "  Monitor timer: Not installed"
    systemctl status certbot-renewal.timer --no-pager 2>/dev/null || echo "  Certbot timer: Not installed"
    echo ""
    
    # Check certificates
    echo "Certificate Status:"
    if [ -f "/usr/local/bin/ssl_monitor.sh" ]; then
        /usr/local/bin/ssl_monitor.sh --config "${CONFIG_DIR}/config.json" 2>/dev/null || echo "  Unable to check certificates"
    else
        echo "  Monitor script not installed"
    fi
    echo ""
    
    # Show next scheduled runs
    echo "Next Scheduled Runs:"
    systemctl list-timers --all --no-pager | grep -E "(ssl-certificate|certbot)" || echo "  No timers found"
}

# Main installation function
install() {
    log "INFO" "Starting SSL certificate automation installation..."
    
    check_root
    check_dependencies
    install_python_dependencies
    setup_config_dir
    install_scripts
    install_systemd_services
    setup_log_rotation
    test_installation
    
    log "INFO" "Installation completed successfully!"
    echo ""
    log "INFO" "Next steps:"
    echo "  1. Edit configuration: ${CONFIG_DIR}/config.json"
    echo "  2. Test manually: /usr/local/bin/ssl_monitor.sh --test"
    echo "  3. Check status: ${SCRIPT_DIR}/install.sh --status"
    echo "  4. Monitor logs: journalctl -u ssl-certificate-monitor -f"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        --status)
            show_status
            exit 0
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run     Run in dry-run mode (no changes)"
            echo "  --uninstall   Uninstall SSL certificate automation"
            echo "  --status      Show current status"
            echo "  --verbose     Enable verbose output"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
if [ "${UNINSTALL}" = true ]; then
    uninstall
else
    install
fi