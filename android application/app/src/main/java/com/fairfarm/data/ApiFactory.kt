package com.fairfarm.data

import android.content.Context
import com.fairfarm.BuildConfig
import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit

object ApiFactory {
    fun create(context: Context): FairFarmApi {
        val prefs = context.getSharedPreferences("fairfarm", Context.MODE_PRIVATE)
        val json = Json {
            ignoreUnknownKeys = true
            isLenient = true
            encodeDefaults = true
        }
        val logging = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BASIC else HttpLoggingInterceptor.Level.NONE
        }
        val client = OkHttpClient.Builder()
            .addInterceptor { chain ->
                val token = prefs.getString("token", null)
                val request = if (token.isNullOrBlank()) chain.request() else
                    chain.request().newBuilder().header("Authorization", "Bearer $token").build()
                chain.proceed(request)
            }
            .addInterceptor(logging)
            .build()
        val baseUrl = BuildConfig.BASE_URL.trimEnd('/') + "/"
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create(FairFarmApi::class.java)
    }
}
