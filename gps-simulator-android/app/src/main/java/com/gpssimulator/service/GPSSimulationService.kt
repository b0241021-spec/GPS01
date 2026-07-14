package com.gpssimulator.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.gpssimulator.R
import com.gpssimulator.utils.LogManager

class GPSSimulationService : Service() {
    private val NOTIFICATION_ID = 1
    private val CHANNEL_ID = "gps_simulation_channel"

    override fun onCreate() {
        super.onCreate()
        LogManager.init(this)
        LogManager.writeLog("GPSSimulationService onCreate")
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        try {
            LogManager.writeLog("GPSSimulationService onStartCommand")
            val isSimulating = intent?.getBooleanExtra("isSimulating", false) ?: false

            if (isSimulating) {
                startForeground(NOTIFICATION_ID, createNotification("GPS 模擬中..."))
            } else {
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        } catch (e: Exception) {
            LogManager.writeError("GPSSimulationService", "onStartCommand failed", e)
        }

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        LogManager.writeLog("GPSSimulationService onDestroy")
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "GPS 模擬通知",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }
    }

    private fun createNotification(message: String): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("GPS 模擬器")
            .setContentText(message)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setOngoing(true)
            .build()
    }
}
