package com.gpssimulator.utils

import android.content.Context
import android.os.Environment
import android.util.Log
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

object LogManager {
    private const val TAG = "GPSSimulator"
    private var logFile: File? = null
    private var context: Context? = null

    fun init(ctx: Context) {
        context = ctx
        createLogFile()
    }

    private fun createLogFile() {
        try {
            val logsDir = File(context?.getExternalFilesDir(null), "logs")
            if (!logsDir.exists()) {
                logsDir.mkdirs()
            }

            val timestamp = SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.getDefault()).format(Date())
            logFile = File(logsDir, "gps_simulator_$timestamp.log")
            logFile?.createNewFile()

            writeLog("=== GPS Simulator Log Started ===")
            writeLog("Device Info: ${android.os.Build.DEVICE}")
            writeLog("Android Version: ${android.os.Build.VERSION.SDK_INT}")
            writeLog("Manufacturer: ${android.os.Build.MANUFACTURER}")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to create log file", e)
        }
    }

    fun writeLog(message: String) {
        val timestamp = SimpleDateFormat("HH:mm:ss.SSS", Locale.getDefault()).format(Date())
        val logMessage = "[$timestamp] $message"

        Log.d(TAG, message)

        try {
            logFile?.appendText("$logMessage\n")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to write log", e)
        }
    }

    fun writeError(tag: String, message: String, exception: Exception? = null) {
        val errorMessage = if (exception != null) {
            "$tag: $message\n${exception.stackTraceToString()}"
        } else {
            "$tag: $message"
        }

        writeLog("ERROR: $errorMessage")
        Log.e(TAG, errorMessage, exception)
    }

    fun getLogFile(): File? = logFile

    fun getLogsDirectory(): File? {
        return try {
            File(context?.getExternalFilesDir(null), "logs")
        } catch (e: Exception) {
            null
        }
    }

    fun getAllLogs(): List<File> {
        return try {
            getLogsDirectory()?.listFiles()?.toList() ?: emptyList()
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun clearOldLogs(daysToKeep: Int = 7) {
        try {
            val logsDir = getLogsDirectory() ?: return
            val currentTime = System.currentTimeMillis()
            val cutoffTime = currentTime - (daysToKeep * 24 * 60 * 60 * 1000L)

            logsDir.listFiles()?.forEach { file ->
                if (file.lastModified() < cutoffTime) {
                    file.delete()
                }
            }
        } catch (e: Exception) {
            writeError("LogManager", "Failed to clear old logs", e)
        }
    }
}
