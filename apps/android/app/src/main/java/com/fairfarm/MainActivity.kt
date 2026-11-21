package com.fairfarm

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.fairfarm.data.ApiFactory
import com.fairfarm.data.Coordinates
import com.fairfarm.domain.FairFarmRepository
import com.fairfarm.ui.FairFarmViewModel
import com.fairfarm.ui.ChatPanel
import com.fairfarm.ui.theme.FairFarmTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); setContent { FairFarmTheme { FarmerApp() } } }
}

@Composable
private fun FarmerApp() {
    val model: FairFarmViewModel = viewModel(factory = object : androidx.lifecycle.ViewModelProvider.Factory {
        override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T = FairFarmViewModel(FairFarmRepository(ApiFactory.api)) as T
    })
    val state by model.state.collectAsState()
    var crop by remember { mutableStateOf("onion") }
    var quantity by remember { mutableStateOf("10") }
    var screen by remember { mutableStateOf("home") }
    LaunchedEffect(Unit) { model.loadCrops() }
    Scaffold(bottomBar = { NavigationBar { listOf("home" to "Home", "insights" to "Insights", "ask" to "Ask", "settings" to "Settings").forEach { (key, label) -> NavigationBarItem(selected = screen == key, onClick = { screen = key }, icon = { Text(label.take(1)) }, label = { Text(label) }) } } }) { padding ->
        LazyColumn(Modifier.padding(padding).padding(20.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            item { Text("FairFarm", style = MaterialTheme.typography.labelLarge); Text(if (screen == "home") "More in your pocket." else screen.replaceFirstChar { it.uppercase() }, style = MaterialTheme.typography.headlineLarge) }
            if (state.offline) item { Text("Offline: showing the last available result.", color = MaterialTheme.colorScheme.error) }
            if (screen == "home") {
                item { OutlinedTextField(value = crop, onValueChange = { crop = it }, label = { Text("Crop") }, modifier = Modifier.fillMaxWidth()) }
                item { OutlinedTextField(value = quantity, onValueChange = { quantity = it }, label = { Text("Quantity (quintal)") }, modifier = Modifier.fillMaxWidth()) }
                item { Button(onClick = { model.recommend(crop, quantity.toDoubleOrNull() ?: 10.0, Coordinates(18.52, 73.86)) }, modifier = Modifier.fillMaxWidth()) { Text("Find best mandi") } }
                state.result?.let { result -> item { Text("${result.sell_or_wait.decision}: ${result.sell_or_wait.reason["en"]}") }; items(result.recommendations) { recommendation -> MandiCard(recommendation.mandi.name, recommendation.costs.total_net_inr, recommendation.mandi.freshness) } }
            } else if (screen == "ask") item { ChatPanel(model, state, crop, quantity) }
            else if (screen == "insights") item { Text("Seasonality and crop-profit insights will use the same backend data.") }
            else item { Text("Language, vehicle rate, water availability, and data freshness settings.") }
            if (state.loading) item { CircularProgressIndicator() }
            state.error?.let { message -> item { Text(message, color = MaterialTheme.colorScheme.error) } }
        }
    }
}

@Composable
private fun MandiCard(name: String, amount: String, freshness: String) {
    Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(16.dp)) { Text(name, style = MaterialTheme.typography.titleLarge); Text("₹$amount total net"); Text(freshness); Button(onClick = { /* Navigation is wired by the platform intent in the detail screen. */ }) { Text("Navigate") } } }
}
