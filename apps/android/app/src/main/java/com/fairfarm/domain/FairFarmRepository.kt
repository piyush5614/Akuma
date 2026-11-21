package com.fairfarm.domain

import com.fairfarm.data.*

class FairFarmRepository(private val api: FairFarmApi) {
    suspend fun crops(): List<Crop> = api.crops().data
    suspend fun recommend(cropId: String, quantity: Double, location: Coordinates): RecommendResult =
        api.recommend(RecommendRequest(cropId, quantity, location, 300.0)).data
    suspend fun nextCrops(category: String, history: List<String>, water: String): List<NextCrop> =
        api.nextCrops(NextCropRequest(category, history, water)).data
    suspend fun chat(request: ChatRequest): ChatResponse = api.chat(request).data
    suspend fun chatStarters(language: String): List<ChatStarter> = api.chatStarters(language).data
    suspend fun chatFeedback(request: ChatFeedbackRequest): ChatFeedbackResponse = api.chatFeedback(request).data
}
