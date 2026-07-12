package com.gpssimulator.service
import android.app.Service
import android.content.Intent
import android.os.IBinder
class GPSSimulationService : Service() {
    override fun onBind(intent: Intent?): IBinder? = null
}
