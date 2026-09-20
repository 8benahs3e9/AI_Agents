#!/usr/bin/env python3
"""template_generator.py — Runbook Template Generator

Generates optimized PLAN.json templates for common automation tasks.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timezone

class TemplateGenerator:
    """Generates runbook templates for common automation scenarios."""
    
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
    
    def generate_system_update_template(self, output_path: str) -> str:
        """Generate template for system package updates."""
        template = {
            "goal": "System Package Update",
            "description": "Update system packages and perform security updates",
            "version": "1.0",
            "toolkit_location": "/home/user/AI_Agents/runbook_toolkit/",
            
            "scope": {
                "include": ["/etc/apt/sources.list", "/var/lib/apt/lists/*"],
                "exclude": ["/boot/*", "/proc/*", "/sys/*"]
            },
            
            "pre_flight_checks": {
                "resource_validation": True,
                "disk_space_threshold": "2GB",
                "internet_connectivity": True
            },
            
            "operations": [
                {
                    "type": "apt_update",
                    "description": "Update package lists",
                    "command": "apt-get update"
                },
                {
                    "type": "apt_upgrade",
                    "description": "Upgrade installed packages",
                    "command": "apt-get upgrade -y"
                },
                {
                    "type": "apt_autoremove",
                    "description": "Remove unused packages",
                    "command": "apt-get autoremove -y"
                },
                {
                    "type": "apt_clean",
                    "description": "Clean package cache",
                    "command": "apt-get clean"
                }
            ],
            
            "verification": {
                "post_execution": [
                    {
                        "type": "command_check",
                        "description": "Verify system is up to date",
                        "command": "apt list --upgradable"
                    }
                ]
            },
            
            "rollback": {
                "enabled": True,
                "automatic_on_failure": True,
                "backup_location": "/var/backups/apt/",
                "backup_retention": "7 days"
            },
            
            "audit": {
                "logging": True,
                "cryptographic_signing": False,
                "manifest_generation": True
            },
            
            "optimization": {
                "enable_caching": True,
                "enable_metrics": True,
                "enable_parallel": False
            }
        }
        
        return self._save_template(template, output_path)
    
    def generate_log_cleanup_template(self, output_path: str) -> str:
        """Generate template for log cleanup operations."""
        template = {
            "goal": "System Log Cleanup",
            "description": "Clean up old log files to free disk space",
            "version": "1.0",
            "toolkit_location": "/home/user/AI_Agents/runbook_toolkit/",
            
            "scope": {
                "include": ["/var/log/*.log", "/var/log/*.gz", "/var/log/*.bz2"],
                "exclude": ["/var/log/journal/*", "/var/log/syslog"]
            },
            
            "pre_flight_checks": {
                "resource_validation": True,
                "disk_space_threshold": "1GB"
            },
            
            "operations": [
                {
                    "type": "file_delete",
                    "description": "Remove compressed logs older than 30 days",
                    "files": ["/var/log/*.gz", "/var/log/*.bz2"],
                    "condition": "mtime > 30"
                },
                {
                    "type": "journal_cleanup",
                    "description": "Clean systemd journal (7-day retention)",
                    "command": "journalctl --vacuum-time=7d"
                },
                {
                    "type": "apt_clean",
                    "description": "Clean APT cache",
                    "command": "apt-get clean"
                }
            ],
            
            "verification": {
                "post_execution": [
                    {
                        "type": "disk_space_check",
                        "description": "Verify disk space improvement",
                        "min_free_gb": 1
                    }
                ]
            },
            
            "rollback": {
                "enabled": False
            },
            
            "audit": {
                "logging": True,
                "cryptographic_signing": False
            },
            
            "optimization": {
                "enable_caching": True,
                "enable_metrics": True
            }
        }
        
        return self._save_template(template, output_path)
    
    def generate_service_restart_template(self, output_path: str, services: List[str]) -> str:
        """Generate template for service restart operations."""
        template = {
            "goal": "Service Restart",
            "description": f"Restart specified services: {', '.join(services)}",
            "version": "1.0",
            "toolkit_location": "/home/user/AI_Agents/runbook_toolkit/",
            
            "scope": {
                "include": ["/etc/systemd/system/*"],
                "exclude": []
            },
            
            "pre_flight_checks": {
                "resource_validation": True,
                "service_check": True
            },
            
            "operations": [
                {
                    "type": "service_restart",
                    "description": f"Restart {service}",
                    "service": service,
                    "restart_command": f"systemctl restart {service}"
                } for service in services
            ],
            
            "verification": {
                "post_execution": [
                    {
                        "type": "service_status",
                        "description": "Verify all services are running",
                        "services": services,
                        "expected_state": "active"
                    }
                ]
            },
            
            "rollback": {
                "enabled": True,
                "automatic_on_failure": True
            },
            
            "audit": {
                "logging": True,
                "cryptographic_signing": False
            },
            
            "optimization": {
                "enable_caching": True,
                "enable_metrics": True,
                "enable_parallel": True
            }
        }
        
        return self._save_template(template, output_path)
    
    def generate_backup_template(self, output_path: str, backup_dirs: List[str]) -> str:
        """Generate template for backup operations."""
        template = {
            "goal": "System Backup",
            "description": f"Backup specified directories: {', '.join(backup_dirs)}",
            "version": "1.0",
            "toolkit_location": "/home/user/AI_Agents/runbook_toolkit/",
            
            "scope": {
                "include": backup_dirs,
                "exclude": ["/proc/*", "/sys/*", "/dev/*", "/tmp/*"]
            },
            
            "pre_flight_checks": {
                "resource_validation": True,
                "disk_space_threshold": "5GB"
            },
            
            "operations": [
                {
                    "type": "directory_backup",
                    "description": f"Backup {backup_dir}",
                    "source": backup_dir,
                    "destination": f"/var/backups/{os.path.basename(backup_dir.rstrip('/'))}_{datetime.now().strftime('%Y%m%d')}",
                    "compression": True
                } for backup_dir in backup_dirs
            ],
            
            "verification": {
                "post_execution": [
                    {
                        "type": "backup_integrity",
                        "description": "Verify backup integrity",
                        "check_type": "file_count"
                    }
                ]
            },
            
            "rollback": {
                "enabled": False
            },
            
            "audit": {
                "logging": True,
                "cryptographic_signing": True,
                "manifest_generation": True
            },
            
            "optimization": {
                "enable_caching": False,
                "enable_metrics": True
            }
        }
        
        return self._save_template(template, output_path)
    
    def _save_template(self, template: Dict, output_path: str) -> str:
        """Save template to file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(template, f, indent=2)
        return output_path

def main():
    """CLI entry point for template generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Runbook Template Generator")
    parser.add_argument("--type", choices=["system-update", "log-cleanup", "service-restart", "backup"], 
                       help="Template type to generate")
    parser.add_argument("--output", help="Output path for generated template")
    parser.add_argument("--services", nargs="+", help="Services to restart (for service-restart type)")
    parser.add_argument("--backup-dirs", nargs="+", help="Directories to backup (for backup type)")
    
    args = parser.parse_args()
    
    generator = TemplateGenerator()
    
    if args.type == "system-update":
        output = args.output or "/tmp/system_update_template.json"
        path = generator.generate_system_update_template(output)
        print(f"Generated system update template: {path}")
    
    elif args.type == "log-cleanup":
        output = args.output or "/tmp/log_cleanup_template.json"
        path = generator.generate_log_cleanup_template(output)
        print(f"Generated log cleanup template: {path}")
    
    elif args.type == "service-restart":
        if not args.services:
            print("Error: --services required for service-restart type")
            return
        output = args.output or "/tmp/service_restart_template.json"
        path = generator.generate_service_restart_template(output, args.services)
        print(f"Generated service restart template: {path}")
    
    elif args.type == "backup":
        if not args.backup_dirs:
            print("Error: --backup-dirs required for backup type")
            return
        output = args.output or "/tmp/backup_template.json"
        path = generator.generate_backup_template(output, args.backup_dirs)
        print(f"Generated backup template: {path}")

if __name__ == "__main__":
    main()