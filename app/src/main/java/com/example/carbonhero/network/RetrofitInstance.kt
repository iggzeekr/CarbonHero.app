package com.example.carbonhero.network

import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.Response
import com.example.carbonhero.model.UserStatsResponse
import com.example.carbonhero.model.UserDataUpdate
import com.example.carbonhero.model.UserData
import com.example.carbonhero.model.LeaderboardResponse
import retrofit2.http.POST
import retrofit2.http.Body

// Recommendation response models
data class RecommendationResponse(
    val status: String,
    val recommendations: List<Recommendation>
)
data class Recommendation(
    val category: String?,
    val message: String?,
    val improvement_potential: Double?,
    val similarity_score: Double?
)

// LeaderboardResponse moved to model package

interface ApiService {
    @GET("user-recommendations/{userId}")
    suspend fun getUserRecommendations(@Path("userId") userId: String): RecommendationResponse

    @GET("user-stats/{userId}")
    suspend fun getUserFootprint(@Path("userId") userId: String): Response<UserStatsResponse>

    @POST("api/user-data/update/{userId}")
    suspend fun updateUserData(
        @Path("userId") userId: String,
        @Body update: UserDataUpdate
    ): Response<Map<String, Any>>

    @POST("api/user-data")
    suspend fun submitUserData(@Body userData: UserData): Response<Map<String, Any>>

    @GET("api/leaderboard")
    suspend fun getLeaderboard(): Response<LeaderboardResponse>

    @POST("api/user-data/initialize/{userId}")
    suspend fun initializeUserData(@Path("userId") userId: String): Response<Map<String, Any>>

    @POST("api/challenges/{userId}/complete/{challengeId}")
    suspend fun completeChallenge(
        @Path("userId") userId: String,
        @Path("challengeId") challengeId: String
    ): Response<Map<String, Any>>
}

object RetrofitInstance {
    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl("http://10.0.2.2:8000/") // Backend artık 8000 portunda
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
} 