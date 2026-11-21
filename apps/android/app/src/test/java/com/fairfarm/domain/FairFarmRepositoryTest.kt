package com.fairfarm.domain

import com.fairfarm.data.*
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

private class FakeApi : FairFarmApi {
    override suspend fun meta() = Envelope(Meta("1.0.0", "1.0.0", true), "now", true)
    override suspend fun crops() = Envelope(listOf(Crop("onion", mapOf("en" to "Onion"), "quintal", "high")), "now", true)
    override suspend fun recommend(request: RecommendRequest) = Envelope(RecommendResult(request.crop_id, request.quantity_quintal, emptyList(), emptyList(), SellWait("UNSURE", emptyMap(), "Guidance, not a guarantee")), "now", true)
}

class FairFarmRepositoryTest {
    @Test fun mapsCropsFromApi() = runTest { assertEquals("onion", FairFarmRepository(FakeApi()).crops().single().id) }
}
