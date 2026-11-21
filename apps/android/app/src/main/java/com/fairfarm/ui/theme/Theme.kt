package com.fairfarm.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.unit.dp

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
        shapes = Shapes(
            small = RoundedCornerShape(14.dp),
            medium = RoundedCornerShape(22.dp),
            large = RoundedCornerShape(30.dp),
        ),
        content = content,
    )
}
