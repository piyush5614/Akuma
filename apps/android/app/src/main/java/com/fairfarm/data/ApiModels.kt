package com.fairfarm.data

import kotlinx.serialization.Serializable

@Serializable data class Envelope<T>(val data: T, val data_as_of: String, val is_demo: Boolean)
@Serializable data class Coordinates(val lat: Double, val lng: Double)
@Serializable data class Crop(val id: String, val name: Map<String, String>, val unit: String, val perishability: String)
@Serializable data class Mandi(val id: String, val name: String, val district: String, val freshness: String, val modal_price_inr: String? = null, val location: Coordinates)
@Serializable data class RecommendRequest(val crop_id: String, val quantity_quintal: Double, val farmer_location: Coordinates, val radius_km: Double)
@Serializable data class RecommendResult(val crop_id: String, val quantity_quintal: Double, val recommendations: List<Recommendation>, val old_mandis: List<Recommendation>, val sell_or_wait: SellWait)
@Serializable data class Recommendation(val mandi: Mandi, val distance_km: String, val costs: Costs, val rank: Int)
@Serializable data class Costs(val total_net_inr: String, val net_per_quintal_inr: String)
@Serializable data class SellWait(val decision: String, val reason: Map<String, String>, val disclaimer: String)
@Serializable data class Meta(val api_version: String, val min_app_version: String, val is_demo: Boolean)
