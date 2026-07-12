package com.gpssimulator.ui

import android.Manifest
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.IBinder
import android.text.Editable
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.lifecycle.lifecycleScope
import com.gpssimulator.R
import com.gpssimulator.service.GPSSimulationService
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    private var simulationService: GPSSimulationService? = null
    private var isBound = false

    private lateinit var etLatitude: EditText
    private lateinit var etLongitude: EditText
    private lateinit var btnApply: Button

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            simulationService = (service as GPSSimulationService.LocalBinder).getService()
            isBound = true
            observeServiceState()
        }
        override fun onServiceDisconnected(name: ComponentName?) {
            isBound = false
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        etLatitude = findViewById(R.id.et_latitude)
        etLongitude = findViewById(R.id.et_longitude)
        btnApply = findViewById(R.id.btn_apply)

        // 👑 啟動時動態申請權限檢查，防止 Android 13 系統直接殺掉 App
        val permissions = mutableListOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        
        if (permissions.any { ActivityCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }) {
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), 100)
        }

        btnApply.setOnClickListener {
            val lat = etLatitude.text.toString().toDoubleOrNull() ?: 0.0
            val lng = etLongitude.text.toString().toDoubleOrNull() ?: 0.0
            
            simulationService?.setTargetLocation(lat, lng)
            
            AlertDialog.Builder(this)
                .setTitle("成功")
                .setMessage("已送出虛擬座標，請確保開發者選項已將本程式選為模擬定位應用。")
                .setPositiveButton("好的", null)
                .show()
        }

        val intent = Intent(this, GPSSimulationService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        bindService(intent, connection, Context.BIND_AUTO_CREATE)
    }

    private fun observeServiceState() {
        lifecycleScope.launch {
            simulationService?.uiState?.collect { state ->
                etLatitude.text = Editable.Factory.getInstance().newEditable(state.latitude.toString())
                etLongitude.text = Editable.Factory.getInstance().newEditable(state.longitude.toString())
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (isBound) {
            unbindService(connection)
            isBound = false
        }
    }
}
