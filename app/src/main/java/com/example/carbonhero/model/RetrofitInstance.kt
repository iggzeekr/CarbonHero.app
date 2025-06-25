package com.example.carbonhero.model

import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

data class UserDataUpdate(
    val field: String,
    val value: String
)

interface CarbonHeroApi {
    @GET("user-stats/{userId}")
    suspend fun getUserFootprint(@Path("userId") userId: String): Response<UserStatsResponse>

    @POST("api/user-data/update/{userId}")
    suspend fun updateUserData(
        @Path("userId") userId: String,
        @Body update: UserDataUpdate
    ): Response<Map<String, Any>>

    @POST("api/user-data")
    suspend fun submitUserData(@Body userData: UserData): Response<Map<String, Any>>
}

object RetrofitInstance {
    private const val BASE_URL = "http://10.0.2.2:8000/" // Android emulator için localhost

    private val retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    val api: CarbonHeroApi by lazy {
        retrofit.create(CarbonHeroApi::class.java)
    }
} 