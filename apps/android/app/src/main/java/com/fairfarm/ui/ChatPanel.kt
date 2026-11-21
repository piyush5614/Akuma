package com.fairfarm.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.fairfarm.data.Coordinates

@Composable
fun ChatPanel(model: FairFarmViewModel, state: FarmerState, crop: String, quantity: String, location: Coordinates) {
    var message by remember { mutableStateOf("") }
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("Saathi", style = MaterialTheme.typography.headlineSmall)
        Text("Ask about mandi prices, net returns, selling, or crops.")
        if (state.chatMessages.isEmpty()) {
            Text("Try one of these:")
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { message = "Which nearby mandi gives the best net return?" }) { Text("Best mandi") }
                Button(onClick = { message = "Should I sell now?" }) { Text("Sell or wait") }
            }
        }
        state.chatMessages.forEach { chatMessage ->
            Text(
                text = if (chatMessage.fromFarmer) "You: ${chatMessage.text}" else "Saathi: ${chatMessage.text}",
                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
            )
        }
        HorizontalDivider()
        OutlinedTextField(
            value = message,
            onValueChange = { message = it },
            label = { Text("Ask Saathi") },
            enabled = !state.chatSending,
            modifier = Modifier.fillMaxWidth(),
        )
        Button(
            onClick = {
                model.sendChat(message, crop, quantity.toDoubleOrNull(), location)
                message = ""
            },
            enabled = message.isNotBlank() && !state.chatSending,
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Send") }
        Button(onClick = model::clearChat, modifier = Modifier.fillMaxWidth()) { Text("Clear chat") }
        if (state.chatSending) CircularProgressIndicator()
    }
}
