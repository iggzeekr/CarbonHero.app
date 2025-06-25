package com.example.carbonhero.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.carbonhero.repository.CarbonHeroRepository
import com.example.carbonhero.utils.CarbonCalculatorUtils
import com.example.carbonhero.model.TahminSonucu
import com.example.carbonhero.model.UserTestResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ProfileUiState(
    val isLoading: Boolean = false,
    val predictions: TahminSonucu? = null,
    val errorMessage: String? = null,
    val isFormValid: Boolean = false,
    val dietType: String = "",
    val transportMode: String = "",
    val heatingSource: String = "",
    val energyEfficiency: String = ""
)

class ProfileViewModel @Inject constructor(
    private val repository: CarbonHeroRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    private val _carbonFootprint = MutableStateFlow<Map<String, Double>?>(null)
    val carbonFootprint: StateFlow<Map<String, Double>?> = _carbonFootprint.asStateFlow()

    /**
     * Get predictions for user test result
     */
    fun getPredictions(userId: String, userTestResult: UserTestResult) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)

            repository.getPredictions(userTestResult)
                .onSuccess { predictions ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        predictions = predictions,
                        errorMessage = null
                    )
                    // Cache the predictions
                    repository.cachePredictions(userId, predictions)
                }
                .onFailure { error ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = error.message ?: "Failed to get predictions"
                    )
                }
        }
    }

    /**
     * Save user test result
     */
    fun saveUserTestResult(userId: String, userTestResult: UserTestResult) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            repository.saveUserTestResult(userId, userTestResult)
                .onSuccess {
                    _uiState.value = _uiState.value.copy(isLoading = false)
                    // Get predictions after saving
                    getPredictions(userId, userTestResult)
                }
                .onFailure { error ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = error.message ?: "Failed to save test result"
                    )
                }
        }
    }

    /**
     * Calculate carbon footprint based on form inputs
     */
    fun calculateCarbonFootprint(
        dietType: String,
        transportMode: String,
        vehicleType: String? = null,
        heatingSource: String,
        energyEfficiency: String,
        screenTime: String = "moderate",
        internetUsage: String = "moderate",
        recycling: String = "sometimes",
        trashBagSize: String = "medium"
    ) {
        viewModelScope.launch {
            try {
                val result = CarbonCalculatorUtils.calculateTotalFootprint(
                    dietType = dietType,
                    transportMode = transportMode,
                    vehicleType = vehicleType,
                    heatingSource = heatingSource,
                    energyEfficiency = energyEfficiency,
                    screenTime = screenTime,
                    internetUsage = internetUsage,
                    recycling = recycling,
                    trashBagSize = trashBagSize
                )
                
                _carbonFootprint.value = result
                _uiState.value = _uiState.value.copy(errorMessage = null)
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "Failed to calculate carbon footprint: ${e.message}"
                )
            }
        }
    }

    /**
     * Update form field and validate
     */
    fun updateFormField(field: String, value: String) {
        val currentState = _uiState.value
        
        val updatedState = when (field) {
            "diet_type" -> currentState.copy(dietType = value)
            "transport_mode" -> currentState.copy(transportMode = value)
            "heating_source" -> currentState.copy(heatingSource = value)
            "energy_efficiency" -> currentState.copy(energyEfficiency = value)
            else -> currentState
        }
        
        _uiState.value = updatedState.copy(
            isFormValid = validateForm(updatedState)
        )
    }

    /**
     * Validate form inputs
     */
    private fun validateForm(state: ProfileUiState): Boolean {
        val validation = CarbonCalculatorUtils.validateUserInput(
            dietType = state.dietType.takeIf { it.isNotBlank() },
            transportMode = state.transportMode.takeIf { it.isNotBlank() },
            heatingSource = state.heatingSource.takeIf { it.isNotBlank() },
            energyEfficiency = state.energyEfficiency.takeIf { it.isNotBlank() }
        )
        
        return validation.isValid
    }

    /**
     * Clear error message
     */
    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }

    /**
     * Reset form
     */
    fun resetForm() {
        _uiState.value = ProfileUiState()
        _carbonFootprint.value = null
    }

    /**
     * Get carbon footprint level description
     */
    fun getFootprintLevelDescription(): String? {
        return _carbonFootprint.value?.get("total")?.let { total ->
            CarbonCalculatorUtils.getFootprintLevel(total)
        }
    }
} 