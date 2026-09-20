#!/usr/bin/env python3
"""__main__.py — CLI Entry Point"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def cmd_execute(args):
    from tranche_processor import TrancheProcessor
    processor = TrancheProcessor(
        plan_path=args.plan, 
        artifacts_dir=args.artifacts_dir,
        enable_caching=not args.no_cache,
        enable_metrics=not args.no_metrics,
        enable_parallel=args.parallel
    )
    summary = processor.execute()
    print(json.dumps(summary, indent=2))
    if summary.get("status") not in ("done", "awaiting_approval"):
        sys.exit(1)

def cmd_verify_audit(args):
    from audit_chain import AuditLogger
    logger = AuditLogger(artifacts_dir=args.artifacts_dir)
    if logger.verify_chain():
        print("✓ Audit log verified — chain intact.")
    else:
        print("✗ Audit log verification FAILED.")
        sys.exit(1)

def cmd_scan_secrets(args):
    from secret_scanner import SecretScanner
    scanner = SecretScanner()

    if os.path.isdir(args.path):
        results = scanner.scan_directory(args.path)
        total = sum(r.get("total_secrets", 0) for r in results)
        print(f"Scanned directory: {args.path}")
        print(f"Files with secrets: {len(results)}")
        print(f"Total secrets found: {total}")
        for r in results:
            print(f"  {r['file']}: {r['total_secrets']} secrets")
            for s in r["secrets_found"]:
                print(f"    offset={s['offset_start']} type={s['pattern_matched']}")
    else:
        report = scanner.scan_file(args.path)
        print(json.dumps(report, indent=2))

    total = sum(r.get("total_secrets", 0) for r in results) if os.path.isdir(args.path) else (report.get("total_secrets", 0) if not os.path.isdir(args.path) else 0)
    if total > 0 or (not os.path.isdir(args.path) and report.get("total_secrets", 0) > 0):
        sys.exit(1)

def cmd_verify_manifest(args):
    from manifest_signer import ManifestSigner
    manifest_path = args.manifest or os.path.join(args.artifacts_dir, "change_manifest.json")
    signer = ManifestSigner(artifacts_dir=args.artifacts_dir, gpg_key_id=args.gpg_key)

    sig_ok = signer.verify(manifest_path)
    digest_ok = signer.verify_digest(manifest_path)

    print(f"Signature valid: {'✓' if sig_ok else '✗'}")
    print(f"Digest matches:  {'✓' if digest_ok else '✗'}")

    if not (sig_ok and digest_ok):
        sys.exit(1)

def cmd_state_show(args):
    from state_manager import StateManager
    import yaml
    state_path = os.path.join(args.artifacts_dir, "STATE.md")
    mgr = StateManager(state_path)
    state = mgr.read()
    print(yaml.dump(state, default_flow_style=False))

def cmd_sign_manifest(args):
    from manifest_signer import ManifestSigner
    manifest_path = args.manifest or os.path.join(args.artifacts_dir, "change_manifest.json")
    signer = ManifestSigner(artifacts_dir=args.artifacts_dir, gpg_key_id=args.gpg_key)

    try:
        sig_meta = signer.sign(manifest_path)
        print(f"✓ Manifest signed successfully")
        print(f"  Algorithm: {sig_meta['algorithm']}")
        print(f"  Key ID: {sig_meta['key_id']}")
        print(f"  Digest: {sig_meta['digest']}")
    except Exception as e:
        print(f"✗ Signing failed: {e}")
        sys.exit(1)



def cmd_show_metrics(args):
    from metrics_collector import MetricsCollector
    metrics = MetricsCollector()
    
    if args.metrics_file:
        # Load specific metrics file
        try:
            with open(args.metrics_file, "r") as fh:
                data = json.load(fh)
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"✗ Failed to load metrics file: {e}")
            sys.exit(1)
    else:
        # Show optimization suggestions
        suggestions = metrics.get_optimization_suggestions()
        print("Optimization Suggestions:")
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("  No specific suggestions at this time.")

def cmd_health_check(args):
    try:
        from toolkit_health import ToolkitHealthChecker
    except ImportError:
        print("✗ toolkit_health module not found. Please ensure toolkit_health.py is in the toolkit directory.")
        sys.exit(1)
    
    checker = ToolkitHealthChecker(args.toolkit_path)
    report = checker.generate_report()
    
    print(f"Overall Status: {report['overall_status'].upper()}")
    print(f"Healthy: {report['healthy']}/{report['total_checks']}")
    print(f"Warnings: {report['warnings']}/{report['total_checks']}")
    print(f"Errors: {report['errors']}/{report['total_checks']}")
    
    if args.verbose:
        print("\nDetailed Results:")
        for check in report['checks']:
            status_symbol = "✓" if check['status'] == "healthy" else "⚠" if check['status'] == "warning" else "✗"
            print(f"  {status_symbol} {check['component']}: {check['message']}")
            if check.get('details'):
                print(f"      Details: {check['details']}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {args.output}")
    
    if report['errors'] > 0:
        sys.exit(1)

def cmd_generate_template(args):
    from template_generator import TemplateGenerator
    generator = TemplateGenerator()
    
    if args.template_type == "system-update":
        output = args.output or "/tmp/system_update_template.json"
        path = generator.generate_system_update_template(output)
        print(f"Generated system update template: {path}")
    
    elif args.template_type == "log-cleanup":
        output = args.output or "/tmp/log_cleanup_template.json"
        path = generator.generate_log_cleanup_template(output)
        print(f"Generated log cleanup template: {path}")
    
    elif args.template_type == "service-restart":
        if not args.services:
            print("✗ --services required for service-restart type")
            sys.exit(1)
        output = args.output or "/tmp/service_restart_template.json"
        path = generator.generate_service_restart_template(output, args.services)
        print(f"Generated service restart template: {path}")
    
    elif args.template_type == "backup":
        if not args.backup_dirs:
            print("✗ --backup-dirs required for backup type")
            sys.exit(1)
        output = args.output or "/tmp/backup_template.json"
        path = generator.generate_backup_template(output, args.backup_dirs)
        print(f"Generated backup template: {path}")

def main():
    parser = argparse.ArgumentParser(prog="runbook_toolkit", description="AI Agent Runbook v2.1 — Companion Automation Toolkit with Health Monitoring")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    p_exec = subparsers.add_parser("execute", help="Run full plan lifecycle")
    p_exec.add_argument("--plan", required=True, help="Path to PLAN.json")
    p_exec.add_argument("--artifacts-dir", required=True, help="Artifacts directory")
    p_exec.add_argument("--no-cache", action="store_true", help="Disable caching")
    p_exec.add_argument("--no-metrics", action="store_true", help="Disable metrics collection")
    p_exec.add_argument("--parallel", action="store_true", help="Enable parallel processing of independent operations")
    p_exec.set_defaults(func=cmd_execute)

    p_audit = subparsers.add_parser("verify-audit", help="Verify audit log hash chain")
    p_audit.add_argument("--artifacts-dir", required=True, help="Artifacts directory")
    p_audit.set_defaults(func=cmd_verify_audit)

    p_scan = subparsers.add_parser("scan-secrets", help="Scan for secrets in files")
    p_scan.add_argument("--path", required=True, help="File or directory to scan")
    p_scan.set_defaults(func=cmd_scan_secrets)

    p_manifest = subparsers.add_parser("verify-manifest", help="Verify manifest signature")
    p_manifest.add_argument("--artifacts-dir", required=True, help="Artifacts directory")
    p_manifest.add_argument("--manifest", help="Path to manifest (default: <artifacts>/change_manifest.json)")
    p_manifest.add_argument("--gpg-key", help="GPG key ID for verification")
    p_manifest.set_defaults(func=cmd_verify_manifest)

    p_state = subparsers.add_parser("state-show", help="Display current STATE.md")
    p_state.add_argument("--artifacts-dir", required=True, help="Artifacts directory")
    p_state.set_defaults(func=cmd_state_show)

    p_sign = subparsers.add_parser("sign-manifest", help="Sign change manifest with GPG")
    p_sign.add_argument("--artifacts-dir", required=True, help="Artifacts directory")
    p_sign.add_argument("--manifest", help="Path to manifest (default: <artifacts>/change_manifest.json)")
    p_sign.add_argument("--gpg-key", required=True, help="GPG key ID for signing")
    p_sign.set_defaults(func=cmd_sign_manifest)

    p_metrics = subparsers.add_parser("show-metrics", help="Show performance metrics and optimization suggestions")
    p_metrics.add_argument("--metrics-file", help="Path to specific metrics JSON file")
    p_metrics.set_defaults(func=cmd_show_metrics)

    p_health = subparsers.add_parser("health-check", help="Run comprehensive toolkit health check")
    p_health.add_argument("--toolkit-path", default="/home/user/AI_Agents/runbook_toolkit", help="Path to runbook toolkit directory")
    p_health.add_argument("--output", help="Output file for JSON health report")
    p_health.add_argument("--verbose", action="store_true", help="Show detailed health check results")
    p_health.set_defaults(func=cmd_health_check)

    p_template = subparsers.add_parser("generate-template", help="Generate runbook templates for common tasks")
    p_template.add_argument("--type", dest="template_type", choices=["system-update", "log-cleanup", "service-restart", "backup"], 
                       help="Template type to generate")
    p_template.add_argument("--output", help="Output path for generated template")
    p_template.add_argument("--services", nargs="+", help="Services to restart (for service-restart type)")
    p_template.add_argument("--backup-dirs", nargs="+", help="Directories to backup (for backup type)")
    p_template.set_defaults(func=cmd_generate_template)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()
