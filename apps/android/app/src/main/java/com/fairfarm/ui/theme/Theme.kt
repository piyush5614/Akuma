package com.fairfarm.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val FairFarmLightColors = lightColorScheme(
    primary = FairFarmInk,
    onPrimary = FairFarmSurface,
    secondary = FairFarmAccent,
    onSecondary = FairFarmInk,
    background = FairFarmCanvas,
    surface = FairFarmSurface,
    outline = FairFarmLine,
    error = FairFarmDanger,
)

@Composable
fun FairFarmTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = FairFarmLightColors,
        content = content,
    )
}
