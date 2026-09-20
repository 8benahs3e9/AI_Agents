#!/usr/bin/env python3
"""asterisk_troubleshooter.py — Advanced Asterisk PJSIP Troubleshooting for Linphone Issues"""

import subprocess
import json
import re
import sys
from typing import Dict, List, Optional
from pathlib import Path

class AsteriskTroubleshooter:
    """Advanced troubleshooting for Asterisk PJSIP issues"""
    
    def __init__(self, voip_config_path: str = "/home/user/voip-config"):
        self.voip_config_path = Path(voip_config_path)
        self.backend_host = "10.128.0.6"
        
    def analyze_documentation_issues(self) -> Dict:
        """Analyze documentation for known issues and solutions"""
        results = {
            "known_issues": [],
            "documented_solutions": [],
            "configuration_checklist": {}
        }
        
        # Read troubleshooting guide
        troubleshooting_doc = self.voip_config_path / "TROUBLESHOOTING_GUIDE_2026-07-24.md"
        if troubleshooting_doc.exists():
            content = troubleshooting_doc.read_text()
            
            # Look for 401 Unauthorized solutions
            if "401 Unauthorized" in content and "RESOLVED" in content:
                results["documented_solutions"].append({
                    "issue": "401 Unauthorized",
                    "documented_fix": "AOR name mismatch and missing IP identification blocks"
                })
            
            # Look for user not found solutions
            if "user not found" in content.lower():
                results["documented_solutions"].append({
                    "issue": "User not found",
                    "documented_fix": content[content.lower().find("user not found"):content.lower().find("user not found")+200]
                })
        
        # Read PJSIP working config
        pjsip_doc = self.voip_config_path / "PJSIP_WORKING_CONFIG_2026-07-24.md"
        if pjsip_doc.exists():
            content = pjsip_doc.read_text()
            
            # Extract configuration checklist
            checklist = {
                "auth_1001": "auth-1001" in content,
                "auth_1002": "auth-1002" in content,
                "endpoint_1001": "endpoint-1001" in content,
                "endpoint_1002": "endpoint-1002" in content,
                "aor_1001": "[1001]" in content and "type=aor" in content,
                "aor_1002": "[1002]" in content and "type=aor" in content,
                "identify_1001": "identify-1001" in content,
                "identify_1002": "identify-1002" in content,
                "dialplan_1001": "exten => 1001" in content,
                "dialplan_1002": "exten => 1002" in content
            }
            results["configuration_checklist"] = checklist
        
        return results
    
    def diagnose_1001_call_failure(self) -> Dict:
        """Diagnose why calls to connected user 1001 fail with 'user not found'"""
        diagnosis = {
            "issue": "User 1001 connected but calls fail with 'user not found'",
            "possible_causes": [],
            "diagnostic_steps": [],
            "likely_cause": "",
            "fix_recommendations": []
        }
        
        # Possible causes for "user not found" when user is connected
        diagnosis["possible_causes"] = [
            "Dialplan extension mismatch",
            "Context mapping issue",
            "Endpoint not in correct context",
            "Extension number format mismatch",
            "Dialplan not reloaded after changes"
        ]
        
        # Diagnostic steps
        diagnosis["diagnostic_steps"] = [
            "Check if extension 1001 is in the correct dialplan context",
            "Verify dialplan extension format matches exactly",
            "Check if endpoint is in the 'from-internal' context",
            "Verify dialplan has been reloaded: asterisk -rx 'dialplan reload'",
            "Check if calls are using the correct context"
        ]
        
        # Most likely cause based on common issues
        diagnosis["likely_cause"] = "Dialplan configuration issue - extension 1001 may not be properly configured in the dialplan or context mismatch"
        
        # Fix recommendations
        diagnosis["fix_recommendations"] = [
            "Check /etc/asterisk/extensions.conf for extension 1001",
            "Verify format: exten => 1001,1,Dial(PJSIP/endpoint-1001,20)",
            "Ensure extension is in [from-internal] context",
            "Reload dialplan: asterisk -rx 'dialplan reload'",
            "Test with: asterisk -rx 'dialplan show from-internal'"
        ]
        
        return diagnosis
    
    def diagnose_1002_unauthorized(self) -> Dict:
        """Diagnose why user 1002 gets 'unauthorized' error"""
        diagnosis = {
            "issue": "User 1002 cannot connect - unauthorized error",
            "possible_causes": [],
            "diagnostic_steps": [],
            "likely_cause": "",
            "fix_recommendations": []
        }
        
        # Possible causes for unauthorized error
        diagnosis["possible_causes"] = [
            "Incorrect password in Linphone configuration",
            "Auth block not properly configured",
            "Endpoint not referencing correct auth block",
            "AOR name mismatch",
            "IP identification not configured for gateway IP"
        ]
        
        # Diagnostic steps
        diagnosis["diagnostic_steps"] = [
            "Verify password in Linphone matches Asterisk configuration",
            "Check auth-1002 block exists in pjsip.conf",
            "Verify endpoint-1002 references auth-1002",
            "Check AOR block is named exactly '1002' (not 'aor-1002')",
            "Verify identify-1002 block exists with match=10.128.0.10",
            "Check Asterisk logs: tail -f /var/log/asterisk/messages.log.skype"
        ]
        
        # Most likely cause based on documentation showing 401 issues were previously fixed
        diagnosis["likely_cause"] = "Authentication configuration issue - likely password mismatch or auth block configuration problem"
        
        # Fix recommendations
        diagnosis["fix_recommendations"] = [
            "Check actual password in /etc/asterisk/pjsip.conf [auth-1002] section",
            "Verify Linphone 1002 configuration uses correct password",
            "Check endpoint-1002 has: auth=auth-1002",
            "Verify AOR is named [1002] not [aor-1002]",
            "Ensure identify-1002 exists with: match=10.128.0.10",
            "Reload PJSIP: asterisk -rx 'pjsip reload'",
            "Test registration with sipsak if available"
        ]
        
        return diagnosis
    
    def generate_diagnostic_commands(self) -> Dict:
        """Generate specific diagnostic commands for backend server"""
        commands = {
            "status_checks": [
                "asterisk -rx 'pjsip show endpoints'",
                "asterisk -rx 'pjsip show registrations'",
                "asterisk -rx 'pjsip show auths'",
                "asterisk -rx 'pjsip show aors'",
                "asterisk -rx 'pjsip show identifies'"
            ],
            "configuration_checks": [
                "cat /etc/asterisk/pjsip.conf | grep -A 5 'auth-1002'",
                "cat /etc/asterisk/pjsip.conf | grep -A 5 'endpoint-1002'",
                "cat /etc/asterisk/pjsip.conf | grep -A 3 '\\[1002\\]'",
                "cat /etc/asterisk/extensions.conf | grep -A 2 'exten => 1002'"
            ],
            "log_analysis": [
                "tail -50 /var/log/asterisk/messages.log.skype | grep -i '1002'",
                "tail -50 /var/log/asterisk/messages.log.skype | grep -i 'unauthorized'",
                "tail -50 /var/log/asterisk/messages.log.skype | grep -i 'registration'"
            ],
            "reload_commands": [
                "asterisk -rx 'pjsip reload'",
                "asterisk -rx 'dialplan reload'"
            ]
        }
        
        return commands
    
    def create_troubleshooting_action_plan(self) -> Dict:
        """Create comprehensive action plan for both issues"""
        action_plan = {
            "priority_1_immediate": [],
            "priority_2_configuration": [],
            "priority_3_verification": []
        }
        
        # Priority 1: Immediate fixes for 1002 authentication
        action_plan["priority_1_immediate"] = [
            "Check actual password for extension 1002 in /etc/asterisk/pjsip.conf",
            "Verify Linphone 1002 configuration uses correct password",
            "Check auth-1002 block configuration",
            "Test 1002 registration with correct credentials"
        ]
        
        # Priority 2: Configuration fixes for 1001 dialplan
        action_plan["priority_2_configuration"] = [
            "Verify dialplan configuration for extension 1001",
            "Check context mapping for endpoint-1001",
            "Ensure extension format matches in dialplan",
            "Reload dialplan configuration"
        ]
        
        # Priority 3: Verification and testing
        action_plan["priority_3_verification"] = [
            "Test call from 1001 to 1002",
            "Test call from 1002 to 1001",
            "Verify audio quality for both directions",
            "Check registration status for both extensions"
        ]
        
        return action_plan
    
    def generate_troubleshooting_report(self) -> Dict:
        """Generate comprehensive troubleshooting report"""
        report = {
            "timestamp": "2026-08-16",
            "issues_identified": {
                "user_1001": "Connected but calls fail with 'user not found'",
                "user_1002": "Cannot connect - unauthorized error"
            },
            "documentation_analysis": self.analyze_documentation_issues(),
            "diagnoses": {
                "user_1001": self.diagnose_1001_call_failure(),
                "user_1002": self.diagnose_1002_unauthorized()
            },
            "diagnostic_commands": self.generate_diagnostic_commands(),
            "action_plan": self.create_troubleshooting_action_plan(),
            "next_steps": []
        }
        
        # Generate next steps based on analysis
        config_checklist = report["documentation_analysis"]["configuration_checklist"]
        
        if not config_checklist.get("dialplan_1001"):
            report["next_steps"].append("URGENT: Extension 1001 missing from dialplan configuration")
        
        if not config_checklist.get("auth_1002"):
            report["next_steps"].append("URGENT: Auth block for extension 1002 may be missing")
        
        report["next_steps"].append("Run diagnostic commands on backend server (10.128.0.6)")
        report["next_steps"].append("Check Asterisk logs for specific error messages")
        report["next_steps"].append("Implement fixes based on diagnostic results")
        
        return report

def main():
    """Main function for standalone execution"""
    troubleshooter = AsteriskTroubleshooter()
    
    print("=== Asterisk PJSIP Troubleshooting Report ===")
    print("Issues: User 1001 call failures, User 1002 unauthorized")
    print()
    
    # Generate comprehensive report
    report = troubleshooter.generate_troubleshooting_report()
    
    print("1. ISSUES IDENTIFIED:")
    for user, issue in report["issues_identified"].items():
        print(f"   {user}: {issue}")
    print()
    
    print("2. USER 1001 DIAGNOSIS:")
    diag_1001 = report["diagnoses"]["user_1001"]
    print(f"   Issue: {diag_1001['issue']}")
    print(f"   Likely Cause: {diag_1001['likely_cause']}")
    print("   Top 3 Fix Recommendations:")
    for i, fix in enumerate(diag_1001['fix_recommendations'][:3], 1):
        print(f"     {i}. {fix}")
    print()
    
    print("3. USER 1002 DIAGNOSIS:")
    diag_1002 = report["diagnoses"]["user_1002"]
    print(f"   Issue: {diag_1002['issue']}")
    print(f"   Likely Cause: {diag_1002['likely_cause']}")
    print("   Top 3 Fix Recommendations:")
    for i, fix in enumerate(diag_1002['fix_recommendations'][:3], 1):
        print(f"     {i}. {fix}")
    print()
    
    print("4. DIAGNOSTIC COMMANDS (run on backend 10.128.0.6):")
    print("   Status Checks:")
    for cmd in report["diagnostic_commands"]["status_checks"][:3]:
        print(f"     • {cmd}")
    print()
    
    print("5. ACTION PLAN:")
    print("   Priority 1 (Immediate):")
    for action in report["action_plan"]["priority_1_immediate"]:
        print(f"     → {action}")
    print()
    print("   Priority 2 (Configuration):")
    for action in report["action_plan"]["priority_2_configuration"]:
        print(f"     → {action}")
    print()
    
    print("6. NEXT STEPS:")
    for step in report["next_steps"]:
        print(f"   • {step}")
    print()
    
    print("=== DETAILED REPORT ===")
    print(json.dumps(report, indent=2))
    
    # Return appropriate exit code
    if report["documentation_analysis"]["configuration_checklist"].get("dialplan_1001") and \
       report["documentation_analysis"]["configuration_checklist"].get("auth_1002"):
        print("\n✅ Configuration appears complete - focus on runtime issues")
        return 0
    else:
        print("\n⚠️ Configuration issues found - see detailed report")
        return 1

if __name__ == "__main__":
    sys.exit(main())