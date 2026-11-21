package com.fairfarm.data

import com.fairfarm.BuildConfig
import kotlinx.serialization.json.Json
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import okhttp3.MediaType.Companion.toMediaType
import java.util.concurrent.TimeUnit

object ApiFactory {
    private val json = Json { ignoreUnknownKeys = true }
    private val retryGet = object : okhttp3.Interceptor {
        override fun intercept(chain: okhttp3.Interceptor.Chain): okhttp3.Response {
            var response = chain.proceed(chain.request())
            if (chain.request().method == "GET" && response.code >= 500) {
                response.close()
                Thread.sleep(200)
                response = chain.proceed(chain.request())
            }
            return response
        }
    }
    val api: FairFarmApi = Retrofit.Builder()
        .baseUrl(BuildConfig.BASE_URL)
        .client(OkHttpClient.Builder().connectTimeout(10, TimeUnit.SECONDS).readTimeout(10, TimeUnit.SECONDS).writeTimeout(10, TimeUnit.SECONDS).addInterceptor(retryGet).build())
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build().create(FairFarmApi::class.java)
}
