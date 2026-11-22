package com.fairfarm.domain

import android.content.Context
import com.fairfarm.data.AdminSettings
import com.fairfarm.data.ApiFactory
import com.fairfarm.data.BacktestResult
import com.fairfarm.data.ChatContext
import com.fairfarm.data.ChatRequest
import com.fairfarm.data.ChatResult
import com.fairfarm.data.Coordinates
import com.fairfarm.data.Crop
import com.fairfarm.data.CropProfit
import com.fairfarm.data.LoginRequest
import com.fairfarm.data.Mandi
import com.fairfarm.data.RecommendRequest
import com.fairfarm.data.RecommendResult
import com.fairfarm.data.RegionPrice
import com.fairfarm.data.SeasonalityResult

class FairFarmRepository(context: Context) {
    private val api = ApiFactory.create(context)
    private val prefs = context.getSharedPreferences("fairfarm", Context.MODE_PRIVATE)

    fun hasToken(): Boolean = !prefs.getString("token", null).isNullOrBlank()

    fun logout() {
        prefs.edit().remove("token").apply()
    }

    suspend fun login(email: String, password: String) {
        val result = api.login(LoginRequest(email, password))
        prefs.edit().putString("token", result.data.access_token).apply()
    }

    suspend fun crops(): List<Crop> = api.crops().data

    suspend fun recommend(cropId: String, quantity: Double, lat: Double, lng: Double): RecommendResult =
        api.recommend(
            RecommendRequest(cropId, quantity, Coordinates(lat, lng), 300.0)
        ).data

    suspend fun mandis(cropId: String, lat: Double, lng: Double): List<Mandi> =
        api.mandis(cropId, lat, lng, 300.0).data

    suspend fun seasonality(cropId: String): SeasonalityResult =
        api.seasonality(cropId).data

    suspend fun cropProfit(water: String): List<CropProfit> =
        api.cropProfit(water).data

    suspend fun backtest(cropId: String): BacktestResult =
        api.backtest(cropId).data

    suspend fun regions(cropId: String): List<RegionPrice> =
        api.regions(cropId).data

    suspend fun settings(): AdminSettings = api.getSettings().data

    suspend fun updateSettings(settings: AdminSettings): AdminSettings =
        api.updateSettings(settings).data

    suspend fun chat(
        message: String,
        sessionId: String?,
        lat: Double,
        lng: Double,
        cropId: String,
        quantity: Double
    ): ChatResult = api.chat(
        ChatRequest(
            message = message,
            session_id = sessionId,
            context = ChatContext(lat, lng, cropId, quantity),
            client = com.fairfarm.data.ChatClient()
        )
    ).data
}
