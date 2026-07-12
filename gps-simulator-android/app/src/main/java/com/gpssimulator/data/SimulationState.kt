package com.gpssimulator.data
data class SimulationState(
    val latitude: Double = 25.0330,
    val longitude: Double = 121.5654,
    val currentLatitude: Double = 25.0330,
    val currentLongitude: Double = 121.5654,
    val isSimulating: Boolean = false,
    val speed: Float = 0f,
    val direction: Int = 0,
    val isTestRunning: Boolean = false
)
