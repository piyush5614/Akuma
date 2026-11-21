package com.fairfarm.domain

import com.fairfarm.data.*

class FairFarmRepository(private val api: FairFarmApi) {
    suspend fun crops(): List<Crop> = api.crops().data
    suspend fun recommend(cropId: String, quantity: Double, location: Coordinates): RecommendResult =
        api.recommend(RecommendRequest(cropId, quantity, location, 300.0)).data
}
