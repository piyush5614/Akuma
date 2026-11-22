package com.fairfarm.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = Color(0xFF1F62DC),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFEDF4FF),
    secondary = Color(0xFFC8EE5A),
    onSecondary = Color(0xFF111827),
    background = Color(0xFFF6F8FC),
    surface = Color.White,
    surfaceVariant = Color(0xFFF1F5FB),
    onSurface = Color(0xFF111827),
    onSurfaceVariant = Color(0xFF687184),
    outline = Color(0xFFE4E8F0),
    error = Color(0xFFDF4A58)
)

@Composable
fun FairFarmTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColors,
        content = content
    )
}
