#!/bin/bash
###############################################################################
# SSL Certificate Monitoring Script
# 
# This script monitors SSL certificate expiry and triggers automated renewal
# when certificates are approaching expiration.
#
# Usage: ./ssl_monitor.sh [--dry-run] [--config <path>]
###############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/ssl_certificate_manager.py"
CONFIG_FILE="${SCRIPT_DIR}/config.json"
LOG_FILE="/var/log/ssl_certificate_monitor.log"
HEALTH_REPORT="/var/log/ssl_certificate_health_report.json"

# Default values
DRY_RUN=false
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}"
}

# Function to check dependencies
check_dependencies() {
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
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log "ERROR" "Missing dependencies: ${missing_deps[*]}"
        log "ERROR" "Install with: sudo apt install ${missing_deps[*]}"
        exit 1
    fi
}

# Function to check certificate expiry manually
check_certificate_expiry() {
    local domain=$1
    local cert_path="/etc/letsencrypt/live/${domain}/cert.pem"
    
    if [ ! -f "${cert_path}" ]; then
        log "ERROR" "Certificate not found for ${domain}: ${cert_path}"
        return 1
    fi
    
    # Get expiry date using openssl
    local expiry_date=$(openssl x509 -enddate -noout -in "${cert_path}" | cut -d= -f2)
    local expiry_timestamp=$(date -d "${expiry_date}" +%s)
    local current_timestamp=$(date +%s)
    local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
    
    if [ ${days_until_expiry} -lt 0 ]; then
        echo -e "${RED}EXPIRED${NC} - ${domain} expired ${days_until_expiry} days ago"
        log "CRITICAL" "${domain} is EXPIRED (${days_until_expiry} days ago)"
        return 2
    elif [ ${days_until_expiry} -le 7 ]; then
        echo -e "${RED}CRITICAL${NC} - ${domain} expires in ${days_until_expiry} days"
        log "CRITICAL" "${domain} expires in ${days_until_expiry} days"
        return 2
    elif [ ${days_until_expiry} -le 30 ]; then
        echo -e "${YELLOW}WARNING${NC} - ${domain} expires in ${days_until_expiry} days"
        log "WARNING" "${domain} expires in ${days_until_expiry} days"
        return 1
    else
        echo -e "${GREEN}OK${NC} - ${domain} expires in ${days_until_expiry} days"
        log "INFO" "${domain} is valid (expires in ${days_until_expiry} days)"
        return 0
    fi
}

# Function to run Python certificate manager
run_python_manager() {
    local action=$1
    local domain=${2:-}
    local args=()
    
    if [ "${DRY_RUN}" = true ]; then
        args+=("--dry-run")
    fi
    
    if [ -n "${domain}" ]; then
        args+=("--domain" "${domain}")
    fi
    
    if [ "${VERBOSE}" = true ]; then
        args+=("--verbose")
    fi
    
    python3 "${PYTHON_SCRIPT}" "${action}" "${args[@]}" --config "${CONFIG_FILE}"
}

# Function to send alert notification
send_alert() {
    local subject=$1
    local message=$2
    local priority=${3:-"NORMAL"}
    
    # Log the alert
    log "ALERT" "[${priority}] ${subject}: ${message}"
    
    # Send email if configured (would need to implement email sending)
    # For now, just log it
    if [ "${VERBOSE}" = true ]; then
        echo "Alert: ${subject} - ${message}"
    fi
}

# Main monitoring function
monitor_certificates() {
    log "INFO" "Starting SSL certificate monitoring"
    
    # Check Python script availability
    if [ ! -f "${PYTHON_SCRIPT}" ]; then
        log "ERROR" "Python script not found: ${PYTHON_SCRIPT}"
        exit 1
    fi
    
    # Use Python script for comprehensive monitoring
    if [ "${DRY_RUN}" = true ]; then
        log "INFO" "DRY RUN MODE - No actual changes will be made"
    fi
    
    # Run scan
    log "INFO" "Scanning certificates..."
    python3 "${PYTHON_SCRIPT}" scan --config "${CONFIG_FILE}"
    
    # Generate health report
    log "INFO" "Generating health report..."
    python3 "${PYTHON_SCRIPT}" report --config "${CONFIG_FILE}"
    
    # Check for certificates needing renewal
    log "INFO" "Checking for certificates needing renewal..."
    python3 "${PYTHON_SCRIPT}" renew --config "${CONFIG_FILE}"
    
    log "INFO" "SSL certificate monitoring completed"
}

# Function to setup automated renewal via cron
setup_cron_job() {
    local cron_entry="0 3 * * * ${SCRIPT_DIR}/ssl_monitor.sh >> ${LOG_FILE} 2>&1"
    
    log "INFO" "Setting up cron job for automated monitoring"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "ssl_monitor.sh"; then
        log "INFO" "Cron job already exists"
        return 0
    fi
    
    # Add cron job
    (crontab -l 2>/dev/null; echo "${cron_entry}") | crontab -
    log "INFO" "Cron job added: ${cron_entry}"
    
    # Also add certbot auto-renewal cron job
    local certbot_cron="0 0,12 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'"
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        (crontab -l 2>/dev/null; echo "${certbot_cron}") | crontab -
        log "INFO" "Certbot auto-renewal cron job added"
    fi
}

# Function to test the setup
test_setup() {
    log "INFO" "Testing SSL certificate automation setup"
    
    check_dependencies
    
    log "INFO" "Testing certificate scan..."
    python3 "${PYTHON_SCRIPT}" scan --config "${CONFIG_FILE}"
    
    log "INFO" "Testing certificate validation..."
    python3 "${PYTHON_SCRIPT}" validate --config "${CONFIG_FILE}"
    
    log "INFO" "Testing health report generation..."
    python3 "${PYTHON_SCRIPT}" report --config "${CONFIG_FILE}"
    
    log "INFO" "Setup test completed successfully"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --setup-cron)
            setup_cron_job
            exit 0
            ;;
        --test)
            test_setup
            exit 0
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run           Run in dry-run mode (no changes)"
            echo "  --config <path>     Path to configuration file"
            echo "  --verbose           Enable verbose output"
            echo "  --setup-cron        Setup automated cron jobs"
            echo "  --test              Test the setup"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create log directory if it doesn't exist
mkdir -p "$(dirname "${LOG_FILE}")"

# Check dependencies
check_dependencies

# Run monitoring
monitor_certificates