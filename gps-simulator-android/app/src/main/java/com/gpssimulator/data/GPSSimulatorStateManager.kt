package com.gpssimulator.data
import com.gpssimulator.data.SimulationState
object GPSSimulatorStateManager {
    var state = SimulationState()
    fun updateState(newState: SimulationState) { state = newState }
    fun setTargetLocation(latitude: Double, longitude: Double) {}
    fun setTargetLocation(latitude: String, longitude: String) {}
}