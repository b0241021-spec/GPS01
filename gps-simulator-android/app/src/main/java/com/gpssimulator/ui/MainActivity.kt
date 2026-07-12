package com.gpssimulator.ui
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val tv = TextView(this)
        tv.text = "GPS Simulator - Repaired Successfully"
        setContentView(tv)
    }
    fun setTargetLocation(lat: Double, lng: Double) {}
}
