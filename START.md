# MTCloud - Quick Start Guide

## ✅ Your Database is Already Seeded!

Your 3 MikroTik devices are already in the database:
- ✅ Main Router (192.168.100.1) - CRS310-8G+2S+
- ✅ 10G Switch (192.168.100.2) - CRS309-1G-8S+
- ✅ 24-port Switch (192.168.100.3) - CRS226-24G-2S+

## 🚀 Start the Application

### Terminal 1: Backend API

```bash
cd /Users/sem/code/mtcloud/backend
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

The API will start on: **http://localhost:8001**  
API Docs: **http://localhost:8001/api/v1/docs**

### Terminal 2: Frontend Dashboard

```bash
cd /Users/sem/code/mtcloud/frontend
npm run dev
```

The dashboard will start on: **http://localhost:5174**

## 🎯 What You'll See

The dashboard will display:
- **Total Devices: 3**
- **Online: 3** (all green)
- **Device List**: All 3 MikroTik devices in the sidebar
- **Real-time Metrics**: Click any device to see:
  - CPU load with color-coded progress bar
  - Memory usage with formatted bytes
  - Device info (IP, model, RouterOS version, uptime)
  - Auto-refresh every 3 seconds

## 📡 Test the API

### List all devices:
```bash
curl http://localhost:8001/api/v1/devices | python3 -m json.tool
```

### Get live metrics from Main Router:
```bash
curl http://localhost:8001/api/v1/metrics/devices/4/current | python3 -m json.tool
```

### Health check:
```bash
curl http://localhost:8001/health
```

## 🔧 Troubleshooting

### If dashboard shows no devices:

1. **Check API is running:**
   ```bash
   curl http://localhost:8001/health
   ```

2. **Verify devices in database:**
   ```bash
   curl http://localhost:8001/api/v1/devices
   ```

3. **Check CORS in browser console:**
   - Open browser DevTools (F12)
   - Look for CORS errors
   - CORS should allow: `http://localhost:5174`

4. **Restart backend after .env changes:**
   - The backend runs with `--reload` so it should auto-restart
   - But if you changed .env, restart manually with Ctrl+C then start again

### If API can't connect to MikroTik devices:

1. **Verify API is enabled on devices:**
   ```bash
   sshpass -p 'Dragon@123!@#' ssh admin@192.168.100.1 "/ip service print where name=api"
   ```

2. **Test connection manually:**
   ```bash
   cd /Users/sem/code/mtcloud/backend
   ./venv/bin/python scripts/test_mikrotik_connection.py
   ```

## 📊 Database Info

- **Organization**: Titanium Computing (ID: 1)
- **Client**: Internal Infrastructure (ID: 2)
- **Site**: Home Network (ID: 1)
- **Devices**: 3 (IDs: 4, 5, 6)

## 🌐 URLs

- **Dashboard**: http://localhost:5174
- **API**: http://localhost:8001
- **API Docs (Swagger)**: http://localhost:8001/api/v1/docs
- **API Docs (ReDoc)**: http://localhost:8001/api/v1/redoc

## 🎨 Features Working

✅ Device list with online/offline status  
✅ Real-time CPU metrics  
✅ Real-time memory metrics  
✅ Auto-refresh every 3 seconds  
✅ Responsive Tailwind UI  
✅ Dark theme  
✅ Color-coded progress bars (green/yellow/red)  
✅ REST API with full CRUD  
✅ WebSocket support (ready but not used yet)  

## 📝 Next Steps

- Add authentication (JWT)
- Implement WebSocket for even faster updates
- Add historical metrics charts
- Build alert system
- Add more dashboard views
- Implement Celery background tasks

---

**Enjoy your MikroTik dashboard!** 🎉
