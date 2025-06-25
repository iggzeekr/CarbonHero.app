package com.example.carbonhero

import com.example.carbonhero.utils.CarbonCalculatorUtils
import org.junit.Test
import org.junit.Assert.*

/**
 * Example local unit test, which will execute on the development machine (host).
 *
 * See [testing documentation](http://d.android.com/tools/testing).
 */
class ExampleUnitTest {
    @Test
    fun addition_isCorrect() {
        assertEquals(4, 2 + 2)
    }

    @Test
    fun testCarbonCalculatorDietFootprint() {
        // Test vegan diet
        val veganFootprint = CarbonCalculatorUtils.calculateDietFootprint("vegan")
        assertEquals(1.5, veganFootprint, 0.01)

        // Test vegetarian diet
        val vegetarianFootprint = CarbonCalculatorUtils.calculateDietFootprint("vegetarian")
        assertEquals(2.5, vegetarianFootprint, 0.01)

        // Test omnivore diet
        val omnivoreFootprint = CarbonCalculatorUtils.calculateDietFootprint("omnivore")
        assertEquals(4.8, omnivoreFootprint, 0.01)
    }

    @Test
    fun testCarbonCalculatorTransportation() {
        // Test walking
        val walkingFootprint = CarbonCalculatorUtils.calculateTransportationFootprint("walking", null)
        assertEquals(0.0, walkingFootprint, 0.01)

        // Test bicycle
        val bicycleFootprint = CarbonCalculatorUtils.calculateTransportationFootprint("bicycle", null)
        assertEquals(0.0, bicycleFootprint, 0.01)

        // Test gasoline car
        val gasolineFootprint = CarbonCalculatorUtils.calculateTransportationFootprint("car", "gasoline")
        assertEquals(4.2, gasolineFootprint, 0.01)
    }

    @Test
    fun testCarbonCalculatorHousing() {
        // Test natural gas heating with medium efficiency
        val housingFootprint = CarbonCalculatorUtils.calculateHousingFootprint("natural_gas", "medium")
        assertEquals(3.2, housingFootprint, 0.01)

        // Test electricity heating with high efficiency  
        val electricFootprint = CarbonCalculatorUtils.calculateHousingFootprint("electricity", "high")
        assertEquals(2.0, electricFootprint, 0.01)
    }

    @Test
    fun testCarbonCalculatorValidation() {
        // Test valid input
        val validResult = CarbonCalculatorUtils.validateUserInput(
            dietType = "vegan",
            transportMode = "bicycle",
            heatingSource = "electricity",
            energyEfficiency = "high"
        )
        assertTrue(validResult.isValid)

        // Test invalid input (null values)
        val invalidResult = CarbonCalculatorUtils.validateUserInput(
            dietType = null,
            transportMode = "bicycle",
            heatingSource = "electricity",
            energyEfficiency = "high"
        )
        assertFalse(invalidResult.isValid)
    }

    @Test
    fun testFootprintLevel() {
        // Test excellent level
        assertEquals("Excellent", CarbonCalculatorUtils.getFootprintLevel(4.0))

        // Test good level
        assertEquals("Good", CarbonCalculatorUtils.getFootprintLevel(7.0))

        // Test average level
        assertEquals("Average", CarbonCalculatorUtils.getFootprintLevel(10.0))

        // Test above average level
        assertEquals("Above Average", CarbonCalculatorUtils.getFootprintLevel(15.0))

        // Test high level
        assertEquals("High", CarbonCalculatorUtils.getFootprintLevel(20.0))
    }
}