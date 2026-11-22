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
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Place
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.fairfarm.data.AdminSettings
import com.fairfarm.data.RegionPrice
import com.fairfarm.data.CropProfit
import com.fairfarm.data.Recommendation

private data class BottomDestination(
    val route: String,
    val label: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector
)

@Composable
fun FairFarmApp() {
    val model: FairFarmViewModel = viewModel()
    val state by model.state.collectAsState()
    val nav = rememberNavController()
    var start by remember { mutableStateOf(if (model.isLoggedIn()) "main" else "login") }

    if (start == "login") {
        LoginScreen(
            loading = state.loading,
            error = state.error,
            onLogin = { email, password ->
                model.login(email, password) {
                    start = "main"
                }
            }
        )
    } else {
        MainShell(nav, model, state)
    }
}

@Composable
private fun LoginScreen(
    loading: Boolean,
    error: String?,
    onLogin: (String, String) -> Unit
) {
    var email by remember { mutableStateOf("admin@example.com") }
    var password by remember { mutableStateOf("change-me") }
    var visible by remember { mutableStateOf(false) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    listOf(Color(0xFFEAF2FF), Color(0xFFF8FAFD), Color(0xFFDDEAFF))
                )
            )
            .statusBarsPadding(),
        contentAlignment = Alignment.TopCenter
    ) {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            contentPadding = PaddingValues(top = 28.dp, bottom = 32.dp)
        ) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(24.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = .92f)),
                    elevation = CardDefaults.cardElevation(defaultElevation = 16.dp)
                ) {
                    Column {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(240.dp)
                                .background(
                                    Brush.linearGradient(
                                        listOf(Color(0xFF1761D8), Color(0xFF2878EF))
                                    )
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Box(
                                    modifier = Modifier
                                        .height(64.dp)
                                        .width(64.dp)
                                        .background(Color.White.copy(alpha = .14f), CircleShape),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(Icons.Filled.AccountCircle, null, tint = Color.White)
                                }
                                Spacer(Modifier.height(10.dp))
                                Text(
                                    "FairFarm",
                                    color = Color.White,
                                    fontSize = 30.sp,
                                    fontWeight = FontWeight.Black
                                )
                                Text(
                                    "Farmer Market Intelligence",
                                    color = Color(0xFFEAF2FF),
                                    fontSize = 13.sp
                                )
                            }
                        }
                        Column(
                            modifier = Modifier.padding(24.dp),
                            verticalArrangement = Arrangement.spacedBy(14.dp)
                        ) {
                            Text(
                                "Welcome back",
                                color = Color(0xFF1F62DC),
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Black
                            )
                            Text(
                                "Continue to your dashboard",
                                fontSize = 20.sp,
                                fontWeight = FontWeight.Bold
                            )
                            OutlinedTextField(
                                value = email,
                                onValueChange = { email = it },
                                modifier = Modifier.fillMaxWidth(),
                                label = { Text("Email address or Officer ID") },
                                singleLine = true
                            )
                            OutlinedTextField(
                                value = password,
                                onValueChange = { password = it },
                                modifier = Modifier.fillMaxWidth(),
                                label = { Text("Password") },
                                singleLine = true,
                                visualTransformation = if (visible) VisualTransformation.None else PasswordVisualTransformation(),
                                trailingIcon = {
                                    IconButton(onClick = { visible = !visible }) {
                                        Text(if (visible) "Hide" else "Show", fontSize = 10.sp)
                                    }
                                }
                            )
                            error?.let {
                                Text(it, color = Color(0xFFB83D48), fontSize = 12.sp)
                            }
                            Button(
                                onClick = { onLogin(email, password) },
                                enabled = !loading,
                                modifier = Modifier.fillMaxWidth().height(52.dp),
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                if (loading) CircularProgressIndicator(
                                    modifier = Modifier.width(20.dp).height(20.dp),
                                    color = Color.White,
                                    strokeWidth = 2.dp
                                ) else Text("Sign in to dashboard", fontWeight = FontWeight.Black)
                            }
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                Card(
                                    modifier = Modifier.weight(1f),
                                    colors = CardDefaults.cardColors(containerColor = Color(0xFFF8FAFD)),
                                    onClick = { email = "admin@example.com"; password = "change-me" }
                                ) {
                                    Column(Modifier.padding(12.dp)) {
                                        Text("Admin", fontWeight = FontWeight.Bold)
                                        Text("Demo account", color = Color(0xFF687184), fontSize = 11.sp)
                                    }
                                }
                                Card(
                                    modifier = Modifier.weight(1f),
                                    colors = CardDefaults.cardColors(containerColor = Color(0xFFF8FAFD)),
                                    onClick = { email = "admin@example.com"; password = "change-me" }
                                ) {
                                    Column(Modifier.padding(12.dp)) {
                                        Text("Officer", fontWeight = FontWeight.Bold)
                                        Text("Demo account", color = Color(0xFF687184), fontSize = 11.sp)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun MainShell(
    nav: NavHostController,
    model: FairFarmViewModel,
    state: FairFarmState
) {
    val destinations = listOf(
        BottomDestination("dashboard", "Overview", Icons.Filled.Home),
        BottomDestination("explorer", "Explorer", Icons.Filled.Place),
        BottomDestination("regions", "Regions", Icons.Filled.Place),
        BottomDestination("insights", "Insights", Icons.Filled.Info),
        BottomDestination("saathi", "Saathi", Icons.Filled.AccountCircle),
        BottomDestination("settings", "Settings", Icons.Filled.Settings)
    )
    val backStack by nav.currentBackStackEntryAsState()
    val currentRoute = backStack?.destination?.route

    Scaffold(
        containerColor = Color(0xFFF6F8FC),
        bottomBar = {
            NavigationBar {
                destinations.forEach { destination ->
                    NavigationBarItem(
                        selected = currentRoute == destination.route,
                        onClick = {
                            nav.navigate(destination.route) {
                                launchSingleTop = true
                            }
                        },
                        icon = { Icon(destination.icon, contentDescription = destination.label) },
                        label = { Text(destination.label) }
                    )
                }
            }
        }
    ) { padding ->
        NavHost(
            navController = nav,
            startDestination = "dashboard",
            modifier = Modifier.padding(padding)
        ) {
            composable("dashboard") { DashboardScreen(model, state) }
            composable("explorer") { ExplorerScreen(model, state) }
            composable("regions") { RegionsScreen(model, state) }
            composable("insights") { InsightsScreen(model, state) }
            composable("saathi") { SaathiScreen(model, state) }
            composable("settings") { SettingsScreen(model, state) }
        }
    }
}
