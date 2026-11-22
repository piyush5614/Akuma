package com.fairfarm.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.fairfarm.data.AdminSettings
import com.fairfarm.data.Crop
import com.fairfarm.data.CropProfit
import com.fairfarm.data.Mandi
import com.fairfarm.data.RecommendResult
import com.fairfarm.data.RegionPrice
import com.fairfarm.data.SeasonalityResult
import com.fairfarm.data.ChatResult
import com.fairfarm.domain.FairFarmRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class FairFarmState(
    val loading: Boolean = false,
    val error: String? = null,
    val crops: List<Crop> = emptyList(),
    val recommend: RecommendResult? = null,
    val mandis: List<Mandi> = emptyList(),
    val seasonality: SeasonalityResult? = null,
    val cropProfits: List<CropProfit> = emptyList(),
    val regions: List<RegionPrice> = emptyList(),
    val settings: AdminSettings? = null,
    val chatMessages: List<ChatResult> = emptyList(),
    val chatSessionId: String? = null
)

class FairFarmViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = FairFarmRepository(application)
    private val _state = MutableStateFlow(FairFarmState())
    val state: StateFlow<FairFarmState> = _state

    fun isLoggedIn(): Boolean = repository.hasToken()

    fun login(email: String, password: String, onSuccess: () -> Unit) {
        runLoading {
            repository.login(email, password)
            onSuccess()
        }
    }

    fun logout() = repository.logout()

    fun loadCrops() = runLoading {
        _state.update { it.copy(crops = repository.crops()) }
    }

    fun recommend(cropId: String, quantity: Double, lat: Double = 18.52, lng: Double = 73.86) =
        runLoading {
            _state.update {
                it.copy(recommend = repository.recommend(cropId, quantity, lat, lng))
            }
        }

    fun loadMandis(cropId: String, lat: Double = 18.52, lng: Double = 73.86) =
        runLoading {
            _state.update { it.copy(mandis = repository.mandis(cropId, lat, lng)) }
        }

    fun loadInsights(cropId: String, water: String = "medium") =
        runLoading {
            val seasonality = repository.seasonality(cropId)
            val profits = repository.cropProfit(water)
            _state.update { it.copy(seasonality = seasonality, cropProfits = profits) }
        }

    fun loadRegions(cropId: String) =
        runLoading {
            _state.update { it.copy(regions = repository.regions(cropId)) }
        }

    fun loadSettings() =
        runLoading {
            _state.update { it.copy(settings = repository.settings()) }
        }

    fun saveSettings(settings: AdminSettings, onSaved: () -> Unit = {}) =
        runLoading {
            val saved = repository.updateSettings(settings)
            _state.update { it.copy(settings = saved) }
            onSaved()
        }

    fun chat(message: String, cropId: String = "onion", quantity: Double = 10.0) =
        runLoading {
            val result = repository.chat(
                message,
                _state.value.chatSessionId,
                18.52,
                73.86,
                cropId,
                quantity
            )
            _state.update {
                it.copy(
                    chatMessages = it.chatMessages + result,
                    chatSessionId = result.session_id
                )
            }
        }

    fun clearChat() {
        _state.update { it.copy(chatMessages = emptyList(), chatSessionId = null) }
    }

    fun clearError() {
        _state.update { it.copy(error = null) }
    }

    private fun runLoading(block: suspend () -> Unit) {
        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null) }
            try {
                block()
            } catch (error: Exception) {
                _state.update { it.copy(error = error.message ?: "Unable to load data") }
            } finally {
                _state.update { it.copy(loading = false) }
            }
        }
    }
}
