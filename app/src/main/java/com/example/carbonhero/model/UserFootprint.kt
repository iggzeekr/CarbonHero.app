package com.example.carbonhero.model

data class UserFootprint(
    val userId: String,
    val timestamp: Long,
    val transportation: Double,
    val electricity: Double,
    val heating: Double,
    val food: Double,
    val waste: Double,
    val totalFootprint: Double
) 