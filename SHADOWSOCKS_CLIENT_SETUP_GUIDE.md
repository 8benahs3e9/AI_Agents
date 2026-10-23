# Shadowsocks Client Setup Guide

**Date**: 2026-10-06
**Server**: et-gtw (Gateway Server)
**Purpose**: Configure Shadowsocks clients for protocol obfuscation

---

## Server Connection Information

**Shadowsocks Server Details**:
- **Server IP**: Your server's public IP (e.g., `et-gtw.shatsie.fun` or IP address)
- **Port**: 8388
- **Password**: `I/GiLCVJWbDuSyPEqatn3YMwe6e5S4w+k1FDTfdHZsk=`
- **Method**: aes-256-gcm
- **Mode**: tcp_and_udp

**Note**: The server IP above is the public IP of your et-gtw server. You can find it by running:
```bash
curl -s ifconfig.me
```

---

## Current WireGuard Setup

### Server Configuration
- **WireGuard Interface**: wg0
- **Server IP**: 10.100.0.1
- **Listen Port**: 51820
- **Network**: 10.100.0.0/24

### Existing Clients
1. **Android Client**
   - WireGuard IP: 10.100.0.2
   - Public Key: A7NoBoK8HQjV2NAWp8HCpyJUkX9vQVfOuTe8pe38JBI=
   - Status: Connected (handshake 34s ago)
   - Transfer: 4.22GB received, 19.94GB sent

2. **Linux Mint Client**
   - WireGuard IP: 10.100.0.3
   - Public Key: 5QmboH9IcWnGi6UP76WF4N2xw9286pGa+6nmo2UBqAw=
   - Status: Connected (handshake 31s ago)
   - Transfer: 605MB received, 9.30GB sent

---

## Integration Options

You have **three options** for integrating Shadowsocks with your existing WireGuard setup:

### Option A: Shadowsocks as Primary VPN (Recommended for Most Users)
**Replace WireGuard with Shadowsocks as your main VPN**

**Pros**:
- Simpler setup (single VPN protocol)
- Better obfuscation (Shadowsocks designed for this)
- Lower overhead than double-encryption
- Easier to manage

**Cons**:
- Lose WireGuard's performance benefits
- Need to migrate routing configuration
- Different client apps

**Best For**: General use, when obfuscation is priority over raw performance

---

### Option B: WireGuard-over-Shadowsocks (Advanced)
**Route WireGuard traffic through Shadowsocks tunnel**

**Pros**:
- Keep WireGuard's performance and security
- Add obfuscation layer on top
- Best of both protocols
- WireGuard configuration unchanged

**Cons**:
- More complex setup
- Double encryption overhead
- Higher latency
- More points of failure

**Best For**: When you need both WireGuard's performance AND maximum obfuscation

---

### Option C: Shadowsocks as Backup (Safest)
**Keep WireGuard as primary, Shadowsocks as backup**

**Pros**:
- Zero risk to existing setup
- Shadowsocks available when needed
- Easy to test and validate
- Can switch back and forth

**Cons**:
- No immediate obfuscation benefit
- Need to manually switch when needed
- Two VPNs to manage

**Best For**: Testing phase, or when obfuscation is only occasionally needed

---

## Client Setup Instructions

### Android Client Setup

#### Step 1: Install Shadowsocks Client
Download from Google Play Store:
- **App**: Shadowsocks (by Shadowsocks)
- **Alternative**: ShadowsocksR, V2RayNG

#### Step 2: Configure Shadowsocks
Open the Shadowsocks app and add a new profile:

**Profile Settings**:
- **Name**: et-gtw Shadowsocks
- **Server**: Your server's public IP (e.g., `et-gtw.shatsie.fun`)
- **Remote Port**: 8388
- **Password**: `I/GiLCVJWbDuSyPEqatn3YMwe6e5S4w+k1FDTfdHZsk=`
- **Encrypt Method**: aes-256-gcm
- **Protocol**: origin (or auto)
- **Obfs**: plain (or leave as default)

#### Step 3: Connect
- Tap the profile to connect
- Check that the status shows "Connected"
- Verify your IP has changed (visit `https://ifconfig.me`)

#### Step 4: Configure VPN Mode (Option A - Primary VPN)
If using Shadowsocks as primary VPN:
- In Shadowsocks app settings, enable "VPN Mode" or "Route All Traffic"
- This will route all device traffic through Shadowsocks
- You can disable the WireGuard app

#### Step 5: Configure Proxy Mode (Option C - Backup)
If using Shadowsocks as backup:
- In Shadowsocks app, use "Proxy Mode" instead of VPN mode
- Configure apps to use proxy (if supported)
- Keep WireGuard as primary VPN

---

### Linux Mint Client Setup

#### Step 1: Install Shadowsocks Client
```bash
# Update package list
sudo apt update

# Install shadowsocks-libev client
sudo apt install shadowsocks-libev -y
```

#### Step 2: Create Client Configuration
Create configuration file:
```bash
nano ~/.config/shadowsocks/config.json
```

Add the following configuration:
```json
{
    "server":"YOUR_SERVER_IP",
    "server_port":8388,
    "local_address":"127.0.0.1",
    "local_port":1080,
    "password":"I/GiLCVJWbDuSyPEqatn3YMwe6e5S4w+k1FDTfdHZsk=",
    "timeout":60,
    "method":"aes-256-gcm",
    "fast_open":true,
    "mode":"tcp_and_udp"
}
```

Replace `YOUR_SERVER_IP` with your server's public IP.

#### Step 3: Start Shadowsocks Client
```bash
# Start Shadowsocks client
ss-local -c ~/.config/shadowsocks/config.json -v

# Or run in background
nohup ss-local -c ~/.config/shadowsocks/config.json -v > ~/.shadowsocks.log 2>&1 &
```

#### Step 4: Configure System Proxy (Option A - Primary VPN)
If using Shadowsocks as primary VPN:

**Install proxychains** (optional, for proxy-aware applications):
```bash
sudo apt install proxychains4 -y
```

**Configure proxychains**:
```bash
sudo nano /etc/proxychains.conf
```

Add or modify:
```
socks5 127.0.0.1 1080
```

**Use with applications**:
```bash
proxychains4 curl https://ifconfig.me
```

**Configure system-wide proxy** (GNOME):
- Settings → Network → Proxy
- Manual proxy configuration
- SOCKS Host: 127.0.0.1, Port: 1080

#### Step 5: WireGuard-over-Shadowsocks (Option B - Advanced)
If routing WireGuard through Shadowsocks:

**Install required tools**:
```bash
sudo apt install wireguard-tools -y
```

**Create WireGuard-over-Shadowsocks configuration**:
This is complex and requires:
1. Shadowsocks client running on port 1080
2. WireGuard configured to use SOCKS5 proxy
3. Additional routing configuration

**Note**: This setup is significantly more complex. See the "WireGuard-over-Shadowsocks" section below for detailed instructions.

#### Step 6: WireGuard Backup (Option C - Safest)
If keeping WireGuard as primary:
- No changes to WireGuard configuration
- Shadowsocks runs alongside for backup use
- Switch manually when needed

---

## WireGuard-over-Shadowsocks (Option B - Advanced Setup)

### Server-Side Changes (Optional)
If you want the server to route Shadowsocks traffic through WireGuard:

**Add Shadowsocks as a WireGuard peer**:
Edit `/etc/wireguard/wg0.conf`:
```ini
[Peer]
# Shadowsocks Bridge (if using separate bridge server)
PublicKey = <SHADOWSOCKS_SERVER_PUBLIC_KEY>
AllowedIPs = 10.100.0.4/32
Endpoint = <SHADOWSOCKS_SERVER_IP>:51820
PersistentKeepalive = 25
```

### Client-Side Configuration

#### Method 1: Using ss-redir (Shadowsocks redirect mode)
```bash
# Install shadowsocks-libev with redir support
sudo apt install shadowsocks-libev -y

# Create redir configuration
nano ~/.config/shadowsocks/redir.json
```

```json
{
    "server":"YOUR_SERVER_IP",
    "server_port":8388,
    "local_address":"0.0.0.0",
    "local_port":1081,
    "password":"I/GiLCVJWbDuSyPEqatn3YMwe6e5S4w+k1FDTfdHZsk=",
    "timeout":60,
    "method":"aes-256-gcm",
    "mode":"tcp_and_udp"
}
```

```bash
# Start ss-redir
ss-redir -c ~/.config/shadowsocks/redir.json -v

# Configure iptables to redirect traffic through ss-redir
sudo iptables -t nat -A OUTPUT -p tcp -j REDIRECT --to-ports 1081
```

#### Method 2: Using ProxyChains with WireGuard
```bash
# Install proxychains
sudo apt install proxychains4 -y

# Configure proxychains
sudo nano /etc/proxychains.conf
```

Set:
```
socks5 127.0.0.1 1080
```

**Use WireGuard through proxy**:
```bash
# This is experimental and may not work reliably
proxychains4 wg-quick up wg0
```

**Note**: WireGuard doesn't natively support SOCKS5 proxies. This is a workaround and may not be stable.

---

## Recommended Approach by Threat Model

### Low Threat Model (ISP Surveillance)
**Recommendation**: Option C (Shadowsocks as Backup)
- Keep WireGuard as primary
- Shadowsocks available if needed
- Zero risk to existing setup

### Medium Threat Model (Corporate Firewalls)
**Recommendation**: Option A (Shadowsocks as Primary)
- Switch to Shadowsocks as main VPN
- Better obfuscation against DPI
- Accept slight performance trade-off

### High Threat Model (Nation-State)
**Recommendation**: Option B (WireGuard-over-Shadowsocks) + Tor
- Maximum obfuscation
- Multi-layer approach
- Accept higher complexity and overhead

---

## Migration Path (Option A - Switch to Shadowsocks)

### Step 1: Test Shadowsocks
- Install and configure Shadowsocks on both clients
- Test connection without disabling WireGuard
- Verify traffic is routed correctly

### Step 2: Backup WireGuard Config
```bash
# On Android
# Export WireGuard config from app

# On Linux Mint
sudo cp /etc/wireguard/wg0.conf ~/wireguard-backup.conf
```

### Step 3: Switch DNS Configuration
Shadowsocks uses server DNS (10.100.0.1), so DNS routing remains the same.

### Step 4: Disable WireGuard
```bash
# On Android
# Turn off WireGuard app

# On Linux Mint
sudo wg-quick down wg0
sudo systemctl disable wg-quick@wg0
```

### Step 5: Enable Shadowsocks
```bash
# On Android
# Connect Shadowsocks in VPN mode

# On Linux Mint
# Start Shadowsocks and configure system proxy
```

### Step 6: Verify
- Check IP: `curl https://ifconfig.me`
- Check DNS: `nslookup google.com`
- Test browsing
- Test other applications

### Step 7: Rollback (if needed)
```bash
# Re-enable WireGuard
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0

# Disable Shadowsocks
pkill ss-local
```

---

## Impact on Existing WireGuard Configurations

### Option A (Shadowsocks as Primary)
**Impact**: HIGH
- WireGuard will be disabled
- WireGuard configuration can be kept as backup
- No server-side changes needed
- Easy rollback by re-enabling WireGuard

### Option B (WireGuard-over-Shadowsocks)
**Impact**: MEDIUM
- WireGuard configuration remains active
- Additional complexity on client side
- Server-side changes optional
- Rollback by removing Shadowsocks layer

### Option C (Shadowsocks as Backup)
**Impact**: NONE
- WireGuard configuration unchanged
- Shadowsocks runs alongside
- No server-side changes
- No rollback needed

---

## Testing Shadowsocks Connection

### From Android
1. Connect Shadowsocks
2. Open browser
3. Visit `https://ifconfig.me`
4. Verify IP shows server's public IP

### From Linux Mint
```bash
# Start Shadowsocks
ss-local -c ~/.config/shadowsocks/config.json -v

# Test with curl through proxy
curl --socks5 127.0.0.1:1080 https://ifconfig.me

# Or use proxychains
proxychains4 curl https://ifconfig.me
```

### Verify DNS
```bash
# DNS should be routed through Shadowsocks
nslookup google.com
# Should use server's DNS (10.100.0.1)
```

---

## Troubleshooting

### Connection Fails
1. Verify server IP is correct
2. Check firewall allows port 8388
3. Verify password is correct (copy-paste exactly)
4. Check Shadowsocks service is running on server:
   ```bash
   sudo systemctl status shadowsocks-libev
   ```

### Slow Performance
1. Try different encryption method (chacha20-poly1305 for mobile)
2. Check server resources
3. Verify network latency
4. Consider Option A (Shadowsocks only) instead of Option B

### DNS Leaks
1. Configure Shadowsocks to use server DNS (already configured)
2. Disable DNS on client side
3. Test with `https://dnsleaktest.com`

### WireGuard Still Active
If you switched to Shadowsocks but WireGuard is still routing:
```bash
# Check WireGuard status
sudo wg show

# Disable WireGuard
sudo wg-quick down wg0
```

---

## Summary & Recommendation

### For Your Setup (2 Clients: Android + Linux Mint)

**Recommended Approach**: **Option A (Shadowsocks as Primary)**

**Rationale**:
- Your threat model appears to be ISP/corporate surveillance (based on fingerprinting concerns)
- Shadowsocks provides better obfuscation than plain WireGuard
- Easier to manage than WireGuard-over-Shadowsocks
- Performance difference is negligible for most use cases
- Easy rollback if needed

**Implementation Steps**:
1. Install Shadowsocks on Android client (from Play Store)
2. Install Shadowsocks on Linux Mint client (`sudo apt install shadowsocks-libev`)
3. Configure both clients with server details
4. Test Shadowsocks connection on both clients
5. Disable WireGuard on both clients
6. Verify traffic routing
7. Keep WireGuard config as backup

**Timeline**:
- Android: 10 minutes
- Linux Mint: 15 minutes
- Testing: 10 minutes
- **Total**: ~35 minutes

---

## Documentation References

- **Phase 2 Status**: `/home/user/AI_Agents/SHADOWSOCKS_PHASE2_STATUS.md`
- **Phase 2 Plan**: `/home/user/AI_Agents/SHADOWSOCKS_PHASE2_PLAN.md`
- **Resource Analysis**: `/home/user/AI_Agents/TRAFFIC_FINGERPRINTING_MITIGATION_RESOURCE_ANALYSIS.md`
- **System Documentation**: `/home/user/AI_Agents/AGENTS.md`

---

**Last Updated**: 2026-10-06
**Status**: Ready for client implementation
