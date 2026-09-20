#!/bin/bash
###############################################################################
# Automated System Cleanup Script
#
# This script performs automated cleanup of various system resources to
# maintain disk space and system performance.
#
# Usage: sudo /usr/local/bin/auto-cleanup.sh [--dry-run] [--verbose]
###############################################################################

set -euo pipefail

# Configuration
LOG_FILE="/var/log/auto-cleanup.log"
MAX_LOG_SIZE=10485760  # 10MB
LOG_RETENTION_DAYS=30
TEMP_RETENTION_DAYS=7
APT_CACHE_CLEAN=true
JOURNAL_CLEAN=true
OLD_LOGS_CLEAN=true
TEMP_FILES_CLEAN=true

# Command line arguments
DRY_RUN=false
VERBOSE=false

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Function to clean APT cache
clean_apt_cache() {
    log "INFO" "Cleaning APT cache..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN: Would clean APT cache"
        return 0
    fi
    
    # Clean package cache
    apt-get clean -qq >> "$LOG_FILE" 2>&1
    apt-get autoclean -qq >> "$LOG_FILE" 2>&1
    
    # Remove unused packages
    apt-get autoremove -y -qq >> "$LOG_FILE" 2>&1
    
    # Clean orphaned packages (deborphan may not be installed)
    if command -v deborphan &> /dev/null; then
        deborphan | xargs -r apt-get -y remove -qq >> "$LOG_FILE" 2>&1 || true
    fi
    
    log "INFO" "APT cache cleaned"
}

# Function to clean systemd journal
clean_journal() {
    log "INFO" "Cleaning systemd journal..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN: Would clean systemd journal"
        return 0
    fi
    
    # Keep journal logs for 7 days
    journalctl --vacuum-time=7d >> "$LOG_FILE" 2>&1
    
    # Limit journal size to 100M
    journalctl --vacuum-size=100M >> "$LOG_FILE" 2>&1
    
    log "INFO" "Systemd journal cleaned"
}

# Function to clean old log files
clean_old_logs() {
    log "INFO" "Cleaning old log files..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN: Would clean old log files"
        return 0
    fi
    
    # Clean old compressed logs in /var/log
    find /var/log -name "*.gz" -mtime +$LOG_RETENTION_DAYS -delete >> "$LOG_FILE" 2>&1
    find /var/log -name "*.bz2" -mtime +$LOG_RETENTION_DAYS -delete >> "$LOG_FILE" 2>&1
    find /var/log -name "*.xz" -mtime +$LOG_RETENTION_DAYS -delete >> "$LOG_FILE" 2>&1
    
    # Clean old numbered logs
    find /var/log -name "*.1" -mtime +$LOG_RETENTION_DAYS -delete >> "$LOG_FILE" 2>&1
    find /var/log -name "*.2" -mtime +$LOG_RETENTION_DAYS -delete >> "$LOG_FILE" 2>&1
    find /var/log -name "*.3" -mtime +$LOG_RETENTION_DAYS -delete >> "$LOG_FILE" 2>&1
    
    # Clean application-specific old logs
    find /var/log -name "*.old" -mtime +$LOG_RETENTION_DAYS -delete >> "$LOG_FILE" 2>&1
    
    log "INFO" "Old log files cleaned"
}

# Function to clean temporary files
clean_temp_files() {
    log "INFO" "Cleaning temporary files..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN: Would clean temporary files"
        return 0
    fi
    
    # Clean /tmp
    find /tmp -type f -mtime +$TEMP_RETENTION_DAYS -delete >> "$LOG_FILE" 2>&1
    
    # Clean /var/tmp
    find /var/tmp -type f -mtime +$TEMP_RETENTION_DAYS -delete >> "$LOG_FILE" 2>&1
    
    # Clean user temp directories
    find /home/*/tmp -type f -mtime +$TEMP_RETENTION_DAYS -delete >> "$LOG_FILE" 2>&1 || true
    
    # Clean package manager temp files
    rm -rf /var/lib/apt/lists/partial/* >> "$LOG_FILE" 2>&1 || true
    rm -rf /var/cache/apt/archives/partial/* >> "$LOG_FILE" 2>&1 || true
    
    log "INFO" "Temporary files cleaned"
}

# Function to clean old kernels (Debian)
clean_old_kernels() {
    log "INFO" "Checking for old kernels..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN: Would check for old kernels"
        return 0
    fi
    
    # Count installed kernels
    current_kernel=$(uname -r)
    kernel_count=$(dpkg -l | grep linux-image | grep -v "$current_kernel" | wc -l)
    
    if [ "$kernel_count" -gt 2 ]; then
        log "INFO" "Found $kernel_count old kernels, removing..."
        apt-get autoremove -y --purge -qq >> "$LOG_FILE" 2>&1
        log "INFO" "Old kernels removed"
    else
        log "INFO" "No old kernels to remove (count: $kernel_count)"
    fi
}

# Function to clean thumbnail cache
clean_thumbnails() {
    log "INFO" "Cleaning thumbnail cache..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN: Would clean thumbnail cache"
        return 0
    fi
    
    # Clean user thumbnail caches
    find /home -type d -name ".thumbnails" -exec rm -rf {} + >> "$LOG_FILE" 2>&1 || true
    find /home -type d -name ".cache/thumbnails" -exec rm -rf {} + >> "$LOG_FILE" 2>&1 || true
    
    log "INFO" "Thumbnail cache cleaned"
}

# Function to clean application caches
clean_app_caches() {
    log "INFO" "Cleaning application caches..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN: Would clean application caches"
        return 0
    fi
    
    # Clean Python cache
    find /home -type d -name "__pycache__" -exec rm -rf {} + >> "$LOG_FILE" 2>&1 || true
    find /home -type d -name ".pytest_cache" -exec rm -rf {} + >> "$LOG_FILE" 2>&1 || true
    
    # Clean Node modules cache (if exists)
    find /home -type d -name ".npm" -exec rm -rf {} + >> "$LOG_FILE" 2>&1 || true
    
    log "INFO" "Application caches cleaned"
}

# Function to check disk space before and after
check_disk_space() {
    local usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    log "INFO" "Disk usage: ${usage}%"
    # Return just the number for arithmetic operations
    echo "$usage"
}

# Function to show cleanup summary
show_summary() {
    local before=$1
    local after=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    
    log "INFO" "Disk usage after cleanup: ${after}%"
    
    if [ "$VERBOSE" = true ]; then
        local freed
        if [[ "$before" =~ ^[0-9]+$ ]] && [[ "$after" =~ ^[0-9]+$ ]]; then
            freed=$((before - after))
        else
            freed="N/A"
        fi
        echo "=== Cleanup Summary ==="
        echo "Before: ${before}%"
        echo "After: ${after}%"
        echo "Freed: ${freed}%"
    fi
}

# Main function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help)
                echo "Usage: $0 [--dry-run] [--verbose] [--help]"
                echo "  --dry-run  : Show what would be done without making changes"
                echo "  --verbose  : Show detailed output"
                echo "  --help     : Show this help message"
                exit 0
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    log "INFO" "Starting automated cleanup"
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN MODE - No changes will be made"
    fi
    
    # Check disk space before
    local before_disk
    before_disk=$(check_disk_space | tail -1)
    
    # Perform cleanup operations
    if [ "$APT_CACHE_CLEAN" = true ]; then
        clean_apt_cache
    fi
    
    if [ "$JOURNAL_CLEAN" = true ]; then
        clean_journal
    fi
    
    if [ "$OLD_LOGS_CLEAN" = true ]; then
        clean_old_logs
    fi
    
    if [ "$TEMP_FILES_CLEAN" = true ]; then
        clean_temp_files
    fi
    
    # Additional cleanup tasks
    clean_old_kernels
    clean_thumbnails
    clean_app_caches
    
    # Show summary
    show_summary "$before_disk"
    
    log "INFO" "Automated cleanup completed"
}

# Run main function
main "$@"