package com.example.carbonhero.utils

object CarbonCalculatorUtils {
    
    /**
     * Calculate carbon footprint for diet category
     */
    fun calculateDietFootprint(dietType: String): Double {
        return when (dietType.lowercase()) {
            "vegan" -> 1.5
            "vegetarian" -> 2.5
            "pescatarian" -> 3.2
            "omnivore" -> 4.8
            else -> 3.5 // default moderate value
        }
    }
    
    /**
     * Calculate carbon footprint for transportation
     */
    fun calculateTransportationFootprint(
        transportMode: String, 
        vehicleType: String? = null
    ): Double {
        return when (transportMode.lowercase()) {
            "walking", "bicycle" -> 0.0
            "public_transport" -> 1.2
            "motorcycle" -> 2.8
            "car" -> when (vehicleType?.lowercase()) {
                "electric" -> 1.5
                "hybrid" -> 2.8
                "gasoline" -> 4.2
                "diesel" -> 4.6
                else -> 3.5
            }
            else -> 2.0
        }
    }
    
    /**
     * Calculate carbon footprint for housing
     */
    fun calculateHousingFootprint(
        heatingSource: String,
        energyEfficiency: String
    ): Double {
        val baseFootprint = when (heatingSource.lowercase()) {
            "renewable" -> 0.8
            "electricity" -> 2.5
            "natural_gas" -> 3.2
            "oil" -> 4.8
            else -> 3.0
        }
        
        val efficiencyMultiplier = when (energyEfficiency.lowercase()) {
            "very_high" -> 0.6
            "high" -> 0.8
            "medium" -> 1.0
            "low" -> 1.3
            else -> 1.0
        }
        
        return baseFootprint * efficiencyMultiplier
    }
    
    /**
     * Calculate lifestyle carbon footprint
     */
    fun calculateLifestyleFootprint(
        screenTime: String,
        internetUsage: String
    ): Double {
        val screenFootprint = when (screenTime.lowercase()) {
            "low" -> 0.5
            "moderate" -> 1.2
            "high" -> 2.1
            "very_high" -> 3.2
            else -> 1.5
        }
        
        val internetFootprint = when (internetUsage.lowercase()) {
            "low" -> 0.3
            "moderate" -> 0.8
            "high" -> 1.5
            "very_high" -> 2.3
            else -> 1.0
        }
        
        return screenFootprint + internetFootprint
    }
    
    /**
     * Calculate waste carbon footprint
     */
    fun calculateWasteFootprint(
        recycling: String,
        trashBagSize: String
    ): Double {
        val baseWaste = when (trashBagSize.lowercase()) {
            "small" -> 1.0
            "medium" -> 2.0
            "large" -> 3.5
            else -> 2.0
        }
        
        val recyclingMultiplier = when (recycling.lowercase()) {
            "always" -> 0.3
            "often" -> 0.5
            "sometimes" -> 0.8
            "never" -> 1.0
            else -> 0.7
        }
        
        return baseWaste * recyclingMultiplier
    }
    
    /**
     * Calculate total carbon footprint
     */
    fun calculateTotalFootprint(
        dietType: String,
        transportMode: String,
        vehicleType: String? = null,
        heatingSource: String,
        energyEfficiency: String,
        screenTime: String,
        internetUsage: String,
        recycling: String,
        trashBagSize: String
    ): Map<String, Double> {
        
        val dietFootprint = calculateDietFootprint(dietType)
        val transportFootprint = calculateTransportationFootprint(transportMode, vehicleType)
        val housingFootprint = calculateHousingFootprint(heatingSource, energyEfficiency)
        val lifestyleFootprint = calculateLifestyleFootprint(screenTime, internetUsage)
        val wasteFootprint = calculateWasteFootprint(recycling, trashBagSize)
        
        val total = dietFootprint + transportFootprint + housingFootprint + 
                   lifestyleFootprint + wasteFootprint
        
        return mapOf(
            "diet" to dietFootprint,
            "transportation" to transportFootprint,
            "housing" to housingFootprint,
            "lifestyle" to lifestyleFootprint,
            "waste" to wasteFootprint,
            "total" to total
        )
    }
    
    /**
     * Validate user input data
     */
    fun validateUserInput(
        dietType: String?,
        transportMode: String?,
        heatingSource: String?,
        energyEfficiency: String?
    ): ValidationResult {
        val errors = mutableListOf<String>()
        
        if (dietType.isNullOrBlank()) {
            errors.add("Diet type is required")
        }
        
        if (transportMode.isNullOrBlank()) {
            errors.add("Transportation mode is required")
        }
        
        if (heatingSource.isNullOrBlank()) {
            errors.add("Heating source is required")
        }
        
        if (energyEfficiency.isNullOrBlank()) {
            errors.add("Energy efficiency is required")
        }
        
        return ValidationResult(
            isValid = errors.isEmpty(),
            errors = errors
        )
    }
    
    /**
     * Get carbon footprint level description
     */
    fun getFootprintLevel(totalFootprint: Double): String {
        return when {
            totalFootprint <= 5.0 -> "Excellent"
            totalFootprint <= 8.0 -> "Good"
            totalFootprint <= 12.0 -> "Average"
            totalFootprint <= 16.0 -> "Above Average"
            else -> "High"
        }
    }
}

data class ValidationResult(
    val isValid: Boolean,
    val errors: List<String>
) 