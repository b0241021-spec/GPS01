package com.gpssimulator.data
data class SimulationState(
    val isRunning: Boolean = false,
    val currentSpeed: Double = 0.0,
    val latitude: Double = 0.0,
    val longitude: Double = 0.0,
    val progress: Int = 0,
    val speedMultiplier: Float = 1.0f,
    val statusText: String = "",
    val currentLocation: String = "0.0, 0.0",
    val direction: Float = 0.0f,
    val speed: Double = 0.0,
    val isSimulating: Boolean = false,
    val isMoving: Boolean = false,
    val statusMessage: String = ""
)
