package com.gpssimulator.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.location.Location
import android.location.LocationManager
import android.os.Binder
import android.os.Build
import android.os.IBinder
import android.os.SystemClock
import androidx.core.app.NotificationCompat
import com.gpssimulator.data.SimulationState
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class GPSSimulationService : Service() {
    private val _uiState = MutableStateFlow(SimulationState())
    val uiState: StateFlow<SimulationState> = _uiState

    private var job: Job? = null
    private val binder = LocalBinder()
    inner class LocalBinder : Binder() { fun getService(): GPSSimulationService = this@GPSSimulationService }
    override fun onBind(intent: Intent?): IBinder = binder

    override fun onCreate() {
        super.onCreate()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel("gps_channel", "GPS Simulation", NotificationManager.IMPORTANCE_LOW)
            getSystemService(NotificationManager::class.java)?.createNotificationChannel(channel)
        }
        val notification = NotificationCompat.Builder(this, "gps_channel")
            .setContentTitle("GPS Simulator Active")
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .build()
        startForeground(1, notification)
    }

    fun updateParams(lat: Double, lng: Double, speed: Float, direction: Int) {
        _uiState.value = _uiState.value.copy(latitude = lat, longitude = lng, speed = speed, direction = direction)
        if (_uiState.value.isSimulating) {
            restartSimulationLoop()
        }
    }

    fun toggleSimulation(enable: Boolean) {
        _uiState.value = _uiState.value.copy(isSimulating = enable)
        if (enable) restartSimulationLoop() else job?.cancel()
    }

    fun toggleTest(enable: Boolean) {
        _uiState.value = _uiState.value.copy(isTestRunning = enable)
    }

    private fun restartSimulationLoop() {
        job?.cancel()
        // 👑 關鍵修復：改用 Dispatchers.IO 執行耗時的位置計算與底層發送，真機再怎麼丟 Exception 也絕不卡死 UI
        job = CoroutineScope(Dispatchers.IO).launch {
            while (isActive && _uiState.value.isSimulating) {
                val state = _uiState.value
                val r = 6378137.0
                val dn = (state.speed * (1000f / 3600f)) * Math.cos(Math.toRadians(state.direction.toDouble()))
                val de = (state.speed * (1000f / 3600f)) * Math.sin(Math.toRadians(state.direction.toDouble()))
                val dLat = dn / r
                val dLon = de / (r * Math.cos(Math.toRadians(state.latitude)))
                
                val newLat = state.currentLatitude + Math.toDegrees(dLat)
                val newLng = state.currentLongitude + Math.toDegrees(dLon)
                
                _uiState.value = _uiState.value.copy(currentLatitude = newLat, currentLongitude = newLng)
                
                try {
                    val locMgr = getSystemService(Context.LOCATION_SERVICE) as LocationManager
                    val providers = listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER)
                    for (p in providers) {
                        try { locMgr.addTestProvider(p, false, false, false, false, true, true, true, 1, 2) } catch(e:Exception){}
                        val mockLocation = Location(p).apply {
                            latitude = newLat
                            longitude = newLng
                            altitude = 0.0
                            time = System.currentTimeMillis()
                            elapsedRealtimeNanos = SystemClock.elapsedRealtimeNanos()
                            accuracy = 1.0f
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) speedAccuracyMetersPerSecond = 0.1f
                        }
                        locMgr.setTestProviderLocation(p, mockLocation)
                    }
                } catch (e: Exception) {
                    // 這裡如果因為真機沒開開發者權限報錯，只打印不卡死
                    e.printStackTrace()
                }
                delay(1000)
            }
        }
    }

    override fun onDestroy() { job?.cancel(); super.onDestroy() }
}
