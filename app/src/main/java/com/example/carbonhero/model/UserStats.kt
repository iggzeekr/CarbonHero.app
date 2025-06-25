package com.example.carbonhero.model

data class UserStats(
    val current_footprint: Double,
    val average_footprint: Double,
    val trend: Double,
    val trend_percentage: Double,
    val improvement_percentage: Double,
    val challenges: ChallengesStats,
    val recent_footprints: List<Footprint>,
    val breakdown: Map<String, Double>? = null // Kategori bazlı değerler
)

data class ChallengesStats(
    val completed: Int,
    val in_progress: Int,
    val total_carbon_saved: Double
)

data class Footprint(
    val userId: String?,
    val timestamp: String?,
    val total_footprint: Double?,
    val transportation: Double?,
    val electricity: Double?,
    val heating: Double?,
    val food: Double?,
    val waste: Double?
)

data class UserStatsResponse(
    val current_footprint: Double,
    val average_footprint: Double,
    val trend: Double,
    val trend_percentage: Double,
    val improvement_percentage: Double,
    val challenges: ChallengesStats,
    val recent_footprints: List<Footprint>,
    val breakdown: Map<String, Double>?,
    val recommendations: List<String>?,
    val user_data: Map<String, Any?>?,
    val total_score: Int = 0
) 