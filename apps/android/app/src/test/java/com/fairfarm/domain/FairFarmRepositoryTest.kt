package com.fairfarm.domain

import com.fairfarm.data.*
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

private class FakeApi : FairFarmApi {
    override suspend fun meta() = Envelope(Meta("1.0.0", "1.0.0", true), "now", true)
    override suspend fun crops() = Envelope(listOf(Crop("onion", mapOf("en" to "Onion"), "quintal", "high")), "now", true)
    override suspend fun recommend(request: RecommendRequest) = Envelope(RecommendResult(request.crop_id, request.quantity_quintal, emptyList(), emptyList(), SellWait("UNSURE", emptyMap(), "Guidance, not a guarantee")), "now", true)
    override suspend fun chat(request: ChatRequest) = Envelope(ChatResponse("session-1", ChatReply("Hello", "Hello", "en", "latin"), emptyList(), emptyList(), ChatMeta("greeting", emptyList(), "now", true, 1.0, true, false, "request-1")), "now", true)
    override suspend fun chatStarters(language: String) = Envelope(emptyList<ChatStarter>(), "now", true)
    override suspend fun chatFeedback(request: ChatFeedbackRequest) = Envelope(ChatFeedbackResponse(true), "now", true)
    override suspend fun nextCrops(request: NextCropRequest) = Envelope(emptyList<NextCrop>(), "now", true)
}

class FairFarmRepositoryTest {
    @Test fun mapsCropsFromApi() = runTest { assertEquals("onion", FairFarmRepository(FakeApi()).crops().single().id) }
    @Test fun mapsSaathiReplyFromApi() = runTest { assertEquals("Hello", FairFarmRepository(FakeApi()).chat(ChatRequest(message = "hello")).reply.text) }
}
