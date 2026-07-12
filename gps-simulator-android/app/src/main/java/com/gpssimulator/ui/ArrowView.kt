package com.gpssimulator.ui

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.view.View
import kotlin.math.cos
import kotlin.math.sin

class ArrowView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var direction = 0.0
    private val paint = Paint().apply {
        isAntiAlias = true
        strokeWidth = 4f
        strokeCap = Paint.Cap.ROUND
        strokeJoin = Paint.Join.ROUND
    }

    fun setDirection(degrees: Double) {
        direction = degrees
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val centerX = width / 2f
        val centerY = height / 2f
        val radius = (minOf(width, height) / 2f) * 0.6f

        paint.color = Color.argb(100, 0, 122, 164)
        paint.style = Paint.Style.FILL
        canvas.drawCircle(centerX, centerY, radius + 20, paint)

        paint.color = Color.argb(200, 0, 122, 164)
        paint.style = Paint.Style.STROKE

        val radians = Math.toRadians(direction - 90)

        val arrowEndX = centerX + (radius * cos(radians)).toFloat()
        val arrowEndY = centerY + (radius * sin(radians)).toFloat()

        canvas.drawLine(centerX, centerY, arrowEndX, arrowEndY, paint)

        val arrowHeadSize = 30f
        val angle1 = radians + Math.toRadians(150.0)
        val angle2 = radians - Math.toRadians(150.0)

        val headX1 = arrowEndX + (arrowHeadSize * cos(angle1)).toFloat()
        val headY1 = arrowEndY + (arrowHeadSize * sin(angle1)).toFloat()
        val headX2 = arrowEndX + (arrowHeadSize * cos(angle2)).toFloat()
        val headY2 = arrowEndY + (arrowHeadSize * sin(angle2)).toFloat()

        canvas.drawLine(arrowEndX, arrowEndY, headX1, headY1, paint)
        canvas.drawLine(arrowEndX, arrowEndY, headX2, headY2, paint)

        paint.textSize = 40f
        paint.style = Paint.Style.FILL
        paint.color = Color.WHITE
        val directionText = "${direction.toInt()}°"
        val textBounds = Rect()
        paint.getTextBounds(directionText, 0, directionText.length, textBounds)
        canvas.drawText(
            directionText,
            centerX - textBounds.width() / 2,
            centerY + textBounds.height() / 2,
            paint
        )

        paint.textSize = 30f
        drawDirectionLabel(canvas, "N", centerX, centerY - radius - 40, paint)
        drawDirectionLabel(canvas, "E", centerX + radius + 40, centerY, paint)
        drawDirectionLabel(canvas, "S", centerX, centerY + radius + 40, paint)
        drawDirectionLabel(canvas, "W", centerX - radius - 40, centerY, paint)
    }

    private fun drawDirectionLabel(canvas: Canvas, label: String, x: Float, y: Float, paint: Paint) {
        paint.color = Color.WHITE
        val textBounds = Rect()
        paint.getTextBounds(label, 0, label.length, textBounds)
        canvas.drawText(label, x - textBounds.width() / 2, y + textBounds.height() / 2, paint)
    }
}
