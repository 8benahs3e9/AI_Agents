#!/usr/bin/env python3
"""asterisk_runner.py — Runbook Toolkit Integration for Asterisk Verification"""

import subprocess
import json
import sys
import os
from pathlib import Path

def run_asterisk_verification():
    """Run the Asterisk verification script and return results"""
    script_path = "/home/user/AI_Agents/runbook_toolkit/asterisk_local_checker.py"
    artifacts_dir = "/tmp/artifacts"
    
    # Run the verification script
    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse the JSON output from the script
        output_lines = result.stdout.split('\n')
        json_start = None
        for i, line in enumerate(output_lines):
            if line.strip() == "=== JSON Output ===":
                json_start = i + 1
                break
        
        if json_start:
            json_output = '\n'.join(output_lines[json_start:])
            verification_results = json.loads(json_output)
            
            # Save results to artifacts directory
            results_file = os.path.join(artifacts_dir, "asterisk_verification_results.json")
            with open(results_file, 'w') as f:
                json.dump(verification_results, f, indent=2)
            
            # Create toolkit-style summary
            summary = {
                "status": "done" if verification_results["overall_status"] in ["healthy", "minor_issues"] else "issues_found",
                "operation": "asterisk_verification",
                "results": verification_results,
                "artifacts": {
                    "verification_results": results_file
                },
                "timestamp": "2026-08-16",
                "tool_call_savings": "Used integrated script instead of 15+ individual tool calls"
            }
            
            return summary
        else:
            return {
                "status": "error",
                "error": "Could not parse JSON output from verification script",
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "Verification script timed out"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def main():
    """Main execution function"""
    print("=== Runbook Toolkit: Asterisk Verification ===")
    print()
    
    # Run verification
    summary = run_asterisk_verification()
    
    # Output results
    print(json.dumps(summary, indent=2))
    
    # Return appropriate exit code
    if summary["status"] == "done":
        print("\n✅ Asterisk verification completed successfully")
        return 0
    else:
        print(f"\n❌ Asterisk verification failed: {summary.get('error', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())