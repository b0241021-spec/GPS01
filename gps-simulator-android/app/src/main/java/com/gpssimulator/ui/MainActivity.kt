package com.gpssimulator.ui

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.Bundle
import android.os.IBinder
import android.text.Editable
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.gpssimulator.service.GPSSimulationService
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    private var simulationService: GPSSimulationService? = null
    private var isBound = false

    private var etLatitude: EditText? = null
    private var etLongitude: EditText? = null
    private var btnApply: Button? = null

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            val binder = service as GPSSimulationService.LocalBinder
            simulationService = binder.getService()
            isBound = true
            observeServiceState()
        }
        override fun onServiceDisconnected(name: ComponentName?) {
            isBound = false
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 動態加載佈局，避開直接寫死 R.layout 的編譯衝突
        val layoutId = resources.getIdentifier("activity_main", "layout", packageName)
        if (layoutId != 0) {
            setContentView(layoutId)
        }

        // 👑 黑科技核心：自動從整個畫面上把所有的 EditText 與 Button 撈出來
        val rootLayout = window.decorView.findViewById<ViewGroup>(android.R.id.content)
        val editTexts = mutableListOf<EditText>()
        val buttons = mutableListOf<Button>()
        
        findAllViews(rootLayout, editTexts, buttons)

        // 依序指派給對應元件 (防禦原廠配置)
        if (editTexts.size >= 2) {
            etLatitude = editTexts[0]
            etLongitude = editTexts[1]
        } else if (editTexts.size == 1) {
            etLatitude = editTexts[0]
        }

        if (buttons.isNotEmpty()) {
            btnApply = buttons[0]
        }

        // 設定觸發事件
        btnApply?.setOnClickListener {
            val lat = etLatitude?.text?.toString()?.toDoubleOrNull() ?: 0.0
            val lng = etLongitude?.text?.toString()?.toDoubleOrNull() ?: 0.0
            
            simulationService?.setTargetLocation(lat, lng)
            
            AlertDialog.Builder(this)
                .setTitle("提示")
                .setMessage("位置更新成功")
                .setPositiveButton("確定", null)
                .show()
        }

        // 綁定服務
        val intent = Intent(this, GPSSimulationService::class.java)
        bindService(intent, connection, Context.BIND_AUTO_CREATE)
    }

    // 遞迴尋找畫面上所有符合型態的 View，跳過 R.id 的綁定限制
    private fun findAllViews(view: View, editTexts: MutableList<EditText>, buttons: MutableList<Button>) {
        if (view is EditText) {
            editTexts.add(view)
        } else if (view is Button) {
            buttons.add(view)
        } else if (view is ViewGroup) {
            for (i in 0 until view.childCount) {
                findAllViews(view.getChildAt(i), editTexts, buttons)
            }
        }
    }

    private fun observeServiceState() {
        lifecycleScope.launch {
            simulationService?.uiState?.collect { state ->
                etLatitude?.text = Editable.Factory.getInstance().newEditable(state.latitude.toString())
                etLongitude?.text = Editable.Factory.getInstance().newEditable(state.longitude.toString())
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (isBound) {
            unbindService(connection)
            isBound = false
        }
    }
}
