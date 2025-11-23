import { useEffect, useState } from 'react'

const API_BASE = 'http://localhost:8001'

interface Device {
  id: number
  name: string
  ip_address: string
  device_type: string
  model: string | null
  firmware_version: string | null
  is_online: boolean
  last_seen_at: string | null
}

interface SystemMetrics {
  cpu_load: number
  memory_used: number
  memory_total: number
  memory_percent: number
  uptime: string
  version: string
}

interface DeviceMetrics {
  device_id: number
  device_name: string
  system: SystemMetrics
  timestamp: string
  status: string
}

function App() {
  const [devices, setDevices] = useState<Device[]>([])
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null)
  const [metrics, setMetrics] = useState<DeviceMetrics | null>(null)
  const [loading, setLoading] = useState(true)

  // Fetch devices on mount
  useEffect(() => {
    fetchDevices()
  }, [])

  // Fetch metrics when device is selected
  useEffect(() => {
    if (selectedDevice) {
      fetchMetrics(selectedDevice.id)
      // Poll metrics every 3 seconds
      const interval = setInterval(() => {
        fetchMetrics(selectedDevice.id)
      }, 3000)
      return () => clearInterval(interval)
    }
  }, [selectedDevice])

  const fetchDevices = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/devices`)
      const data = await response.json()
      setDevices(data.devices || [])
      if (data.devices && data.devices.length > 0 && !selectedDevice) {
        setSelectedDevice(data.devices[0])
      }
    } catch (error) {
      console.error('Failed to fetch devices:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchMetrics = async (deviceId: number) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/metrics/devices/${deviceId}/current`)
      const data = await response.json()
      setMetrics(data)
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-blue-400">MTCloud Dashboard</h1>
          <p className="text-gray-400 text-sm">MikroTik Fleet Management</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="text-sm text-gray-400 mb-1">Total Devices</div>
            <div className="text-3xl font-bold">{devices.length}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="text-sm text-gray-400 mb-1">Online</div>
            <div className="text-3xl font-bold text-green-400">
              {devices.filter(d => d.is_online).length}
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="text-sm text-gray-400 mb-1">Offline</div>
            <div className="text-3xl font-bold text-red-400">
              {devices.filter(d => !d.is_online).length}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Device List */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="p-4 border-b border-gray-700">
                <h2 className="text-lg font-semibold">Devices</h2>
              </div>
              <div className="divide-y divide-gray-700">
                {devices.map(device => (
                  <button
                    key={device.id}
                    onClick={() => setSelectedDevice(device)}
                    className={`w-full text-left p-4 hover:bg-gray-750 transition-colors ${
                      selectedDevice?.id === device.id ? 'bg-gray-750' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium">{device.name}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        device.is_online 
                          ? 'bg-green-900 text-green-300' 
                          : 'bg-red-900 text-red-300'
                      }`}>
                        {device.is_online ? 'Online' : 'Offline'}
                      </span>
                    </div>
                    <div className="text-sm text-gray-400">{device.ip_address}</div>
                    <div className="text-xs text-gray-500 mt-1">{device.model}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Device Details & Metrics */}
          <div className="lg:col-span-2">
            {selectedDevice && metrics ? (
              <div className="space-y-4">
                {/* Device Info Card */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <h2 className="text-xl font-semibold mb-4">{selectedDevice.name}</h2>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">IP Address:</span>
                      <span className="ml-2 font-mono">{selectedDevice.ip_address}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Model:</span>
                      <span className="ml-2">{selectedDevice.model || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">RouterOS:</span>
                      <span className="ml-2">{metrics.system.version}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Uptime:</span>
                      <span className="ml-2">{metrics.system.uptime}</span>
                    </div>
                  </div>
                </div>

                {/* System Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* CPU Card */}
                  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">CPU Load</h3>
                      <span className="text-2xl font-bold text-blue-400">
                        {metrics.system.cpu_load}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all ${
                          metrics.system.cpu_load > 80 
                            ? 'bg-red-500' 
                            : metrics.system.cpu_load > 50 
                            ? 'bg-yellow-500' 
                            : 'bg-green-500'
                        }`}
                        style={{ width: `${metrics.system.cpu_load}%` }}
                      />
                    </div>
                  </div>

                  {/* Memory Card */}
                  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">Memory</h3>
                      <span className="text-2xl font-bold text-purple-400">
                        {metrics.system.memory_percent}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-3 mb-2">
                      <div
                        className={`h-3 rounded-full transition-all ${
                          metrics.system.memory_percent > 80 
                            ? 'bg-red-500' 
                            : metrics.system.memory_percent > 50 
                            ? 'bg-yellow-500' 
                            : 'bg-green-500'
                        }`}
                        style={{ width: `${metrics.system.memory_percent}%` }}
                      />
                    </div>
                    <div className="text-xs text-gray-400">
                      {formatBytes(metrics.system.memory_used)} / {formatBytes(metrics.system.memory_total)}
                    </div>
                  </div>
                </div>

                {/* Last Updated */}
                <div className="text-xs text-gray-500 text-right">
                  Last updated: {new Date(metrics.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ) : (
              <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
                <p className="text-gray-400">Select a device to view metrics</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
