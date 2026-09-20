#!/usr/bin/env python3
"""
SSL Certificate Manager - Automated Certificate Renewal and Monitoring

This script provides comprehensive SSL certificate management including:
- Automated certificate renewal via certbot
- Certificate expiry monitoring and alerting
- Certificate validation and health checks
- Integration with monitoring systems
"""

import subprocess
import json
import logging
import sys
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import smtplib
from email.mime.text import MIMEText

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ssl_certificate_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class CertificateInfo:
    """Data class for certificate information."""
    domain: str
    path: str
    expiry_date: datetime
    days_until_expiry: int
    issuer: str
    status: str  # valid, expiring_soon, expired, error
    auto_renewal: bool = False


@dataclass
class RenewalResult:
    """Data class for renewal operation results."""
    domain: str
    success: bool
    message: str
    new_expiry: Optional[datetime] = None
    error: Optional[str] = None


class SSLCertificateManager:
    """Main SSL certificate management class."""
    
    def __init__(self, config_path: str = '/etc/ssl_certificate_manager/config.json'):
        self.config_path = config_path
        self.config = self._load_config()
        self.certificates: List[CertificateInfo] = []
        
    def _load_config(self) -> Dict:
        """Load configuration from file or use defaults."""
        default_config = {
            "domains": [
                "calendar.shatsie.fun",
                "connect.shatsie.fun", 
                "gotify.shatsie.fun"
            ],
            "cert_path": "/etc/letsencrypt/live",
            "renewal_threshold_days": 30,
            "email_alerts": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "your-email@gmail.com",
                "recipients": ["admin@shatsie.fun"]
            },
            "webhook_url": None,
            "dry_run": False
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load config file: {e}. Using defaults.")
        
        return default_config
    
    def get_certificate_info(self, domain: str) -> Optional[CertificateInfo]:
        """Get detailed information about a certificate."""
        cert_path = Path(f"{self.config['cert_path']}/{domain}/cert.pem")
        
        if not cert_path.exists():
            logger.error(f"Certificate file not found for {domain}: {cert_path}")
            return None
        
        try:
            # Use openssl to get certificate details
            cmd = [
                'openssl', 'x509', 
                '-in', str(cert_path),
                '-noout', 
                '-dates', 
                '-issuer'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse certificate information
            output = result.stdout
            expiry_match = re.search(r'notAfter=(.+)', output)
            issuer_match = re.search(r'issuer=(.+)', output)
            
            if not expiry_match:
                logger.error(f"Could not parse expiry date for {domain}")
                return None
            
            expiry_date = datetime.strptime(expiry_match.group(1).strip(), '%b %d %H:%M:%S %Y %Z')
            days_until_expiry = (expiry_date - datetime.now()).days
            issuer = issuer_match.group(1).strip() if issuer_match else "Unknown"
            
            # Determine certificate status
            if days_until_expiry < 0:
                status = "expired"
            elif days_until_expiry <= self.config['renewal_threshold_days']:
                status = "expiring_soon"
            else:
                status = "valid"
            
            return CertificateInfo(
                domain=domain,
                path=str(cert_path),
                expiry_date=expiry_date,
                days_until_expiry=days_until_expiry,
                issuer=issuer,
                status=status,
                auto_renewal=self._check_auto_renewal(domain)
            )
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get certificate info for {domain}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting certificate info for {domain}: {e}")
            return None
    
    def _check_auto_renewal(self, domain: str) -> bool:
        """Check if auto-renewal is configured for a domain."""
        try:
            cmd = ['certbot', 'certificates']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Check if domain appears in certbot certificates output
            return domain in result.stdout
        except subprocess.CalledProcessError:
            return False
    
    def scan_all_certificates(self) -> List[CertificateInfo]:
        """Scan all configured certificates and return their information."""
        self.certificates = []
        
        for domain in self.config['domains']:
            cert_info = self.get_certificate_info(domain)
            if cert_info:
                self.certificates.append(cert_info)
                logger.info(f"Certificate for {domain}: {cert_info.status} (expires in {cert_info.days_until_expiry} days)")
        
        return self.certificates
    
    def renew_certificate(self, domain: str, force: bool = False) -> RenewalResult:
        """Renew a certificate using certbot."""
        if self.config['dry_run']:
            logger.info(f"DRY RUN: Would renew certificate for {domain}")
            return RenewalResult(
                domain=domain,
                success=True,
                message="Dry run - certificate would be renewed"
            )
        
        try:
            cmd = ['certbot', 'renew', '--cert-name', domain]
            if force:
                cmd.append('--force-renewal')
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Get new certificate info
            new_cert_info = self.get_certificate_info(domain)
            
            return RenewalResult(
                domain=domain,
                success=True,
                message="Certificate renewed successfully",
                new_expiry=new_cert_info.expiry_date if new_cert_info else None
            )
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to renew certificate for {domain}: {e}")
            return RenewalResult(
                domain=domain,
                success=False,
                message="Certificate renewal failed",
                error=str(e)
            )
    
    def renew_expiring_certificates(self) -> List[RenewalResult]:
        """Renew all certificates that are expiring soon or expired."""
        results = []
        
        self.scan_all_certificates()
        
        for cert in self.certificates:
            if cert.status in ['expiring_soon', 'expired']:
                logger.info(f"Renewing certificate for {cert.domain} (status: {cert.status})")
                result = self.renew_certificate(cert.domain)
                results.append(result)
                
                if result.success:
                    logger.info(f"Successfully renewed {cert.domain}")
                    self._send_alert(
                        f"Certificate Renewed: {cert.domain}",
                        f"Certificate for {cert.domain} has been successfully renewed. New expiry: {result.new_expiry}"
                    )
                else:
                    logger.error(f"Failed to renew {cert.domain}: {result.error}")
                    self._send_alert(
                        f"Certificate Renewal Failed: {cert.domain}",
                        f"Failed to renew certificate for {cert.domain}. Error: {result.error}",
                        is_error=True
                    )
        
        return results
    
    def _send_alert(self, subject: str, message: str, is_error: bool = False):
        """Send email alert for certificate events."""
        if not self.config['email_alerts']['enabled']:
            return
        
        try:
            msg = MIMEText(message)
            msg['Subject'] = f"[{'ERROR' if is_error else 'INFO'}] {subject}"
            msg['From'] = self.config['email_alerts']['smtp_username']
            msg['To'] = ', '.join(self.config['email_alerts']['recipients'])
            
            with smtplib.SMTP(
                self.config['email_alerts']['smtp_server'],
                self.config['email_alerts']['smtp_port']
            ) as server:
                server.starttls()
                server.login(
                    self.config['email_alerts']['smtp_username'],
                    self.config['email_alerts'].get('smtp_password', '')
                )
                server.send_message(msg)
            
            logger.info(f"Alert sent: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def _send_webhook(self, event_type: str, data: Dict):
        """Send webhook notification for certificate events."""
        if not self.config.get('webhook_url'):
            return
        
        try:
            import requests
            payload = {
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            requests.post(self.config['webhook_url'], json=payload, timeout=10)
            logger.info(f"Webhook sent: {event_type}")
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
    
    def validate_certificate_chain(self, domain: str) -> bool:
        """Validate the complete certificate chain."""
        cert_path = Path(f"{self.config['cert_path']}/{domain}/cert.pem")
        chain_path = Path(f"{self.config['cert_path']}/{domain}/chain.pem")
        
        if not cert_path.exists() or not chain_path.exists():
            logger.error(f"Certificate or chain file not found for {domain}")
            return False
        
        try:
            cmd = [
                'openssl', 'verify',
                '-CAfile', str(chain_path),
                str(cert_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                logger.info(f"Certificate chain valid for {domain}")
                return True
            else:
                logger.error(f"Certificate chain validation failed for {domain}: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Certificate chain validation error for {domain}: {e}")
            return False
    
    def generate_health_report(self) -> Dict:
        """Generate a comprehensive health report for all certificates."""
        self.scan_all_certificates()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_certificates': len(self.certificates),
            'valid': len([c for c in self.certificates if c.status == 'valid']),
            'expiring_soon': len([c for c in self.certificates if c.status == 'expiring_soon']),
            'expired': len([c for c in self.certificates if c.status == 'expired']),
            'certificates': [asdict(cert) for cert in self.certificates],
            'auto_renewal_enabled': len([c for c in self.certificates if c.auto_renewal])
        }
        
        return report
    
    def export_report(self, output_path: str = '/var/log/ssl_certificate_health_report.json'):
        """Export health report to JSON file."""
        report = self.generate_health_report()
        
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Health report exported to {output_path}")
            return output_path
        except IOError as e:
            logger.error(f"Failed to export report: {e}")
            return None


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SSL Certificate Manager')
    parser.add_argument('action', choices=['scan', 'renew', 'report', 'validate'], 
                       help='Action to perform')
    parser.add_argument('--domain', help='Specific domain to process')
    parser.add_argument('--force', action='store_true', help='Force renewal')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    # Override config if specified
    config_path = args.config if args.config else '/etc/ssl_certificate_manager/config.json'
    
    manager = SSLCertificateManager(config_path)
    
    if args.dry_run:
        manager.config['dry_run'] = True
    
    if args.action == 'scan':
        certificates = manager.scan_all_certificates()
        for cert in certificates:
            print(f"{cert.domain}: {cert.status} (expires in {cert.days_until_expiry} days)")
    
    elif args.action == 'renew':
        if args.domain:
            result = manager.renew_certificate(args.domain, force=args.force)
            print(f"{result.domain}: {'SUCCESS' if result.success else 'FAILED'} - {result.message}")
        else:
            results = manager.renew_expiring_certificates()
            for result in results:
                print(f"{result.domain}: {'SUCCESS' if result.success else 'FAILED'} - {result.message}")
    
    elif args.action == 'report':
        report = manager.generate_health_report()
        print(json.dumps(report, indent=2, default=str))
        manager.export_report()
    
    elif args.action == 'validate':
        if args.domain:
            valid = manager.validate_certificate_chain(args.domain)
            print(f"{args.domain}: {'VALID' if valid else 'INVALID'}")
        else:
            for cert in manager.scan_all_certificates():
                valid = manager.validate_certificate_chain(cert.domain)
                print(f"{cert.domain}: {'VALID' if valid else 'INVALID'}")


if __name__ == '__main__':
    main()