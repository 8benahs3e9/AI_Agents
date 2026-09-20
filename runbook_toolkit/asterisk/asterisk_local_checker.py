#!/usr/bin/env python3
"""asterisk_local_checker.py — Local Asterisk Configuration Documentation Review"""

import subprocess
import json
import re
from typing import Dict, List, Optional
from pathlib import Path

class AsteriskLocalChecker:
    """Reviews Asterisk documentation and checks gateway configuration for Linphone connectivity"""
    
    def __init__(self, voip_config_path: str = "/home/user/voip-config"):
        self.voip_config_path = Path(voip_config_path)
        self.backend_host = "10.128.0.6"
        self.gateway_ip = "10.128.0.10"
        
    def review_documentation(self) -> Dict:
        """Review Asterisk documentation files"""
        results = {
            "documentation_files": {},
            "configuration_status": {},
            "issues": [],
            "recommendations": []
        }
        
        # Review PJSIP working configuration
        pjsip_doc = self.voip_config_path / "PJSIP_WORKING_CONFIG_2026-07-24.md"
        if pjsip_doc.exists():
            results["documentation_files"]["pjsip_config"] = str(pjsip_doc)
            pjsip_content = pjsip_doc.read_text()
            
            # Check key configuration elements
            checks = {
                "auth-1001": "auth-1001" in pjsip_content,
                "auth-1002": "auth-1002" in pjsip_content,
                "endpoint-1001": "endpoint-1001" in pjsip_content,
                "endpoint-1002": "endpoint-1002" in pjsip_content,
                "identify-1001": "identify-1001" in pjsip_content,
                "identify-1002": "identify-1002" in pjsip_content,
                "transport-udp": "transport-udp" in pjsip_content,
                "dialplan": "from-internal" in pjsip_content
            }
            
            results["configuration_status"] = checks
            
            # Check for documented issues
            if "401 Unauthorized" in pjsip_content and "RESOLVED" in pjsip_content:
                results["recommendations"].append("Documentation shows 401 issues were previously resolved")
            
            if "✅ PRODUCTION" in pjsip_content:
                results["recommendations"].append("Documentation indicates production-ready status")
                
            # Check if credentials are redacted
            if "**REDACTED**" in pjsip_content:
                results["recommendations"].append("Credentials are properly redacted in documentation")
            else:
                results["issues"].append("Credentials may not be properly redacted in documentation")
                
        else:
            results["issues"].append("PJSIP working configuration document not found")
        
        # Review quick reference
        quick_ref = self.voip_config_path / "QUICK_REFERENCE_2026-07-24.md"
        if quick_ref.exists():
            results["documentation_files"]["quick_reference"] = str(quick_ref)
            quick_content = quick_ref.read_text()
            
            if "1001" in quick_content and "1002" in quick_content:
                results["recommendations"].append("Quick reference contains both extensions")
            
            if "Instant Checklist" in quick_content:
                results["recommendations"].append("Quick reference provides instant commands")
                
        else:
            results["issues"].append("Quick reference document not found")
        
        return results
    
    def check_gateway_services(self) -> Dict:
        """Check gateway service status"""
        results = {
            "services": {},
            "firewall": {},
            "connectivity": {},
            "issues": [],
            "recommendations": []
        }
        
        # Check service status
        services = ["nginx", "radicale", "gotify", "unbound"]
        for service in services:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                status = result.stdout.strip()
                results["services"][service] = status
                
                if status != "active":
                    results["issues"].append(f"Service {service} is not active: {status}")
                else:
                    results["recommendations"].append(f"Service {service} is running")
                    
            except Exception as e:
                results["services"][service] = f"error: {str(e)}"
                results["issues"].append(f"Failed to check service {service}: {str(e)}")
        
        # Check firewall status
        try:
            result = subprocess.run(
                ["ufw", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            ufw_output = result.stdout
            
            if "Status: active" in ufw_output:
                results["firewall"]["status"] = "active"
                results["recommendations"].append("UFW firewall is active")
                
                # Check for SIP port rules
                if "5060" in ufw_output:
                    results["firewall"]["sip_rules"] = "present"
                    results["recommendations"].append("SIP port 5060 rules found in firewall")
                else:
                    results["firewall"]["sip_rules"] = "missing"
                    results["issues"].append("SIP port 5060 rules may be missing from firewall")
            else:
                results["firewall"]["status"] = "inactive"
                results["issues"].append("UFW firewall is not active")
                
        except Exception as e:
            results["firewall"]["status"] = f"error: {str(e)}"
            results["issues"].append(f"Failed to check firewall: {str(e)}")
        
        # Check backend connectivity
        try:
            result = subprocess.run(
                ["ping", "-c", "3", self.backend_host],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                results["connectivity"]["backend_ping"] = "success"
                results["recommendations"].append(f"Backend {self.backend_host} is reachable via ping")
                
                # Parse ping stats
                if "0% packet loss" in result.stdout:
                    results["connectivity"]["packet_loss"] = "0%"
                else:
                    # Extract packet loss percentage
                    match = re.search(r'(\d+)% packet loss', result.stdout)
                    if match:
                        results["connectivity"]["packet_loss"] = f"{match.group(1)}%"
                        results["issues"].append(f"Packet loss to backend: {match.group(1)}%")
            else:
                results["connectivity"]["backend_ping"] = "failed"
                results["issues"].append(f"Cannot ping backend {self.backend_host}")
                
        except Exception as e:
            results["connectivity"]["backend_ping"] = f"error: {str(e)}"
            results["issues"].append(f"Failed to ping backend: {str(e)}")
        
        # Check SIP port connectivity
        try:
            result = subprocess.run(
                ["nc", "-zvu", self.backend_host, "5060"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                results["connectivity"]["sip_port"] = "open"
                results["recommendations"].append(f"SIP port 5060 on backend {self.backend_host} is accessible")
            else:
                results["connectivity"]["sip_port"] = "closed"
                results["issues"].append(f"SIP port 5060 on backend {self.backend_host} is not accessible")
                
        except Exception as e:
            results["connectivity"]["sip_port"] = f"error: {str(e)}"
            results["issues"].append(f"Failed to check SIP port: {str(e)}")
        
        return results
    
    def check_ssh_access(self) -> Dict:
        """Check SSH access to backend"""
        results = {
            "ssh_status": "unknown",
            "ssh_key_configured": False,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Try SSH connection
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", self.backend_host, "echo SSH_TEST"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "SSH_TEST" in result.stdout:
                results["ssh_status"] = "working"
                results["ssh_key_configured"] = True
                results["recommendations"].append("SSH key authentication to backend is working")
            else:
                results["ssh_status"] = "not_working"
                results["ssh_key_configured"] = False
                results["issues"].append("SSH key authentication to backend is not working")
                results["recommendations"].append("Configure SSH key authentication for backend access")
                
        except Exception as e:
            results["ssh_status"] = f"error: {str(e)}"
            results["ssh_key_configured"] = False
            results["issues"].append(f"SSH connection failed: {str(e)}")
        
        # Check for SSH keys
        ssh_dir = Path.home() / ".ssh"
        if ssh_dir.exists():
            private_keys = list(ssh_dir.glob("id_*")) + list(ssh_dir.glob("google_compute_*"))
            if private_keys:
                results["recommendations"].append(f"Found {len(private_keys)} SSH private key(s) in ~/.ssh")
            else:
                results["issues"].append("No SSH private keys found in ~/.ssh")
        else:
            results["issues"].append("SSH directory ~/.ssh does not exist")
        
        return results
    
    def generate_summary(self) -> Dict:
        """Generate comprehensive summary of Asterisk configuration status"""
        summary = {
            "timestamp": "2026-08-16",
            "backend_host": self.backend_host,
            "gateway_ip": self.gateway_ip,
            "overall_status": "unknown",
            "documentation": self.review_documentation(),
            "gateway": self.check_gateway_services(),
            "ssh_access": self.check_ssh_access(),
            "linphone_readiness": {
                "extension_1001": "unknown",
                "extension_1002": "unknown"
            },
            "recommendations": [],
            "immediate_actions": []
        }
        
        # Collect all issues and recommendations
        all_issues = []
        all_recommendations = []
        
        for category in ["documentation", "gateway", "ssh_access"]:
            if category in summary:
                if "issues" in summary[category]:
                    all_issues.extend(summary[category]["issues"])
                if "recommendations" in summary[category]:
                    all_recommendations.extend(summary[category]["recommendations"])
        
        # Determine overall status
        if not all_issues:
            summary["overall_status"] = "healthy"
        elif len(all_issues) <= 2:
            summary["overall_status"] = "minor_issues"
        else:
            summary["overall_status"] = "issues_found"
        
        # Assess Linphone readiness based on documentation
        config_status = summary["documentation"].get("configuration_status", {})
        
        if config_status.get("auth-1001") and config_status.get("endpoint-1001") and config_status.get("identify-1001"):
            summary["linphone_readiness"]["extension_1001"] = "configured"
        else:
            summary["linphone_readiness"]["extension_1001"] = "not_configured"
        
        if config_status.get("auth-1002") and config_status.get("endpoint-1002") and config_status.get("identify-1002"):
            summary["linphone_readiness"]["extension_1002"] = "configured"
        else:
            summary["linphone_readiness"]["extension_1002"] = "not_configured"
        
        # Generate immediate actions
        if summary["ssh_access"]["ssh_status"] != "working":
            summary["immediate_actions"].append("Configure SSH key authentication for backend access")
        
        if summary["gateway"]["connectivity"].get("sip_port") != "open":
            summary["immediate_actions"].append("Check SIP port 5060 accessibility and firewall rules")
        
        if summary["linphone_readiness"]["extension_1001"] == "configured" and summary["linphone_readiness"]["extension_1002"] == "configured":
            summary["immediate_actions"].append("Test Linphone registration with extensions 1001 and 1002")
        
        summary["issues"] = all_issues
        summary["recommendations"] = all_recommendations
        
        return summary

def main():
    """Main function for standalone execution"""
    import sys
    
    checker = AsteriskLocalChecker()
    
    print("=== Asterisk Configuration Documentation Review ===")
    print(f"VoIP Config Path: {checker.voip_config_path}")
    print(f"Backend Host: {checker.backend_host}")
    print(f"Gateway IP: {checker.gateway_ip}")
    print()
    
    # Generate comprehensive summary
    summary = checker.generate_summary()
    
    print("1. Overall Status:")
    print(f"   Status: {summary['overall_status'].upper()}")
    print()
    
    print("2. Linphone Extension Readiness:")
    for ext, status in summary["linphone_readiness"].items():
        status_icon = "✅" if status == "configured" else "❌"
        print(f"   {ext}: {status_icon} ({status})")
    print()
    
    print("3. Documentation Review:")
    doc_status = summary["documentation"]["configuration_status"]
    for config_item, status in doc_status.items():
        status_icon = "✅" if status else "❌"
        print(f"   {config_item}: {status_icon}")
    print()
    
    print("4. Gateway Services:")
    for service, status in summary["gateway"]["services"].items():
        status_icon = "✅" if status == "active" else "❌"
        print(f"   {service}: {status_icon} ({status})")
    print()
    
    print("5. Connectivity:")
    connectivity = summary["gateway"]["connectivity"]
    print(f"   Backend Ping: {connectivity.get('backend_ping', 'unknown')}")
    print(f"   SIP Port 5060: {connectivity.get('sip_port', 'unknown')}")
    print()
    
    print("6. SSH Access:")
    ssh_info = summary["ssh_access"]
    print(f"   SSH Status: {ssh_info['ssh_status']}")
    print(f"   SSH Key Configured: {ssh_info['ssh_key_configured']}")
    print()
    
    print("7. Issues Found:")
    if summary["issues"]:
        for issue in summary["issues"]:
            print(f"   ❌ {issue}")
    else:
        print("   ✅ No issues found")
    print()
    
    print("8. Immediate Actions Required:")
    if summary["immediate_actions"]:
        for action in summary["immediate_actions"]:
            print(f"   → {action}")
    else:
        print("   ✅ No immediate actions required")
    print()
    
    print("9. Additional Recommendations:")
    if summary["recommendations"]:
        for rec in summary["recommendations"][:5]:  # Show top 5
            print(f"   • {rec}")
    else:
        print("   ✅ No additional recommendations")
    print()
    
    # Output JSON for runbook integration
    print("=== JSON Output ===")
    print(json.dumps(summary, indent=2))
    
    # Return appropriate exit code
    if summary["overall_status"] == "healthy":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()