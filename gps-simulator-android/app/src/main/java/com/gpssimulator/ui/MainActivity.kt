package com.gpssimulator.ui

import android.Manifest
import android.content.*
import android.content.pm.PackageManager
import android.os.*
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.lifecycle.lifecycleScope
import com.gpssimulator.service.GPSSimulationService
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    private var service: GPSSimulationService? = null
    private var isBound = false

    private var etLat: EditText? = null
    private var etLng: EditText? = null
    private var tvCurrentGps: TextView? = null
    private var sbSpeed: SeekBar? = null
    private var sbDirection: SeekBar? = null
    private var tvSpeedVal: TextView? = null
    private var tvDirVal: TextView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val layoutId = resources.getIdentifier("activity_main", "layout", packageName)
        if (layoutId != 0) setContentView(layoutId)

        val reqs = mutableListOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) reqs.add(Manifest.permission.POST_NOTIFICATIONS)
        if (reqs.any { ActivityCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }) {
            ActivityCompat.requestPermissions(this, reqs.toTypedArray(), 101)
        }

        etLat = findViewByNames("et_latitude", "etLatitude", "latitude_input", "lat")
        etLng = findViewByNames("et_longitude", "etLongitude", "longitude_input", "lng")
        tvCurrentGps = findViewByNames("tv_current_location", "currentLocationText", "tvCurrentGps", "location_display", "gps_status")
        sbSpeed = findViewByNames("sb_speed", "speedSeekBar", "speed_bar", "seekBarSpeed")
        sbDirection = findViewByNames("sb_direction", "directionSeekBar", "direction_bar", "seekBarDirection")
        tvSpeedVal = findViewByNames("tv_speed_value", "speedValue", "speed_text")
        tvDirVal = findViewByNames("tv_direction_value", "directionValue", "direction_text")
        
        val swView = findViewByNames<android.view.View>("switch_simulate", "simulateSwitch", "btn_simulate", "toggle_simulate", "mock_switch")
        val btnTestView = findViewByNames<android.view.View>("btn_start_test", "startTestButton", "btn_test", "test_button", "start_test")

        // 👑 關鍵修復：滑塊滑動時，第一時間在 UI 主執行緒刷新畫面的數字，絕不延遲
        val seekListener = object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(s: SeekBar?, p: Int, f: Boolean) {
                if (s == sbSpeed) tvSpeedVal?.text = "$p km/hr"
                if (s == sbDirection) tvDirVal?.text = "$p°"
                syncParamsFromUi()
            }
            override fun onStartTrackingTouch(s: SeekBar?) {}
            override fun onStopTrackingTouch(s: SeekBar?) {}
        }
        sbSpeed?.setOnSeekBarChangeListener(seekListener)
        sbDirection?.setOnSeekBarChangeListener(seekListener)

        if (swView is CompoundButton) {
            swView.setOnCheckedChangeListener { _, isChecked -> service?.toggleSimulation(isChecked) }
        } else {
            swView?.setOnClickListener {
                it.isSelected = !it.isSelected
                service?.toggleSimulation(it.isSelected)
            }
        }

        btnTestView?.setOnClickListener {
            val currentStatus = service?.uiState?.value?.isTestRunning ?: false
            service?.toggleTest(!currentStatus)
            
            val nextStatus = !currentStatus
            etLat?.isEnabled = !nextStatus
            etLng?.isEnabled = !nextStatus
            sbSpeed?.isEnabled = !nextStatus
            sbDirection?.isEnabled = !nextStatus
            if (btnTestView is Button) {
                btnTestView.text = if (nextStatus) "停止測試" else "開始測試"
            }
        }

        val intent = Intent(this, GPSSimulationService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent) else startService(intent)
        bindService(intent, connection, Context.BIND_AUTO_CREATE)
    }

    private fun syncParamsFromUi() {
        val lat = etLat?.text?.toString()?.toDoubleOrNull() ?: 25.0330
        val lng = etLng?.text?.toString()?.toDoubleOrNull() ?: 121.5654
        val speed = sbSpeed?.progress?.toFloat() ?: 0f
        val dir = sbDirection?.progress ?: 0
        service?.updateParams(lat, lng, speed, dir)
    }

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(n: ComponentName?, s: IBinder?) {
            service = (s as GPSSimulationService.LocalBinder).getService()
            isBound = true
            observeState()
        }
        override fun onServiceDisconnected(n: ComponentName?) { isBound = false }
    }

    private fun observeState() {
        lifecycleScope.launch {
            service?.uiState?.collect { state ->
                // 👑 關鍵修復：強制在 Main 執行緒更新當前經緯度文字，防止真機無視 UI 更新
                withContext(Dispatchers.Main) {
                    val gpsFormattedText = String.format("當前位置 (經緯度): %.6f, %.6f", state.currentLatitude, state.currentLongitude)
                    tvCurrentGps?.text = gpsFormattedText
                }
            }
        }
    }

    private fun <T : android.view.View> findViewByNames(vararg names: String): T? {
        for (name in names) {
            val id = resources.getIdentifier(name, "id", packageName)
            if (id != 0) return findViewById(id)
        }
        return null
    }

    override fun onDestroy() {
        super.onDestroy()
        if (isBound) { unbindService(connection); isBound = false }
    }
}
