# MTCloud MikroTik Integration Scripts

This directory contains scripts for testing and managing MikroTik device connections.

---

## 🚀 Quick Start

### Prerequisites

1. Python virtual environment with dependencies installed:
   ```bash
   cd /Users/sem/code/mtcloud/backend
   python3 -m venv venv
   ./venv/bin/pip install -r requirements.txt
   ```

2. MikroTik devices must have:
   - Network connectivity (ping test)
   - SSH access enabled (for initial setup)
   - API service enabled (port 8728)

---

## 📋 Scripts Available

### 1. `check_api_status.sh`
**Purpose:** Check if RouterOS API service is enabled on your MikroTik devices

**Usage:**
```bash
./scripts/check_api_status.sh
```

This script will:
- Check SSH connectivity to all three devices
- Display API service status
- Show if API is enabled/disabled
- Provide instructions to enable API if needed

**Sample Output:**
```
==============================================
Checking: Main Router (CRS310)
IP: 192.168.100.1
==============================================

API Service Status:
 0   name="api" port=8728 address="" certificate=none disabled=no
```

---

### 2. `test_mikrotik_connection.py`
**Purpose:** Test API connections and retrieve device information

**Usage:**
```bash
./venv/bin/python scripts/test_mikrotik_connection.py
```

This script will:
- Connect to all three MikroTik devices via RouterOS API
- Retrieve system information (hostname, version, uptime)
- Display CPU load and memory usage
- Save results to `test_results.json`

**Sample Output:**
```
============================================================
Testing: Main Router (CRS310-8G+2S+)
IP: 192.168.100.1
Description: 8x 2.5G + 2x 10G SFP+
============================================================

✅ CONNECTION SUCCESSFUL

Device Information:
  Hostname:     Main Router
  Platform:     CRS310-8G+2S+IN
  RouterOS:     7.20.4
  Uptime:       2d5h32m15s
  CPU Load:     3%
  Memory:       0.09 GB / 0.24 GB (39.1% used)
```

---

## 🔧 Setting Up MikroTik API Access

### Step 1: Check Current API Status

Run the API status check script:
```bash
./scripts/check_api_status.sh
```

### Step 2: Enable API Service (if disabled)

SSH into each device and enable the API:

**For Main Router (192.168.100.1):**
```bash
ssh admin@192.168.100.1
/ip service enable api
/ip service set api address=192.168.100.0/24
exit
```

**For 10G Switch (192.168.100.2):**
```bash
ssh admin@192.168.100.2
/ip service enable api
/ip service set api address=192.168.100.0/24
exit
```

**For 24-port Switch (192.168.100.3):**
```bash
ssh admin@192.168.100.3
/ip service enable api
/ip service set api address=192.168.100.0/24
exit
```

### Step 3: Test API Connection

Run the Python test script:
```bash
./venv/bin/python scripts/test_mikrotik_connection.py
```

---

## 🔐 Security Considerations

### API vs API-SSL

- **API (port 8728):** Unencrypted connection
  - ✅ Faster
  - ❌ Credentials sent in plaintext
  - ✅ Good for internal networks

- **API-SSL (port 8729):** Encrypted connection
  - ✅ Encrypted traffic
  - ✅ Better security
  - ❌ Slightly slower
  - ✅ Recommended for production

### Enable API-SSL (Recommended)

```bash
ssh admin@192.168.100.1
/ip service enable api-ssl
/ip service set api-ssl address=192.168.100.0/24 certificate=auto
exit
```

Update the MikroTik service to use SSL:
```python
service = MikroTikService(
    host="192.168.100.1",
    username="admin",
    password="your_password",
    port=8729,           # API-SSL port
    use_ssl=True         # Enable SSL
)
```

### Restrict API Access

Limit API access to specific IP addresses:

```bash
# Allow only your application server
/ip service set api address=192.168.100.200/32

# Allow entire management subnet
/ip service set api address=192.168.100.0/24
```

---

## 📊 Your MikroTik Devices

| Device | IP | Model | Ports | RouterOS |
|--------|-----|-------|-------|----------|
| Main Router | 192.168.100.1 | CRS310-8G+2S+ | 8x 2.5G + 2x 10G SFP+ | 7.20.4 |
| 10G Switch | 192.168.100.2 | CRS309-1G-8S+ | 1x 1G + 8x 10G SFP+ | 7.16.1 |
| 24-port Switch | 192.168.100.3 | CRS226-24G-2S+ | 24x 1G + 2x 10G SFP+ | 7.20.4 |

---

## 🛠️ Troubleshooting

### Issue: "Connection failed: invalid user name or password"

**Possible causes:**
1. API service not enabled
2. Wrong credentials
3. User doesn't have API access permissions

**Solutions:**
1. Enable API service (see Step 2 above)
2. Verify credentials via SSH first: `ssh admin@192.168.100.1`
3. Check user permissions:
   ```bash
   /user print detail where name=admin
   ```
   Make sure group is `full` or has API access

### Issue: "Connection timeout"

**Possible causes:**
1. Device is offline
2. Firewall blocking port 8728
3. Network routing issues

**Solutions:**
1. Ping device: `ping 192.168.100.1`
2. Check firewall: `/ip firewall filter print where dst-port=8728`
3. Verify API is listening: `/ip service print detail where name=api`

### Issue: "Connection refused"

**Possible causes:**
1. API service disabled
2. Wrong port number
3. API bound to different interface

**Solutions:**
1. Enable API: `/ip service enable api`
2. Verify port: `/ip service print where name=api`
3. Check binding: `/ip service set api address=0.0.0.0/0` (temporary, then restrict)

---

## 📚 API Methods Available

The `MikroTikService` class in `app/services/mikrotik.py` provides:

### System Information:
- `get_system_identity()` - Get device hostname
- `get_system_resources()` - Get CPU, memory, uptime
- `test_connection()` - Test connectivity and get basic info

### Network Information:
- `get_interfaces()` - List all network interfaces
- `get_interface_stats(name)` - Get real-time stats for interface
- `get_all_interface_stats()` - Get stats for all interfaces
- `get_ip_addresses()` - List configured IP addresses
- `get_dhcp_leases()` - List DHCP leases

### Context Manager Support:
```python
with MikroTikService(host="192.168.100.1", username="admin", password="pass") as mt:
    resources = mt.get_system_resources()
    print(f"CPU Load: {resources['cpu-load']}%")
```

---

## 🔜 Next Steps

Once API connections are working:

1. **Create Device Management API Endpoints**
   - POST /api/v1/devices - Add device to database
   - GET /api/v1/devices - List all devices
   - GET /api/v1/devices/{id} - Get device details
   - PUT /api/v1/devices/{id} - Update device
   - DELETE /api/v1/devices/{id} - Remove device

2. **Implement Polling Service**
   - Celery task to poll devices every 60 seconds
   - Store metrics in `device_metrics` table
   - Update interface statistics

3. **Build Dashboard**
   - Real-time device status
   - CPU/Memory graphs
   - Interface traffic monitoring
   - Alert notifications

---

## 📖 References

- RouterOS API Protocol: https://help.mikrotik.com/docs/display/ROS/API
- Python RouterOS-api Library: https://github.com/socialwifi/RouterOS-api
- MikroTik Service Configuration: https://help.mikrotik.com/docs/display/ROS/Services

---

**Last Updated:** November 22, 2025
