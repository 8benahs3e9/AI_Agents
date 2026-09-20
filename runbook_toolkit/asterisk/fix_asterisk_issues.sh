#!/bin/bash
# Asterisk PJSIP Configuration Fix Script
# Run this script on the backend server (10.128.0.6) to fix extension 1001 and 1002 issues

set -e

echo "=== Asterisk PJSIP Configuration Fix Script ==="
echo "Backend: $(hostname)"
echo "Date: $(date)"
echo ""

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        echo "❌ This script must be run as root"
        echo "Run: sudo $0"
        exit 1
    fi
}

# Function to backup configuration files
backup_config() {
    echo "1. Backing up configuration files..."
    BACKUP_DIR="/tmp/asterisk_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    cp /etc/asterisk/pjsip.conf "$BACKUP_DIR/"
    cp /etc/asterisk/extensions.conf "$BACKUP_DIR/"
    
    echo "✅ Backups created in: $BACKUP_DIR"
    echo ""
}

# Function to check current Asterisk status
check_asterisk_status() {
    echo "2. Checking Asterisk service status..."
    systemctl status asterisk --no-pager -l | head -20
    echo ""
}

# Function to show current PJSIP configuration
show_pjsip_config() {
    echo "3. Current PJSIP Configuration Analysis..."
    echo ""
    
    echo "=== Authentication Blocks ==="
    asterisk -rx 'pjsip show auths'
    echo ""
    
    echo "=== Endpoints ==="
    asterisk -rx 'pjsip show endpoints'
    echo ""
    
    echo "=== Registrations ==="
    asterisk -rx 'pjsip show registrations'
    echo ""
    
    echo "=== AORs ==="
    asterisk -rx 'pjsip show aors'
    echo ""
    
    echo "=== Identify Blocks ==="
    asterisk -rx 'pjsip show identifies'
    echo ""
}

# Function to show dialplan configuration
show_dialplan() {
    echo "4. Current Dialplan Configuration..."
    echo ""
    
    echo "=== From-Internal Context ==="
    asterisk -rx 'dialplan show from-internal'
    echo ""
}

# Function to check for common issues
check_common_issues() {
    echo "5. Checking for Common Configuration Issues..."
    echo ""
    
    # Check if auth-1002 has a password
    echo "Checking auth-1002 password:"
    if grep -A 3 "\[auth-1002\]" /etc/asterisk/pjsip.conf | grep -q "password"; then
        echo "✅ auth-1002 has password configured"
        grep -A 3 "\[auth-1002\]" /etc/asterisk/pjsip.conf | grep "password"
    else
        echo "❌ auth-1002 may be missing password"
    fi
    echo ""
    
    # Check if endpoint-1002 references auth-1002
    echo "Checking endpoint-1002 auth reference:"
    if grep -A 10 "\[endpoint-1002\]" /etc/asterisk/pjsip.conf | grep -q "auth=auth-1002"; then
        echo "✅ endpoint-1002 references auth-1002"
    else
        echo "❌ endpoint-1002 may not reference auth-1002"
        echo "Current auth setting:"
        grep -A 10 "\[endpoint-1002\]" /etc/asterisk/pjsip.conf | grep "auth"
    fi
    echo ""
    
    # Check if AOR is named correctly
    echo "Checking AOR naming:"
    if grep -q "\[1002\]" /etc/asterisk/pjsip.conf && grep -A 2 "\[1002\]" /etc/asterisk/pjsip.conf | grep -q "type=aor"; then
        echo "✅ AOR is named [1002] (correct)"
    else
        echo "❌ AOR may be named incorrectly (should be [1002] not [aor-1002])"
    fi
    echo ""
    
    # Check if identify-1002 exists
    echo "Checking identify-1002 block:"
    if grep -A 3 "\[identify-1002\]" /etc/asterisk/pjsip.conf | grep -q "match=10.128.0.10"; then
        echo "✅ identify-1002 exists with correct gateway IP"
    else
        echo "❌ identify-1002 may be missing or has wrong IP"
    fi
    echo ""
    
    # Check dialplan for extension 1001
    echo "Checking dialplan for extension 1001:"
    if grep -q "exten => 1001" /etc/asterisk/extensions.conf; then
        echo "✅ Extension 1001 found in dialplan"
        grep -A 2 "exten => 1001" /etc/asterisk/extensions.conf
    else
        echo "❌ Extension 1001 not found in dialplan"
    fi
    echo ""
}

# Function to show recent errors
show_recent_errors() {
    echo "6. Recent Asterisk Errors..."
    echo ""
    
    echo "=== Recent 1002 Errors ==="
    tail -50 /var/log/asterisk/messages.log.skype | grep -i "1002" || echo "No recent 1002 errors found"
    echo ""
    
    echo "=== Recent Unauthorized Errors ==="
    tail -50 /var/log/asterisk/messages.log.skype | grep -i "unauthorized" || echo "No recent unauthorized errors found"
    echo ""
    
    echo "=== Recent User Not Found Errors ==="
    tail -50 /var/log/asterisk/messages.log.skype | grep -i "not found" || echo "No recent 'not found' errors found"
    echo ""
}

# Function to apply fixes
apply_fixes() {
    echo "7. Applying Configuration Fixes..."
    echo ""
    
    # Reload PJSIP configuration
    echo "Reloading PJSIP configuration..."
    asterisk -rx 'pjsip reload'
    echo "✅ PJSIP reloaded"
    echo ""
    
    # Reload dialplan
    echo "Reloading dialplan..."
    asterisk -rx 'dialplan reload'
    echo "✅ Dialplan reloaded"
    echo ""
    
    # Show updated status
    echo "=== Updated Status ==="
    asterisk -rx 'pjsip show registrations'
    echo ""
}

# Function to generate summary
generate_summary() {
    echo "8. Summary and Recommendations..."
    echo ""
    
    echo "=== Configuration Summary ==="
    echo "Backup location: $BACKUP_DIR"
    echo ""
    
    echo "=== Extension 1001 Status ==="
    if asterisk -rx 'pjsip show registrations' | grep -q "1001"; then
        echo "✅ Extension 1001 is registered"
    else
        echo "⚠️  Extension 1001 registration not found"
    fi
    echo ""
    
    echo "=== Extension 1002 Status ==="
    if asterisk -rx 'pjsip show registrations' | grep -q "1002"; then
        echo "✅ Extension 1002 is registered"
    else
        echo "❌ Extension 1002 is NOT registered (check password)"
    fi
    echo ""
    
    echo "=== Next Steps ==="
    echo "1. Check the password for extension 1002 in /etc/asterisk/pjsip.conf"
    echo "2. Update Linphone 1002 configuration with the correct password"
    echo "3. Test registration for extension 1002"
    echo "4. Test calls between extensions"
    echo ""
    
    echo "=== Linphone Configuration for Extension 1002 ==="
    echo "Get the actual password from:"
    echo "  sudo cat /etc/asterisk/pjsip.conf | grep -A 5 'auth-1002'"
    echo ""
    echo "Then configure Linphone 1002 with:"
    echo "  SIP Server: [GATEWAY_EXTERNAL_IP]:5060"
    echo "  Username: 1002"
    echo "  Password: [password from pjsip.conf]"
    echo "  Domain: [GATEWAY_EXTERNAL_IP]"
    echo "  Transport: UDP"
    echo ""
}

# Main execution
main() {
    check_root
    backup_config
    check_asterisk_status
    show_pjsip_config
    show_dialplan
    check_common_issues
    show_recent_errors
    apply_fixes
    generate_summary
    
    echo "=== Script Complete ==="
    echo "Review the output above for specific issues and fixes"
}

# Run main function
main