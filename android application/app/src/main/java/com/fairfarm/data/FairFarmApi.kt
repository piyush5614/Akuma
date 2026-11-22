package com.fairfarm.data

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Query

@Serializable
data class Envelope<T>(
    val data: T,
    val data_as_of: String,
    val is_demo: Boolean
)

@Serializable
data class Crop(
    val id: String,
    val name: Map<String, String>,
    val category: String,
    val unit: String,
    val perishability: String
)

@Serializable
data class Coordinates(val lat: Double, val lng: Double)

@Serializable
data class Mandi(
    val id: String,
    val name: String,
    val district: String,
    val state: String = "Maharashtra",
    val location: Coordinates,
    val freshness: String,
    val latest_report_date: String? = null,
    val modal_price_inr: String? = null
)

@Serializable
data class Costs(
    val road_km: String? = null,
    val transport_inr: String? = null,
    val fee_inr: String? = null,
    val shrinkage_inr: String? = null,
    val net_per_quintal_inr: String,
    val total_net_inr: String
)

@Serializable
data class Recommendation(
    val mandi: Mandi,
    val distance_km: String,
    val costs: Costs,
    val rank: Int
)

@Serializable
data class LocalizedText(
    val en: String,
    val mr: String,
    val hi: String
)

@Serializable
data class SellWait(
    val decision: String,
    val reason_codes: List<String>,
    val reason: LocalizedText,
    val disclaimer: String
)

@Serializable
data class RecommendResult(
    val crop_id: String,
    val quantity_quintal: String,
    val recommendations: List<Recommendation>,
    val old_mandis: List<Recommendation>,
    val sell_or_wait: SellWait
)

@Serializable
data class RecommendRequest(
    val crop_id: String,
    val quantity_quintal: Double,
    val farmer_location: Coordinates,
    val radius_km: Double = 300.0
)

@Serializable
data class LoginRequest(val email: String, val password: String)

@Serializable
data class LoginResult(val access_token: String, val expires_in_seconds: Int)

@Serializable
data class SeasonalityMonth(
    val month: Int,
    val price_index: String,
    val median_modal_price_inr: String
)

@Serializable
data class SeasonalityResult(
    val crop_id: String,
    val months: List<SeasonalityMonth>,
    val best_months: List<Int>,
    val worst_months: List<Int>
)

@Serializable
data class CropProfit(
    val crop_id: String,
    val price_range_inr_per_quintal: List<String>,
    val yield_range_quintal_per_acre: List<String>,
    val cost_inr_per_acre: String,
    val risk_adjusted_midpoint_inr_per_acre: String,
    val water_fit: String,
    val herd_warning: Boolean,
    val source: String
)

@Serializable
data class BacktestResult(
    val crop_id: String,
    val window_days: Int,
    val rule_hit_rate: String,
    val baseline_hit_rate: String,
    val sample_count: Int,
    val measured_only: Boolean
)

@Serializable
data class RegionPrice(
    val region_id: String,
    val name: String,
    val location: Coordinates,
    val average_modal_price_inr: String? = null,
    val mandi_count: Int,
    val freshness: String
)

@Serializable
data class AdminSettings(
    val road_factor: String,
    val transport_rate_per_quintal_km: String,
    val fee_pct: String,
    val shrinkage_pct_by_crop: Map<String, String>
)

@Serializable
data class ChatRequest(
    val message: String,
    val session_id: String? = null,
    val ui_language: String = "auto",
    val context: ChatContext,
    val client: ChatClient
)

@Serializable
data class ChatContext(
    val lat: Double,
    val lng: Double,
    val crop_id: String,
    val quantity_quintal: Double
)

@Serializable
data class ChatClient(
    val platform: String = "android",
    val app_version: String = "1.0.0"
)

@Serializable
data class ChatReply(
    val text: String,
    val speak_text: String,
    val language: String,
    val script: String
)

@Serializable
data class ChatMeta(
    val intent: String,
    val tools_used: List<String>,
    val grounded: Boolean,
    val fallback_used: Boolean,
    val request_id: String
)

@Serializable
data class ChatResult(
    val session_id: String,
    val reply: ChatReply,
    val cards: List<JsonElement>,
    val chips: List<String>,
    val meta: ChatMeta
)

interface FairFarmApi {
    @GET("crops")
    suspend fun crops(): Envelope<List<Crop>>

    @POST("recommend")
    suspend fun recommend(@Body request: RecommendRequest): Envelope<RecommendResult>

    @GET("mandis")
    suspend fun mandis(
        @Query("crop_id") cropId: String,
        @Query("lat") lat: Double,
        @Query("lng") lng: Double,
        @Query("radius_km") radiusKm: Double = 300.0
    ): Envelope<List<Mandi>>

    @GET("insights/seasonality")
    suspend fun seasonality(@Query("crop_id") cropId: String): Envelope<SeasonalityResult>

    @GET("insights/crop-profit")
    suspend fun cropProfit(@Query("water_availability") water: String): Envelope<List<CropProfit>>

    @GET("insights/backtest")
    suspend fun backtest(@Query("crop_id") cropId: String): Envelope<BacktestResult>

    @GET("regions/prices")
    suspend fun regions(@Query("crop_id") cropId: String): Envelope<List<RegionPrice>>

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Envelope<LoginResult>

    @GET("admin/settings")
    suspend fun getSettings(): Envelope<AdminSettings>

    @PUT("admin/settings")
    suspend fun updateSettings(@Body settings: AdminSettings): Envelope<AdminSettings>

    @POST("chat")
    suspend fun chat(@Body request: ChatRequest): Envelope<ChatResult>
}
