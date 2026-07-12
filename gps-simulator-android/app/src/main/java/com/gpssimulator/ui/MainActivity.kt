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
import android.view.View
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.lifecycle.lifecycleScope
import com.gpssimulator.service.GPSSimulationService
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    private var simulationService: GPSSimulationService? = null
    private var isBound = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val layoutId = resources.getIdentifier("activity_main", "layout", packageName)
        if (layoutId != 0) setContentView(layoutId)

        val permissions = mutableListOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        if (permissions.any { ActivityCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }) {
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), 100)
        }

        val btnIds = arrayOf("btnApply", "btn_apply", "button_apply", "start_btn")
        var applyButton: View? = null
        for (idStr in btnIds) {
            val id = resources.getIdentifier(idStr, "id", packageName)
            if (id != 0) { applyButton = findViewById(id); break }
        }

        applyButton?.setOnClickListener {
            val latId = resources.getIdentifier("etLatitude", "id", packageName).let { if(it==0) resources.getIdentifier("et_latitude", "id", packageName) else it }
            val lngId = resources.getIdentifier("etLongitude", "id", packageName).let { if(it==0) resources.getIdentifier("et_longitude", "id", packageName) else it }
            
            val lat = if (latId != 0) findViewById<EditText>(latId)?.text?.toString()?.toDoubleOrNull() ?: 0.0 else 0.0
            val lng = if (lngId != 0) findViewById<EditText>(lngId)?.text?.toString()?.toDoubleOrNull() ?: 0.0 else 0.0
            
            simulationService?.setTargetLocation(lat, lng)
            
            AlertDialog.Builder(this)
                .setTitle("成功")
                .setMessage("原廠功能已就緒！請確保開發者選項中已選取本應用。")
                .setPositiveButton("確定", null)
                .show()
        }

        val intent = Intent(this, GPSSimulationService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent) else startService(intent)
        bindService(intent, connection, Context.BIND_AUTO_CREATE)
    }

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            simulationService = (service as GPSSimulationService.LocalBinder).getService()
            isBound = true
            observeServiceState()
        }
        override fun onServiceDisconnected(name: ComponentName?) { isBound = false }
    }

    private fun observeServiceState() {
        lifecycleScope.launch {
            simulationService?.uiState?.collect { state ->
                val latId = resources.getIdentifier("etLatitude", "id", packageName).let { if(it==0) resources.getIdentifier("et_latitude", "id", packageName) else it }
                val lngId = resources.getIdentifier("etLongitude", "id", packageName).let { if(it==0) resources.getIdentifier("et_longitude", "id", packageName) else it }
                if (latId != 0) findViewById<EditText>(latId)?.text = Editable.Factory.getInstance().newEditable(state.latitude.toString())
                if (lngId != 0) findViewById<EditText>(lngId)?.text = Editable.Factory.getInstance().newEditable(state.longitude.toString())
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (isBound) { unbindService(connection); isBound = false }
    }
}
