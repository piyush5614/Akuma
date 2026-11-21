package com.fairfarm.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fairfarm.data.*
import com.fairfarm.domain.FairFarmRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class ChatMessage(val text: String, val fromFarmer: Boolean, val speakText: String = text)
data class FarmerState(val loading: Boolean = false, val crops: List<Crop> = emptyList(), val result: RecommendResult? = null, val nextCrops: List<NextCrop> = emptyList(), val error: String? = null, val offline: Boolean = false, val chatMessages: List<ChatMessage> = emptyList(), val chatSending: Boolean = false, val chatSessionId: String? = null)

class FairFarmViewModel(private val repository: FairFarmRepository) : ViewModel() {
    private val _state = MutableStateFlow(FarmerState())
    val state: StateFlow<FarmerState> = _state
    fun loadCrops() { viewModelScope.launch { _state.value = _state.value.copy(loading = true); runCatching { repository.crops() }.onSuccess { _state.value = _state.value.copy(loading = false, crops = it) }.onFailure { _state.value = _state.value.copy(loading = false, error = "Could not load crops. Check your connection.", offline = true) } } }
    fun recommend(crop: String, quantity: Double, location: Coordinates) { viewModelScope.launch { _state.value = _state.value.copy(loading = true, error = null); runCatching { repository.recommend(crop, quantity, location) }.onSuccess { _state.value = _state.value.copy(loading = false, result = it) }.onFailure { _state.value = _state.value.copy(loading = false, error = "Could not calculate returns. Try again.", offline = true) } } }
    fun suggestNextCrops(category: String, crop: String, water: String) { viewModelScope.launch { runCatching { repository.nextCrops(category, listOf(crop), water) }.onSuccess { _state.value = _state.value.copy(nextCrops = it, error = null) }.onFailure { _state.value = _state.value.copy(error = "Could not load crop suggestions. Try again.") } } }
    fun sendChat(message: String, crop: String? = null, quantity: Double? = null, location: Coordinates? = null) {
        if (message.isBlank() || _state.value.chatSending) return
        viewModelScope.launch {
            val current = _state.value
            _state.value = current.copy(chatSending = true, error = null, chatMessages = (current.chatMessages + ChatMessage(message.trim(), true)).takeLast(100))
            val request = ChatRequest(
                session_id = current.chatSessionId,
                message = message.trim(),
                context = ChatContext(location?.lat, location?.lng, crop, quantity),
                client = ChatClient(),
            )
            runCatching { repository.chat(request) }
                .onSuccess { response ->
                    val latest = _state.value
                    _state.value = latest.copy(chatSending = false, chatSessionId = response.session_id, chatMessages = (latest.chatMessages + ChatMessage(response.reply.text, false, response.reply.speak_text)).takeLast(100))
                }
                .onFailure { _state.value = _state.value.copy(chatSending = false, error = "Saathi could not respond. Check your connection.", offline = true) }
        }
    }
    fun clearChat() { _state.value = _state.value.copy(chatMessages = emptyList(), chatSessionId = null, error = null) }
}
