package com.fairfarm.data

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonObject

@Serializable data class Envelope<T>(val data: T, val data_as_of: String, val is_demo: Boolean)
@Serializable data class Coordinates(val lat: Double, val lng: Double)
@Serializable data class Crop(val id: String, val name: Map<String, String>, val unit: String, val perishability: String, val category: String = "vegetable")
@Serializable data class Mandi(val id: String, val name: String, val district: String, val freshness: String, val modal_price_inr: String? = null, val location: Coordinates)
@Serializable data class RecommendRequest(val crop_id: String, val quantity_quintal: Double, val farmer_location: Coordinates, val radius_km: Double)
@Serializable data class RecommendResult(val crop_id: String, val quantity_quintal: Double, val recommendations: List<Recommendation>, val old_mandis: List<Recommendation>, val sell_or_wait: SellWait)
@Serializable data class Recommendation(val mandi: Mandi, val distance_km: String, val costs: Costs, val rank: Int)
@Serializable data class Costs(val total_net_inr: String, val net_per_quintal_inr: String)
@Serializable data class SellWait(val decision: String, val reason: Map<String, String>, val disclaimer: String)
@Serializable data class Meta(val api_version: String, val min_app_version: String, val is_demo: Boolean)
@Serializable data class ChatContext(val lat: Double? = null, val lng: Double? = null, val crop_id: String? = null, val quantity_quintal: Double? = null, val last_recommendation_id: String? = null)
@Serializable data class ChatClient(val platform: String = "android", val app_version: String = "1.0.0", val device_id: String? = null)
@Serializable data class ChatRequest(val session_id: String? = null, val message: String, val input_mode: String = "text", val ui_language: String = "auto", val context: ChatContext = ChatContext(), val client: ChatClient = ChatClient())
@Serializable data class ChatReply(val text: String, val speak_text: String, val language: String, val script: String)
@Serializable data class ChatMeta(val intent: String, val tools_used: List<String>, val data_as_of: String? = null, val is_demo: Boolean, val confidence: Double, val grounded: Boolean, val fallback_used: Boolean, val request_id: String)
@Serializable data class ChatCard(val type: String, val data: JsonObject)
@Serializable data class ChatResponse(val session_id: String, val reply: ChatReply, val cards: List<ChatCard>, val chips: List<String>, val meta: ChatMeta)
@Serializable data class ChatStarter(val label: String, val message: String)
@Serializable data class NextCropRequest(val category: String, val crop_history: List<String>, val water_availability: String)
@Serializable data class NextCrop(val crop: CropProfit, val reason: String, val reasons: List<String>)
@Serializable data class CropProfit(val crop_id: String, val risk_adjusted_midpoint_inr_per_acre: String, val water_fit: String)
@Serializable data class ChatFeedbackRequest(val request_id: String, val rating: String, val reason_code: String? = null)
@Serializable data class ChatFeedbackResponse(val accepted: Boolean)
