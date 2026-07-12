package com.gpssimulator.ui
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.gpssimulator.R

class MainActivity : AppCompatActivity() {
    private var isSimulating = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 連結剛才建立的佈局檔
        setContentView(R.layout.activity_main)

        val tvStatus = findViewById<TextView>(R.id.tvStatus)
        val btnToggle = findViewById<Button>(R.id.btnToggle)

        btnToggle.setOnClickListener {
            isSimulating = !isSimulating
            if (isSimulating) {
                tvStatus.text = "目前狀態：模擬中 (正在模擬虛擬 GPS 位置...)"
                btnToggle.text = "停止模擬"
                btnToggle.setBackgroundColor(android.graphics.Color.RED)
            } else {
                tvStatus.text = "目前狀態：未啟動模擬"
                btnToggle.text = "啟動 GPS 模擬"
                btnToggle.setBackgroundColor(android.graphics.Color.parseColor("#2196F3"))
            }
        }
    }
    fun setTargetLocation(lat: Double, lng: Double) {}
}
