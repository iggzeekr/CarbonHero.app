package com.example.carbonhero.repository

import com.example.carbonhero.model.ApiService
import com.example.carbonhero.model.TahminSonucu
import com.example.carbonhero.model.UserTestResult
import com.example.carbonhero.model.UserStatsResponse
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CarbonHeroRepository @Inject constructor(
    private val apiService: ApiService,
    private val firestore: FirebaseFirestore
) {
    
    /**
     * Get predictions and recommendations from API
     */
    suspend fun getPredictions(userTestResult: UserTestResult): Result<TahminSonucu> {
        return try {
            val response = apiService.tahminYap(userTestResult)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to get predictions: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Cache user predictions in Firestore
     */
    suspend fun cachePredictions(userId: String, predictions: TahminSonucu): Result<Boolean> {
        return try {
            val data = mapOf(
                "predictions" to predictions,
                "last_updated" to System.currentTimeMillis()
            )
            firestore.collection("user_predictions")
                .document(userId)
                .set(data)
                .await()
            Result.success(true)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get cached predictions from Firestore
     */
    suspend fun getCachedPredictions(userId: String): Result<TahminSonucu?> {
        return try {
            val document = firestore.collection("user_predictions")
                .document(userId)
                .get()
                .await()
            
            if (document.exists()) {
                val predictions = document.get("predictions") as? TahminSonucu
                Result.success(predictions)
            } else {
                Result.success(null)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Check if cached predictions are fresh (less than 1 hour old)
     */
    suspend fun isPredictionsFresh(userId: String): Result<Boolean> {
        return try {
            val document = firestore.collection("user_predictions")
                .document(userId)
                .get()
                .await()
            
            if (document.exists()) {
                val timestamp = document.getLong("last_updated") ?: 0L
                val currentTime = System.currentTimeMillis()
                val isDataFresh = (currentTime - timestamp) < (60 * 60 * 1000) // 1 hour
                Result.success(isDataFresh)
            } else {
                Result.success(false)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Save user test result to Firestore
     */
    suspend fun saveUserTestResult(userId: String, testResult: UserTestResult): Result<Boolean> {
        return try {
            firestore.collection("user_test_results")
                .document(userId)
                .set(testResult)
                .await()
            Result.success(true)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
} 