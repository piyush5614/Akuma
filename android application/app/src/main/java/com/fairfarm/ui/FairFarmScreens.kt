package com.fairfarm.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fairfarm.data.AdminSettings
import com.fairfarm.data.CropProfit

@Composable
fun DashboardScreen(model: FairFarmViewModel, state: FairFarmState) {
    LaunchedEffect(Unit) {
        model.recommend("onion", 10.0)
    }
    NativeScreenTitle("Overview", "Welcome back, Officer")
    if (state.loading) {
        CenterLoading()
    } else if (state.error != null) {
        ErrorCard(state.error) { model.recommend("onion", 10.0) }
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                val best = state.recommend?.recommendations?.firstOrNull()
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF1F62DC)),
                    elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(20.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Today's best net return", color = Color(0xFFDDEAFF), fontSize = 12.sp)
                            Text(
                                best?.mandi?.name ?: "Loading market",
                                color = Color.White,
                                fontSize = 26.sp,
                                fontWeight = FontWeight.Black
                            )
                            Text("Onion · 10 quintal", color = Color(0xFFDDEAFF), fontSize = 12.sp)
                        }
                        Text(
                            "₹${best?.costs?.total_net_inr ?: "—"}",
                            color = Color.White,
                            fontSize = 22.sp,
                            fontWeight = FontWeight.Black
                        )
                    }
                }
            }
            item {
                MetricRow(state.recommend)
            }
            val recommendations = state.recommend?.recommendations.orEmpty()
            if (recommendations.isEmpty()) {
                item { EmptyCard("No ranked mandis available for this crop.") }
            } else {
                item {
                    Text("Top mandis", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                }
                items(recommendations) { item ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = Color.White),
                        shape = RoundedCornerShape(14.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(14.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Box(
                                modifier = Modifier.size(34.dp).background(Color(0xFFEDF4FF), CircleShape),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(item.rank.toString(), color = Color(0xFF1F62DC), fontWeight = FontWeight.Bold)
                            }
                            Spacer(Modifier.width(12.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(item.mandi.name, fontWeight = FontWeight.Bold)
                                Text(
                                    "${item.distance_km} km · ${item.mandi.freshness}",
                                    color = Color(0xFF687184),
                                    fontSize = 11.sp
                                )
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text(
                                    "₹${item.costs.net_per_quintal_inr}/q",
                                    color = Color(0xFF1F62DC),
                                    fontWeight = FontWeight.Bold
                                )
                                Text("₹${item.costs.total_net_inr}", fontSize = 11.sp)
                            }
                        }
                    }
                }
            }
            state.recommend?.sell_or_wait?.let { guidance ->
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFFFF8E8)),
                        shape = RoundedCornerShape(14.dp)
                    ) {
                        Column(Modifier.padding(16.dp)) {
                            Text("SELL GUIDANCE", color = Color(0xFF956400), fontSize = 10.sp, fontWeight = FontWeight.Black)
                            Text(guidance.decision.replace("_", " "), fontSize = 20.sp, fontWeight = FontWeight.Black)
                            Text(guidance.reason.en, color = Color(0xFF596275))
                            Text(guidance.disclaimer, color = Color(0xFF929AAA), fontSize = 11.sp)
                        }
                    }
                }
            }
            item { Spacer(Modifier.height(8.dp)) }
        }
    }
}

@Composable
private fun MetricRow(recommend: com.fairfarm.data.RecommendResult?) {
    val best = recommend?.recommendations?.firstOrNull()
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        MetricCard("Top mandi", best?.mandi?.name ?: "—", Modifier.weight(1f))
        MetricCard("Net / quintal", "₹${best?.costs?.net_per_quintal_inr ?: "—"}", Modifier.weight(1f))
    }
}

@Composable
private fun MetricCard(label: String, value: String, modifier: Modifier) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = Color.White),
        shape = RoundedCornerShape(14.dp)
    ) {
        Column(Modifier.padding(14.dp)) {
            Text(label, color = Color(0xFF687184), fontSize = 11.sp)
            Text(value, fontSize = 18.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun ExplorerScreen(model: FairFarmViewModel, state: FairFarmState) {
    var cropId by remember { mutableStateOf("onion") }
    var quantity by remember { mutableStateOf("10") }
    LaunchedEffect(Unit) {
        model.loadCrops()
        model.recommend(cropId, 10.0)
    }
    NativeScreenTitle("Price Explorer", "Where should you sell?")
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("Crop", fontSize = 11.sp, color = Color(0xFF687184))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        listOf("onion", "tomato", "soybean", "wheat").forEach { crop ->
                            FilterChip(
                                selected = cropId == crop,
                                onClick = { cropId = crop },
                                label = { Text(crop.replaceFirstChar { it.uppercase() }) }
                            )
                        }
                    }
                    OutlinedTextField(
                        value = quantity,
                        onValueChange = { quantity = it.filter(Char::isDigit) },
                        label = { Text("Quantity in quintal") },
                        modifier = Modifier.fillMaxWidth(),
                        leadingIcon = { Icon(Icons.Filled.LocationOn, null) }
                    )
                    Button(
                        onClick = {
                            val amount = quantity.toDoubleOrNull()?.coerceIn(0.1, 10000.0) ?: 10.0
                            model.recommend(cropId, amount)
                        },
                        modifier = Modifier.fillMaxWidth().height(50.dp)
                    ) {
                        Text("Find markets")
                    }
                }
            }
        }
        if (state.loading) item { CenterLoading() }
        state.error?.let { error ->
            item { ErrorCard(error) { model.recommend(cropId, quantity.toDoubleOrNull() ?: 10.0) } }
        }
        val recommendations = state.recommend?.recommendations.orEmpty()
        if (recommendations.isEmpty() && !state.loading) {
            item { EmptyCard("No ranked markets found. Try another crop.") }
        } else {
            items(recommendations) { item ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color.White)
                ) {
                    Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier.size(34.dp).background(Color(0xFFEDF4FF), CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(item.rank.toString(), color = Color(0xFF1F62DC), fontWeight = FontWeight.Bold)
                        }
                        Spacer(Modifier.width(10.dp))
                        Column(Modifier.weight(1f)) {
                            Text(item.mandi.name, fontWeight = FontWeight.Bold)
                            Text("${item.distance_km} km · ${item.mandi.freshness}", fontSize = 11.sp, color = Color(0xFF687184))
                        }
                        Text("₹${item.costs.total_net_inr}", fontWeight = FontWeight.Bold, color = Color(0xFF1F62DC))
                    }
                }
            }
        }
    }
}

@Composable
fun RegionsScreen(model: FairFarmViewModel, state: FairFarmState) {
    var cropId by remember { mutableStateOf("onion") }
    LaunchedEffect(cropId) { model.loadRegions(cropId) }
    NativeScreenTitle("Regions", "Compare market districts")
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("onion", "tomato", "soybean", "wheat").forEach { crop ->
                    FilterChip(
                        selected = cropId == crop,
                        onClick = { cropId = crop },
                        label = { Text(crop.replaceFirstChar { it.uppercase() }) }
                    )
                }
            }
        }
        if (state.loading) item { CenterLoading() }
        state.error?.let { item { ErrorCard(it) { model.loadRegions(cropId) } } }
        val regions = state.regions
        if (regions.isEmpty() && !state.loading) {
            item { EmptyCard("No regional market data is available.") }
        } else {
            items(regions) { region ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Row(
                        Modifier.fillMaxWidth().padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(Modifier.weight(1f)) {
                            Text(region.name, fontWeight = FontWeight.Bold)
                            Text(
                                "${region.mandi_count} mandi${if (region.mandi_count == 1) "" else "s"} · ${region.freshness}",
                                color = Color(0xFF687184),
                                fontSize = 11.sp
                            )
                        }
                        Text(
                            region.average_modal_price_inr?.let { "₹${it}" } ?: "—",
                            color = Color(0xFF1F62DC),
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun InsightsScreen(model: FairFarmViewModel, state: FairFarmState) {
    var water by remember { mutableStateOf("medium") }
    LaunchedEffect(water) { model.loadInsights("onion", water) }
    NativeScreenTitle("Insights", "Signals for the next decision")
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("low", "medium", "high").forEach { option ->
                    FilterChip(
                        selected = water == option,
                        onClick = { water = option },
                        label = { Text(option.replaceFirstChar { it.uppercase() }) }
                    )
                }
            }
        }
        if (state.loading) item { CenterLoading() }
        state.error?.let { item { ErrorCard(it) { model.loadInsights("onion", water) } } }
        state.seasonality?.let { seasonality ->
            item {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(16.dp)) {
                        Text("Monthly seasonality", fontWeight = FontWeight.Bold)
                        Text("Best months: ${seasonality.best_months.joinToString()}",
                            color = Color(0xFF1F62DC),
                            fontWeight = FontWeight.Bold)
                        Text("Lowest months: ${seasonality.worst_months.joinToString()}",
                            color = Color(0xFF687184))
                    }
                }
            }
        }
        items(state.cropProfits) { profit ->
            CropProfitCard(profit)
        }
    }
}

@Composable
private fun CropProfitCard(profit: CropProfit) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(14.dp)) {
            Text(profit.crop_id.replaceFirstChar { it.uppercase() }, fontWeight = FontWeight.Bold)
            Text(
                "₹${profit.risk_adjusted_midpoint_inr_per_acre}/acre",
                color = Color(0xFF1F62DC),
                fontWeight = FontWeight.Bold
            )
            Text("Water fit: ${profit.water_fit}", color = Color(0xFF687184), fontSize = 12.sp)
            Text("Source: ${profit.source}", color = Color(0xFF929AAA), fontSize = 11.sp)
        }
    }
}

@Composable
fun SaathiScreen(model: FairFarmViewModel, state: FairFarmState) {
    var message by remember { mutableStateOf("") }
    val chatMessages = state.chatMessages
    NativeScreenTitle("Saathi", "Your farming companion")
    Column(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            modifier = Modifier.weight(1f),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            item {
                Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFEDF4FF))) {
                    Text(
                        "Namaskar! Ask me for mandi prices, sell guidance, trends, or crop ideas.",
                        modifier = Modifier.padding(14.dp)
                    )
                }
            }
            items(chatMessages) { chat ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Text(chat.reply.text, modifier = Modifier.padding(14.dp))
                }
            }
        }
        Row(
            modifier = Modifier.fillMaxWidth().padding(12.dp),
            verticalAlignment = Alignment.Bottom
        ) {
            OutlinedTextField(
                value = message,
                onValueChange = { message = it },
                modifier = Modifier.weight(1f),
                label = { Text("Ask Saathi") },
                maxLines = 3
            )
            Spacer(Modifier.width(8.dp))
            IconButton(
                onClick = {
                    val text = message.trim()
                    if (text.isNotBlank()) {
                        message = ""
                        model.chat(text)
                    }
                },
                modifier = Modifier.size(52.dp).background(Color(0xFF1F62DC), CircleShape)
            ) {
                Icon(Icons.Filled.Send, null, tint = Color.White)
            }
        }
    }
}

@Composable
fun SettingsScreen(model: FairFarmViewModel, state: FairFarmState) {
    LaunchedEffect(Unit) { model.loadSettings() }
    NativeScreenTitle("Settings", "Backend calculation assumptions")
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        if (state.loading) item { CenterLoading() }
        state.error?.let { item { ErrorCard(it) { model.loadSettings() } } }
        state.settings?.let { settings ->
            item {
                SettingsCard(settings) { updated ->
                    model.saveSettings(updated)
                }
            }
        }
    }
}

@Composable
private fun SettingsCard(settings: AdminSettings, onSave: (AdminSettings) -> Unit) {
    var roadFactor by remember(settings) { mutableStateOf(settings.road_factor) }
    var transport by remember(settings) { mutableStateOf(settings.transport_rate_per_quintal_km) }
    var fee by remember(settings) { mutableStateOf(settings.fee_pct) }
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            OutlinedTextField(roadFactor, { roadFactor = it }, Modifier.fillMaxWidth(), label = { Text("Road factor") })
            OutlinedTextField(transport, { transport = it }, Modifier.fillMaxWidth(), label = { Text("Transport ₹ / quintal-km") })
            OutlinedTextField(fee, { fee = it }, Modifier.fillMaxWidth(), label = { Text("Fee percentage") })
            Button(
                onClick = {
                    onSave(settings.copy(
                        road_factor = roadFactor,
                        transport_rate_per_quintal_km = transport,
                        fee_pct = fee
                    ))
                },
                modifier = Modifier.fillMaxWidth()
            ) { Text("Save settings") }
        }
    }
}

@Composable
private fun NativeScreenTitle(title: String, subtitle: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(Brush.linearGradient(listOf(Color(0xFF1F62DC), Color(0xFF2878EF))))
            .padding(start = 20.dp, end = 20.dp, top = 44.dp, bottom = 18.dp)
    ) {
        Text(title, color = Color.White, fontSize = 26.sp, fontWeight = FontWeight.Black)
        Text(subtitle, color = Color(0xFFDDEAFF), fontSize = 13.sp)
    }
}

@Composable
private fun CenterLoading() {
    Box(Modifier.fillMaxWidth().height(180.dp), contentAlignment = Alignment.Center) {
        CircularProgressIndicator()
    }
}

@Composable
private fun EmptyCard(text: String) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.fillMaxWidth().padding(18.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(Icons.Filled.CheckCircle, null, tint = Color(0xFF687184))
            Spacer(Modifier.height(6.dp))
            Text(text, color = Color(0xFF687184))
        }
    }
}

@Composable
private fun ErrorCard(error: String, retry: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFFDECEF))
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Filled.Warning, null, tint = Color(0xFFB83D48))
                Spacer(Modifier.width(8.dp))
                Text(error, color = Color(0xFFB83D48), fontWeight = FontWeight.Bold)
            }
            Button(onClick = retry) {
                Icon(Icons.Filled.Refresh, null)
                Spacer(Modifier.width(6.dp))
                Text("Try again")
            }
        }
    }
}
