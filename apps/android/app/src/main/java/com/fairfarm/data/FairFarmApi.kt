package com.fairfarm.data

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface FairFarmApi {
    @GET("meta") suspend fun meta(): Envelope<Meta>
    @GET("crops") suspend fun crops(): Envelope<List<Crop>>
    @POST("recommend") suspend fun recommend(@Body request: RecommendRequest): Envelope<RecommendResult>
    @POST("chat") suspend fun chat(@Body request: ChatRequest): Envelope<ChatResponse>
    @GET("chat/starters") suspend fun chatStarters(@retrofit2.http.Query("lang") language: String): Envelope<List<ChatStarter>>
    @POST("chat/feedback") suspend fun chatFeedback(@Body request: ChatFeedbackRequest): Envelope<ChatFeedbackResponse>
    @POST("insights/next-crops") suspend fun nextCrops(@Body request: NextCropRequest): Envelope<List<NextCrop>>
}
