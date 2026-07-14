package com.gpssimulator.data

import com.gpssimulator.utils.GPSCoordinate
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class SimulationState(
    val currentLocation: GPSCoordinate = GPSCoordinate(25.0330, 121.5654),
    val direction: Double = 0.0,
    val speed: Double = 0.0,
    val scale: Double = 100.0,
    val isSimulating: Boolean = false,
    val isMoving: Boolean = false,
    val statusMessage: String = ""
)

class GPSSimulatorStateManager {
    private val _state = MutableStateFlow(SimulationState())
    val state: StateFlow<SimulationState> = _state.asStateFlow()

    fun updateLocation(location: GPSCoordinate) {
        _state.value = _state.value.copy(currentLocation = location)
    }

    fun updateDirection(direction: Double) {
        val normalized = direction % 360
        _state.value = _state.value.copy(direction = if (normalized < 0) normalized + 360 else normalized)
    }

    fun updateSpeed(speed: Double) {
        val clamped = speed.coerceIn(0.0, 20.0)
        _state.value = _state.value.copy(speed = clamped)
    }

    fun updateScale(scale: Double) {
        val clamped = scale.coerceIn(1.0, 300.0)
        _state.value = _state.value.copy(scale = clamped)
    }

    fun startSimulation() {
        _state.value = _state.value.copy(
            isSimulating = true,
            statusMessage = "✓ GPS 模擬已啟動"
        )
    }

    fun stopSimulation() {
        _state.value = _state.value.copy(
            isSimulating = false,
            isMoving = false,
            statusMessage = "✓ GPS 模擬已復原"
        )
    }

    fun startMoving() {
        if (_state.value.isSimulating) {
            _state.value = _state.value.copy(
                isMoving = true,
                statusMessage = "✓ GPS 模擬已啟動：移動中"
            )
        }
    }

    fun stopMoving() {
        _state.value = _state.value.copy(
            isMoving = false,
            statusMessage = if (_state.value.isSimulating) "✓ GPS 模擬已啟動：已停止" else ""
        )
    }

    fun setStatusMessage(message: String) {
        _state.value = _state.value.copy(statusMessage = message)
    }

    fun reset() {
        _state.value = SimulationState()
    }
}
