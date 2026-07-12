package com.gpssimulator.utils

import kotlin.math.*

data class GPSCoordinate(
    val latitude: Double,
    val longitude: Double
)

object GPSCalculator {
    private const val EARTH_RADIUS_KM = 6371.0

    private fun degreesToRadians(degrees: Double): Double {
        return (degrees * PI) / 180.0
    }

    private fun radiansToDegrees(radians: Double): Double {
        return (radians * 180.0) / PI
    }

    fun calculateNewLocation(
        startLocation: GPSCoordinate,
        directionDegrees: Double,
        distanceKm: Double
    ): GPSCoordinate {
        val lat1 = degreesToRadians(startLocation.latitude)
        val lon1 = degreesToRadians(startLocation.longitude)
        val bearing = degreesToRadians(directionDegrees)
        val angularDistance = distanceKm / EARTH_RADIUS_KM

        val lat2 = asin(
            sin(lat1) * cos(angularDistance) +
                    cos(lat1) * sin(angularDistance) * cos(bearing)
        )

        val lon2 = lon1 + atan2(
            sin(bearing) * sin(angularDistance) * cos(lat1),
            cos(angularDistance) - sin(lat1) * sin(lat2)
        )

        return GPSCoordinate(
            latitude = radiansToDegrees(lat2),
            longitude = radiansToDegrees(lon2)
        )
    }

    fun calculateDistance(speedKmHr: Double, intervalSeconds: Double): Double {
        return (speedKmHr / 3600.0) * intervalSeconds
    }

    fun calculateNextLocation(
        currentLocation: GPSCoordinate,
        direction: Double,
        speed: Double,
        intervalSeconds: Double
    ): GPSCoordinate {
        if (speed == 0.0) {
            return currentLocation
        }

        val distance = calculateDistance(speed, intervalSeconds)
        return calculateNewLocation(currentLocation, direction, distance)
    }

    fun normalizeDirection(direction: Double): Double {
        var normalized = direction % 360
        if (normalized < 0) {
            normalized += 360
        }
        return normalized
    }
}
