package com.fairfarm.data

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface FairFarmApi {
    @GET("meta") suspend fun meta(): Envelope<Meta>
    @GET("crops") suspend fun crops(): Envelope<List<Crop>>
    @POST("recommend") suspend fun recommend(@Body request: RecommendRequest): Envelope<RecommendResult>
}
