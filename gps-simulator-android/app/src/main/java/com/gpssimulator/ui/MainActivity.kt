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
import android.view.ViewGroup
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

    private var capturedEditTexts = mutableListOf<EditText>()
    private var capturedButtons = mutableListOf<View>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        try {
            val layoutId = resources.getIdentifier("activity_main", "layout", packageName)
            if (layoutId != 0) setContentView(layoutId)

            // 1. 動態權限申請
            val permissions = mutableListOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            if (permissions.any { ActivityCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }) {
                ActivityCompat.requestPermissions(this, permissions.toTypedArray(), 100)
            }

            // 2. 🛡️ 雙重機制盲抓元件：先找畫面上所有的視圖，確保即便 ID 不符也能控到按鈕
            val rootLayout = window.decorView.findViewById<ViewGroup>(android.R.id.content)
            findAllViews(rootLayout)

            // 3. 為畫面上抓到的第一個按鈕（通常是應用按鈕）綁定事件
            val mainButton = capturedButtons.firstOrNull()
            mainButton?.setOnClickListener {
                try {
                    val lat = capturedEditTexts.getOrNull(0)?.text?.toString()?.toDoubleOrNull() ?: 0.0
                    val lng = capturedEditTexts.getOrNull(1)?.text?.toString()?.toDoubleOrNull() ?: 0.0
                    
                    simulationService?.setTargetLocation(lat, lng)
                    
                    AlertDialog.Builder(this)
                        .setTitle("提示")
                        .setMessage("位置已更新！請確認【開發者選項】中已將本 App 設為模擬位置應用。")
                        .setPositiveButton("我知道了", null)
                        .show()
                } catch (ex: Exception) {
                    ex.printStackTrace()
                }
            }

            // 4. 啟動背景 Service
            val intent = Intent(this, GPSSimulationService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent) else startService(intent)
            bindService(intent, connection, Context.BIND_AUTO_CREATE)

        } catch (e: Exception) {
            // 👑 終極防禦：就算 onCreate 發生任何預期外的錯誤，也絕對不讓 App 閃退！
            e.printStackTrace()
        }
    }

    private fun findAllViews(view: View) {
        if (view is EditText) {
            capturedEditTexts.add(view)
        } else if (view is Button || view.isClickable) {
            capturedButtons.add(view)
        }
        if (view is ViewGroup) {
            for (i in 0 until view.childCount) {
                findAllViews(view.getChildAt(i))
            }
        }
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
            try {
                simulationService?.uiState?.collect { state ->
                    capturedEditTexts.getOrNull(0)?.text = Editable.Factory.getInstance().newEditable(state.latitude.toString())
                    capturedEditTexts.getOrNull(1)?.text = Editable.Factory.getInstance().newEditable(state.longitude.toString())
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (isBound) { try { unbindService(connection) } catch(e: Exception){} ; isBound = false }
    }
}
