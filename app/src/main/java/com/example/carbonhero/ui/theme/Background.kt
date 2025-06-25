package com.example.carbonhero.ui.theme

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import com.example.carbonhero.R

@Composable
fun CarbonHeroBackground(
    content: @Composable BoxScope.() -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF1B5E20),  // Koyu Yeşil
                        Color(0xFF388E3C)   // Açık Yeşil
                    )
                )
            )
    ) {
        // Arka plan görseli
        Image(
            painter = painterResource(id = R.drawable.background),
            contentDescription = "Carbon Footprint Background",
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop,
            alpha = 0.6f  // Görsel opaklığı
        )

        // Sayfa içeriği
        content()
    }
}