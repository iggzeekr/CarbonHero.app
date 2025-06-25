package com.example.carbonhero.utils

import com.google.common.truth.Truth.assertThat
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.JUnit4

@RunWith(JUnit4::class)
class CarbonCalculatorUtilsTest {

    // ============ DIET FOOTPRINT TESTS ============
    
    @Test
    fun `calculateDietFootprint with vegan diet returns lowest footprint`() {
        // Given
        val dietType = "vegan"
        
        // When
        val result = CarbonCalculatorUtils.calculateDietFootprint(dietType)
        
        // Then
        assertThat(result).isEqualTo(1.5)
    }
    
    @Test
    fun `calculateDietFootprint with vegetarian diet returns expected value`() {
        // Given
        val dietType = "vegetarian"
        
        // When
        val result = CarbonCalculatorUtils.calculateDietFootprint(dietType)
        
        // Then
        assertThat(result).isEqualTo(2.5)
    }
    
    @Test
    fun `calculateDietFootprint with omnivore diet returns highest footprint`() {
        // Given
        val dietType = "omnivore"
        
        // When
        val result = CarbonCalculatorUtils.calculateDietFootprint(dietType)
        
        // Then
        assertThat(result).isEqualTo(4.8)
    }
    
    @Test
    fun `calculateDietFootprint with case insensitive input works correctly`() {
        // Given
        val dietTypes = listOf("VEGAN", "Vegetarian", "OmNiVoRe")
        val expected = listOf(1.5, 2.5, 4.8)
        
        // When & Then
        dietTypes.forEachIndexed { index, dietType ->
            val result = CarbonCalculatorUtils.calculateDietFootprint(dietType)
            assertThat(result).isEqualTo(expected[index])
        }
    }
    
    @Test
    fun `calculateDietFootprint with invalid diet type returns default value`() {
        // Given
        val invalidDietType = "invalid_diet"
        
        // When
        val result = CarbonCalculatorUtils.calculateDietFootprint(invalidDietType)
        
        // Then
        assertThat(result).isEqualTo(3.5)
    }

    // ============ TRANSPORTATION FOOTPRINT TESTS ============
    
    @Test
    fun `calculateTransportationFootprint with walking returns zero`() {
        // Given
        val transportMode = "walking"
        
        // When
        val result = CarbonCalculatorUtils.calculateTransportationFootprint(transportMode)
        
        // Then
        assertThat(result).isEqualTo(0.0)
    }
    
    @Test
    fun `calculateTransportationFootprint with electric car returns lowest car footprint`() {
        // Given
        val transportMode = "car"
        val vehicleType = "electric"
        
        // When
        val result = CarbonCalculatorUtils.calculateTransportationFootprint(transportMode, vehicleType)
        
        // Then
        assertThat(result).isEqualTo(1.5)
    }
    
    @Test
    fun `calculateTransportationFootprint with diesel car returns highest car footprint`() {
        // Given
        val transportMode = "car"
        val vehicleType = "diesel"
        
        // When
        val result = CarbonCalculatorUtils.calculateTransportationFootprint(transportMode, vehicleType)
        
        // Then
        assertThat(result).isEqualTo(4.6)
    }

    // ============ VALIDATION TESTS ============
    
    @Test
    fun `validateUserInput with all valid inputs returns valid result`() {
        // Given
        val dietType = "vegan"
        val transportMode = "bicycle"
        val heatingSource = "renewable"
        val energyEfficiency = "high"
        
        // When
        val result = CarbonCalculatorUtils.validateUserInput(
            dietType, transportMode, heatingSource, energyEfficiency
        )
        
        // Then
        assertThat(result.isValid).isTrue()
        assertThat(result.errors).isEmpty()
    }
    
    @Test
    fun `validateUserInput with null inputs returns invalid result with errors`() {
        // Given
        val dietType: String? = null
        val transportMode: String? = null
        val heatingSource: String? = null
        val energyEfficiency: String? = null
        
        // When
        val result = CarbonCalculatorUtils.validateUserInput(
            dietType, transportMode, heatingSource, energyEfficiency
        )
        
        // Then
        assertThat(result.isValid).isFalse()
        assertThat(result.errors).hasSize(4)
        assertThat(result.errors).contains("Diet type is required")
        assertThat(result.errors).contains("Transportation mode is required")
        assertThat(result.errors).contains("Heating source is required")
        assertThat(result.errors).contains("Energy efficiency is required")
    }

    // ============ FOOTPRINT LEVEL TESTS ============
    
    @Test
    fun `getFootprintLevel returns correct level for different footprint values`() {
        // Test cases: (footprint, expectedLevel)
        val testCases = listOf(
            3.0 to "Excellent",
            7.5 to "Good", 
            10.0 to "Average",
            14.0 to "Above Average",
            20.0 to "High"
        )
        
        // When & Then
        testCases.forEach { (footprint, expectedLevel) ->
            val result = CarbonCalculatorUtils.getFootprintLevel(footprint)
            assertThat(result).isEqualTo(expectedLevel)
        }
    }
}
