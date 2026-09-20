#!/usr/bin/env python3
"""asterisk_checker.py — Asterisk PJSIP Configuration Verification Module"""

import subprocess
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AsteriskEndpoint:
    name: str
    auth: str
    aors: str
    status: str
    contact: str = ""

@dataclass
class AsteriskAuth:
    name: str
    username: str
    auth_type: str

@dataclass 
class AsteriskAOR:
    name: str
    max_contacts: int
    contacts: List[str]

class AsteriskChecker:
    """Verifies Asterisk PJSIP configuration for Linphone connectivity"""
    
    def __init__(self, backend_host: str = "10.128.0.6"):
        self.backend_host = backend_host
        self.asterisk_cmd = "/usr/sbin/asterisk -rx"
        
    def execute_asterisk_command(self, command: str) -> str:
        """Execute Asterisk CLI command on backend server"""
        full_command = f"ssh {self.backend_host} '{self.asterisk_cmd} {command}'"
        try:
            result = subprocess.run(
                full_command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "ERROR: Command timeout"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def check_service_status(self) -> Dict:
        """Check if Asterisk service is running"""
        command = "systemctl status asterisk --no-pager"
        full_command = f"ssh {self.backend_host} '{command}'"
        try:
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout
            is_running = "active (running)" in output or "active" in output
            
            return {
                "status": "running" if is_running else "not_running",
                "output": output,
                "is_healthy": is_running
            }
        except Exception as e:
            return {
                "status": "error",
                "output": str(e),
                "is_healthy": False
            }
    
    def get_endpoints(self) -> List[AsteriskEndpoint]:
        """Get all PJSIP endpoints"""
        output = self.execute_asterisk_command("'pjsip show endpoints'")
        endpoints = []
        
        # Parse endpoint output
        lines = output.split('\n')
        for line in lines[1:]:  # Skip header
            if line.strip() and not line.startswith("---") and "Endpoint" not in line:
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    auth = parts[1] if len(parts) > 1 else ""
                    aors = parts[2] if len(parts) > 2 else ""
                    status = parts[3] if len(parts) > 3 else "Unknown"
                    
                    endpoints.append(AsteriskEndpoint(
                        name=name,
                        auth=auth,
                        aors=aors,
                        status=status
                    ))
        
        return endpoints
    
    def get_auth_blocks(self) -> List[AsteriskAuth]:
        """Get PJSIP authentication blocks"""
        output = self.execute_asterisk_command("'pjsip show auths'")
        auth_blocks = []
        
        lines = output.split('\n')
        for line in lines[1:]:  # Skip header
            if line.strip() and not line.startswith("---") and "Auth" not in line:
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    auth_type = parts[1] if len(parts) > 1 else ""
                    username = parts[2] if len(parts) > 2 else ""
                    
                    auth_blocks.append(AsteriskAuth(
                        name=name,
                        auth_type=auth_type,
                        username=username
                    ))
        
        return auth_blocks
    
    def get_aor_blocks(self) -> List[AsteriskAOR]:
        """Get PJSIP AOR blocks"""
        aors = []
        
        # Check specific AORs for extensions 1001 and 1002
        for extension in ["1001", "1002"]:
            output = self.execute_asterisk_command(f"'pjsip show aor {extension}'")
            
            max_contacts = 1
            contacts = []
            
            for line in output.split('\n'):
                if "MaxContacts" in line:
                    match = re.search(r'MaxContacts:\s*(\d+)', line)
                    if match:
                        max_contacts = int(match.group(1))
                if "Contact" in line and "/" in line:
                    contact = line.split()[-1]
                    contacts.append(contact)
            
            aors.append(AsteriskAOR(
                name=extension,
                max_contacts=max_contacts,
                contacts=contacts
            ))
        
        return aors
    
    def get_identify_blocks(self) -> List[Dict]:
        """Get PJSIP identify blocks"""
        output = self.execute_asterisk_command("'pjsip show identifies'")
        identifies = []
        
        lines = output.split('\n')
        for line in lines[1:]:  # Skip header
            if line.strip() and not line.startswith("---") and "Identify" not in line:
                parts = line.split()
                if len(parts) >= 3:
                    identifies.append({
                        "name": parts[0],
                        "endpoint": parts[1] if len(parts) > 1 else "",
                        "match": parts[2] if len(parts) > 2 else ""
                    })
        
        return identifies
    
    def get_registrations(self) -> List[Dict]:
        """Get current PJSIP registrations"""
        output = self.execute_asterisk_command("'pjsip show registrations'")
        registrations = []
        
        lines = output.split('\n')
        for line in lines[1:]:  # Skip header
            if line.strip() and not line.startswith("---") and "Registration" not in line:
                parts = line.split()
                if len(parts) >= 4:
                    registrations.append({
                        "aor": parts[0],
                        "status": parts[1] if len(parts) > 1 else "",
                        "contact": parts[2] if len(parts) > 2 else ""
                    })
        
        return registrations
    
    def verify_linphone_extensions(self) -> Dict:
        """Verify configuration for Linphone extensions 1001 and 1002"""
        results = {
            "extensions": {
                "1001": {"configured": False, "issues": []},
                "1002": {"configured": False, "issues": []}
            },
            "overall_status": "unknown",
            "recommendations": []
        }
        
        # Check service status
        service_status = self.check_service_status()
        results["service_status"] = service_status
        
        if not service_status["is_healthy"]:
            results["overall_status"] = "error"
            results["recommendations"].append("Asterisk service is not running - start service first")
            return results
        
        # Get endpoints
        endpoints = self.get_endpoints()
        endpoint_names = [ep.name for ep in endpoints]
        
        # Get auth blocks
        auth_blocks = self.get_auth_blocks()
        auth_names = [auth.name for auth in auth_blocks]
        
        # Get AOR blocks
        aor_blocks = self.get_aor_blocks()
        aor_names = [aor.name for aor in aor_blocks]
        
        # Get identify blocks
        identify_blocks = self.get_identify_blocks()
        
        # Check extension 1001
        ext_1001_issues = []
        
        if "endpoint-1001" not in endpoint_names:
            ext_1001_issues.append("Missing endpoint-1001")
        else:
            results["extensions"]["1001"]["configured"] = True
        
        if "auth-1001" not in auth_names:
            ext_1001_issues.append("Missing auth-1001")
        
        if "1001" not in aor_names:
            ext_1001_issues.append("Missing AOR 1001")
        
        if not any(id_block["endpoint"] == "endpoint-1001" for id_block in identify_blocks):
            ext_1001_issues.append("Missing identify block for endpoint-1001")
        
        results["extensions"]["1001"]["issues"] = ext_1001_issues
        
        # Check extension 1002
        ext_1002_issues = []
        
        if "endpoint-1002" not in endpoint_names:
            ext_1002_issues.append("Missing endpoint-1002")
        else:
            results["extensions"]["1002"]["configured"] = True
        
        if "auth-1002" not in auth_names:
            ext_1002_issues.append("Missing auth-1002")
        
        if "1002" not in aor_names:
            ext_1002_issues.append("Missing AOR 1002")
        
        if not any(id_block["endpoint"] == "endpoint-1002" for id_block in identify_blocks):
            ext_1002_issues.append("Missing identify block for endpoint-1002")
        
        results["extensions"]["1002"]["issues"] = ext_1002_issues
        
        # Check registrations
        registrations = self.get_registrations()
        registered_extensions = [reg["aor"] for reg in registrations if reg["status"] == "Registered"]
        
        results["current_registrations"] = registrations
        results["registered_extensions"] = registered_extensions
        
        # Overall status
        if results["extensions"]["1001"]["configured"] and results["extensions"]["1002"]["configured"]:
            if not ext_1001_issues and not ext_1002_issues:
                results["overall_status"] = "ready"
                results["recommendations"].append("Configuration is correct - Linphone clients should be able to register")
                
                if "1001" not in registered_extensions:
                    results["recommendations"].append("Extension 1001 is not currently registered - check Linphone client configuration")
                if "1002" not in registered_extensions:
                    results["recommendations"].append("Extension 1002 is not currently registered - check Linphone client configuration")
            else:
                results["overall_status"] = "issues_found"
                results["recommendations"].append("Configuration has issues - see extension-specific issues")
        else:
            results["overall_status"] = "not_configured"
            results["recommendations"].append("Extensions are not properly configured - review Asterisk PJSIP configuration")
        
        return results
    
    def test_connectivity(self) -> Dict:
        """Test network connectivity to Asterisk server"""
        try:
            # Test SSH connectivity
            ssh_result = subprocess.run(
                f"ssh -o ConnectTimeout=5 {self.backend_host} 'echo SSH_OK'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            ssh_ok = ssh_result.returncode == 0 and "SSH_OK" in ssh_result.stdout
            
            # Test SIP port connectivity
            sip_result = subprocess.run(
                f"nc -zvu {self.backend_host} 5060",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            sip_ok = sip_result.returncode == 0
            
            return {
                "ssh_connectivity": ssh_ok,
                "sip_port_accessible": sip_ok,
                "backend_host": self.backend_host,
                "overall_connectivity": ssh_ok and sip_ok
            }
        except Exception as e:
            return {
                "ssh_connectivity": False,
                "sip_port_accessible": False,
                "backend_host": self.backend_host,
                "overall_connectivity": False,
                "error": str(e)
            }

def main():
    """Main function for standalone execution"""
    import sys
    
    checker = AsteriskChecker()
    
    print("=== Asterisk PJSIP Configuration Check ===")
    print(f"Backend Host: {checker.backend_host}")
    print()
    
    # Test connectivity
    print("1. Testing connectivity...")
    connectivity = checker.test_connectivity()
    print(f"   SSH Connectivity: {'✅' if connectivity['ssh_connectivity'] else '❌'}")
    print(f"   SIP Port Accessible: {'✅' if connectivity['sip_port_accessible'] else '❌'}")
    print()
    
    if not connectivity['overall_connectivity']:
        print("❌ Cannot reach backend server - aborting")
        sys.exit(1)
    
    # Check configuration
    print("2. Verifying Linphone extension configuration...")
    results = checker.verify_linphone_extensions()
    
    print(f"   Overall Status: {results['overall_status'].upper()}")
    print()
    
    print("3. Extension Details:")
    for ext, details in results["extensions"].items():
        status_icon = "✅" if details["configured"] else "❌"
        print(f"   Extension {ext}: {status_icon}")
        if details["issues"]:
            for issue in details["issues"]:
                print(f"      - {issue}")
    print()
    
    print("4. Current Registrations:")
    if results["current_registrations"]:
        for reg in results["current_registrations"]:
            status_icon = "✅" if reg["status"] == "Registered" else "❌"
            print(f"   {reg['aor']}: {status_icon} ({reg['status']})")
    else:
        print("   No registrations found")
    print()
    
    print("5. Recommendations:")
    for rec in results["recommendations"]:
        print(f"   - {rec}")
    print()
    
    # Output JSON for runbook integration
    print("=== JSON Output ===")
    print(json.dumps(results, indent=2))
    
    # Return appropriate exit code
    if results["overall_status"] == "ready":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()