package com.gpssimulator.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.gpssimulator.R
import com.gpssimulator.data.GPSSimulatorStateManager
import com.gpssimulator.service.GPSSimulationService
import com.gpssimulator.utils.GPSCalculator
import com.gpssimulator.utils.GPSCoordinate
import com.gpssimulator.utils.LogManager
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    private lateinit var stateManager: GPSSimulatorStateManager
    private var lastSimulationTime = System.currentTimeMillis()

    // UI Components
    private lateinit var currentLocationDisplay: EditText
    private lateinit var targetLocationInput: EditText
    private lateinit var directionSlider: SeekBar
    private lateinit var speedSlider: SeekBar
    private lateinit var simulationSwitch: Switch
    private lateinit var movingSwitch: Switch
    private lateinit var startTestButton: Button
    private lateinit var stopTestButton: Button
    private lateinit var statusText: TextView
    private lateinit var directionText: TextView
    private lateinit var speedText: TextView

    private var isTestRunning = false
    private var testProgress = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            LogManager.init(this)
            LogManager.writeLog("MainActivity onCreate started")

            setContentView(R.layout.activity_main)
            stateManager = GPSSimulatorStateManager()

            initializeUI()
            requestPermissions()
            observeState()
            startSimulationLoop()

            LogManager.writeLog("MainActivity onCreate completed successfully")
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "onCreate failed", e)
            showErrorDialog("初始化失敗", e.message ?: "未知錯誤")
        }
    }

    private fun initializeUI() {
        try {
            LogManager.writeLog("Initializing UI components")

            currentLocationDisplay = findViewById(R.id.currentLocationDisplay)
            targetLocationInput = findViewById(R.id.targetLocationInput)
            directionSlider = findViewById(R.id.directionSlider)
            speedSlider = findViewById(R.id.speedSlider)
            simulationSwitch = findViewById(R.id.simulationSwitch)
            movingSwitch = findViewById(R.id.movingSwitch)
            startTestButton = findViewById(R.id.startTestButton)
            stopTestButton = findViewById(R.id.stopTestButton)
            statusText = findViewById(R.id.statusText)
            directionText = findViewById(R.id.directionText)
            speedText = findViewById(R.id.speedText)

            // 設定 currentLocationDisplay 為不可編輯
            currentLocationDisplay.isEnabled = false
            currentLocationDisplay.isFocusable = false
            currentLocationDisplay.text = "25.0330, 121.5654"

            // 設定 targetLocationInput 為可編輯
            targetLocationInput.isEnabled = true
            targetLocationInput.isFocusable = true
            targetLocationInput.text = "25.0330, 121.5654"

            // Direction Slider (0-359)
            directionSlider.max = 359
            directionSlider.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    if (fromUser) {
                        stateManager.updateDirection(progress.toDouble())
                        directionText.text = "方向: ${progress}°"
                    }
                }
                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })

            // Speed Slider (0-20 km/hr)
            speedSlider.max = 200
            speedSlider.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    if (fromUser) {
                        val speed = progress / 10.0
                        stateManager.updateSpeed(speed)
                        speedText.text = "速度: %.1f km/hr".format(speed)
                    }
                }
                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })

            // Simulation Switch
            simulationSwitch.setOnCheckedChangeListener { _, isChecked ->
                if (isChecked) {
                    try {
                        val targetText = targetLocationInput.text.toString().trim()
                        val parts = targetText.split(",")
                        if (parts.size == 2) {
                            val lat = parts[0].trim().toDouble()
                            val lng = parts[1].trim().toDouble()
                            stateManager.setTargetLocation(GPSCoordinate(lat, lng))
                            stateManager.startSimulation()
                            showToast("已設置 GPS 位置為: $lat, $lng")
                            LogManager.writeLog("Simulation started with location: $lat, $lng")
                        } else {
                            showToast("GPS 位置格式錯誤，請輸入: 緯度,經度")
                            simulationSwitch.isChecked = false
                        }
                    } catch (e: Exception) {
                        LogManager.writeError("MainActivity", "Failed to parse target location", e)
                        showToast("GPS 位置格式錯誤")
                        simulationSwitch.isChecked = false
                    }
                } else {
                    stateManager.stopSimulation()
                    movingSwitch.isChecked = false
                    showToast("已復原 GPS 訊號")
                    LogManager.writeLog("Simulation stopped")
                }
            }

            // Moving Switch
            movingSwitch.setOnCheckedChangeListener { _, isChecked ->
                if (isChecked && stateManager.state.value.isSimulating) {
                    stateManager.startMoving()
                    showToast("開始移動模擬")
                    LogManager.writeLog("Moving simulation started")
                } else {
                    stateManager.stopMoving()
                    showToast("停止移動模擬")
                    LogManager.writeLog("Moving simulation stopped")
                }
            }

            // Start Test Button
            startTestButton.setOnClickListener {
                if (!isTestRunning) {
                    startTestRunning()
                }
            }

            // Stop Test Button
            stopTestButton.setOnClickListener {
                if (isTestRunning) {
                    stopTestRunning()
                }
            }

            LogManager.writeLog("UI components initialized successfully")
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "initializeUI failed", e)
            throw e
        }
    }

    private fun observeState() {
        try {
            lifecycleScope.launch {
                stateManager.state.collect { state ->
                    try {
                        currentLocationDisplay.setText("${state.currentLocation.latitude.format(6)}, ${state.currentLocation.longitude.format(6)}")
                        directionSlider.progress = state.direction.toInt()
                        speedSlider.progress = (state.speed * 10).toInt()
                        simulationSwitch.isChecked = state.isSimulating
                        movingSwitch.isChecked = state.isMoving && state.isSimulating

                        statusText.text = state.statusMessage
                    } catch (e: Exception) {
                        LogManager.writeError("MainActivity", "observeState update failed", e)
                    }
                }
            }
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "observeState failed", e)
        }
    }

    private fun startSimulationLoop() {
        try {
            lifecycleScope.launch {
                while (true) {
                    try {
                        val state = stateManager.state.value
                        if (state.isSimulating && state.isMoving && state.speed > 0) {
                            val now = System.currentTimeMillis()
                            val elapsedSeconds = (now - lastSimulationTime) / 1000.0
                            lastSimulationTime = now

                            val newLocation = GPSCalculator.calculateNextLocation(
                                state.currentLocation,
                                state.direction,
                                state.speed,
                                elapsedSeconds.coerceAtMost(1.0)
                            )

                            stateManager.updateLocation(newLocation)
                        }
                        Thread.sleep(1000)
                    } catch (e: Exception) {
                        LogManager.writeError("MainActivity", "Simulation loop error", e)
                    }
                }
            }
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "startSimulationLoop failed", e)
        }
    }

    private fun startTestRunning() {
        try {
            isTestRunning = true
            testProgress = 0
            startTestButton.isEnabled = false
            directionSlider.isEnabled = false
            speedSlider.isEnabled = false
            simulationSwitch.isEnabled = false
            movingSwitch.isEnabled = false
            targetLocationInput.isEnabled = false

            showToast("開始移動模擬測試：20km/hr 往正東1000m，正西1000m，重複3次")
            LogManager.writeLog("Test running started")

            lifecycleScope.launch {
                try {
                    // Set initial location from target input
                    val targetText = targetLocationInput.text.toString().trim()
                    val parts = targetText.split(",")
                    if (parts.size == 2) {
                        val lat = parts[0].trim().toDouble()
                        val lng = parts[1].trim().toDouble()
                        stateManager.setTargetLocation(GPSCoordinate(lat, lng))
                        stateManager.startSimulation()
                        stateManager.updateSpeed(20.0)
                    }

                    // Run 3 cycles of east-west movement
                    for (cycle in 0..2) {
                        // Move east 1000m
                        stateManager.updateDirection(90.0)
                        directionSlider.progress = 90
                        statusText.text = "測試中: 第 ${cycle + 1}/3 週期，往正東移動..."
                        moveDistance(1000.0, 20.0)

                        // Move west 1000m
                        stateManager.updateDirection(270.0)
                        directionSlider.progress = 270
                        statusText.text = "測試中: 第 ${cycle + 1}/3 週期，往正西移動..."
                        moveDistance(1000.0, 20.0)
                    }

                    stopTestRunning()
                    showToast("移動模擬測試完成")
                } catch (e: Exception) {
                    LogManager.writeError("MainActivity", "Test running failed", e)
                    stopTestRunning()
                }
            }
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "startTestRunning failed", e)
        }
    }

    private suspend fun moveDistance(distance: Double, speed: Double) {
        val timeSeconds = (distance / 1000.0) / speed * 3600.0
        val steps = (timeSeconds * 1000).toInt() / 100
        for (i in 0..steps) {
            Thread.sleep(100)
        }
    }

    private fun stopTestRunning() {
        try {
            isTestRunning = false
            startTestButton.isEnabled = true
            directionSlider.isEnabled = true
            speedSlider.isEnabled = true
            simulationSwitch.isEnabled = true
            movingSwitch.isEnabled = true
            targetLocationInput.isEnabled = true

            stateManager.stopSimulation()
            movingSwitch.isChecked = false
            simulationSwitch.isChecked = false
            statusText.text = "已停止測試"

            showToast("移動模擬測試已停止，GPS 訊號已復原")
            LogManager.writeLog("Test running stopped")
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "stopTestRunning failed", e)
        }
    }

    private fun requestPermissions() {
        try {
            val permissions = mutableListOf(
                Manifest.permission.INTERNET,
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION,
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
                Manifest.permission.READ_EXTERNAL_STORAGE
            )

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                permissions.add(Manifest.permission.ACCESS_BACKGROUND_LOCATION)
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }

            val missingPermissions = permissions.filter {
                ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
            }

            if (missingPermissions.isNotEmpty()) {
                LogManager.writeLog("Requesting permissions: $missingPermissions")
                ActivityCompat.requestPermissions(
                    this,
                    missingPermissions.toTypedArray(),
                    PERMISSION_REQUEST_CODE
                )
            } else {
                LogManager.writeLog("All permissions already granted")
            }
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "requestPermissions failed", e)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        try {
            if (requestCode == PERMISSION_REQUEST_CODE) {
                val grantedPermissions = permissions.filterIndexed { index, _ ->
                    grantResults[index] == PackageManager.PERMISSION_GRANTED
                }
                LogManager.writeLog("Permissions granted: $grantedPermissions")
            }
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "onRequestPermissionsResult failed", e)
        }
    }

    private fun showErrorDialog(title: String, message: String) {
        try {
            AlertDialog.Builder(this)
                .setTitle(title)
                .setMessage(message)
                .setPositiveButton("確定") { _, _ -> }
                .show()
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "showErrorDialog failed", e)
        }
    }

    private fun showToast(message: String) {
        try {
            Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
            LogManager.writeLog("Toast: $message")
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "showToast failed", e)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            LogManager.writeLog("MainActivity onDestroy")
        } catch (e: Exception) {
            LogManager.writeError("MainActivity", "onDestroy failed", e)
        }
    }

    companion object {
        private const val PERMISSION_REQUEST_CODE = 100
    }
}

private fun Double.format(digits: Int): String = "%.${digits}f".format(this)
