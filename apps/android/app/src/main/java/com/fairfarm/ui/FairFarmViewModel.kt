package com.fairfarm.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fairfarm.data.*
import com.fairfarm.domain.FairFarmRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class FarmerState(val loading: Boolean = false, val crops: List<Crop> = emptyList(), val result: RecommendResult? = null, val error: String? = null, val offline: Boolean = false)

class FairFarmViewModel(private val repository: FairFarmRepository) : ViewModel() {
    private val _state = MutableStateFlow(FarmerState())
    val state: StateFlow<FarmerState> = _state
    fun loadCrops() { viewModelScope.launch { _state.value = _state.value.copy(loading = true); runCatching { repository.crops() }.onSuccess { _state.value = _state.value.copy(loading = false, crops = it) }.onFailure { _state.value = _state.value.copy(loading = false, error = "Could not load crops. Check your connection.", offline = true) } } }
    fun recommend(crop: String, quantity: Double, location: Coordinates) { viewModelScope.launch { _state.value = _state.value.copy(loading = true, error = null); runCatching { repository.recommend(crop, quantity, location) }.onSuccess { _state.value = _state.value.copy(loading = false, result = it) }.onFailure { _state.value = _state.value.copy(loading = false, error = "Could not calculate returns. Try again.", offline = true) } } }
}
