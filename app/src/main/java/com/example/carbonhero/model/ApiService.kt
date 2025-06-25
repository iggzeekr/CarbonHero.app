package com.example.carbonhero.model

import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.Response

// Recommendation and collaborative challenge models

data class ChallengeRecommendation(
    val challenge: String,
    val score: Int
)

data class CollaborativeChallenge(
    val challenge: String,
    val users: List<String>,
    val score: Int
)

data class TahminSonucu(
    val sonuc: String,
    val recommendations: List<ChallengeRecommendation>,
    val collaborative_challenges: List<CollaborativeChallenge>
)

// Leaderboard models
data class LeaderboardUser(
    val userId: String,
    val username: String,
    val points: Int,
    val carbon_footprint: Any?, // Can be Double or Object
    val rank: Int
) {
    // Helper function to get carbon footprint as double
    fun getCarbonFootprintValue(): Double {
        return when (carbon_footprint) {
            is Double -> carbon_footprint
            is Number -> carbon_footprint.toDouble()
            is Map<*, *> -> {
                (carbon_footprint["total_footprint"] as? Number)?.toDouble() ?: 0.0
            }
            else -> 0.0
        }
    }
}

data class LeaderboardResponse(
    val status: String,
    val leaderboard: List<LeaderboardUser>
)

interface ApiService {
    @POST("tahmin")
    suspend fun tahminYap(@Body veri: UserTestResult): Response<TahminSonucu>
} 