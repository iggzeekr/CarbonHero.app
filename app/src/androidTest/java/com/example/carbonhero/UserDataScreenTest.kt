package com.example.carbonhero

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.navigation.compose.rememberNavController
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.carbonhero.screens.UserDataScreen
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class UserDataScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testUserDataScreenDisplaysCorrectly() {
        // Test that the user data screen displays all required elements
        composeTestRule.setContent {
            UserDataScreen(navController = rememberNavController())
        }

        // Check if title is displayed
        composeTestRule.onNodeWithText("Tell us about yourself").assertIsDisplayed()
        
        // Check if subtitle is displayed
        composeTestRule.onNodeWithText("Help us calculate your carbon footprint").assertIsDisplayed()
        
        // Check if diet question is displayed
        composeTestRule.onNodeWithText("What is your diet type?").assertIsDisplayed()
        
        // Check if transportation question is displayed
        composeTestRule.onNodeWithText("What is your primary mode of transportation?").assertIsDisplayed()
        
        // Check if heating question is displayed
        composeTestRule.onNodeWithText("What is your primary heating source?").assertIsDisplayed()
        
        // Check if energy efficiency question is displayed
        composeTestRule.onNodeWithText("Do you have energy-efficient appliances?").assertIsDisplayed()
        
        // Check if submit button is displayed
        composeTestRule.onNodeWithText("Calculate My Footprint").assertIsDisplayed()
    }

    @Test
    fun testDietTypeSelection() {
        composeTestRule.setContent {
            UserDataScreen(navController = rememberNavController())
        }

        // Test diet type selection
        composeTestRule.onNodeWithText("Vegan").performClick()
        
        // Verify selection
        composeTestRule.onNodeWithText("Vegan").assertIsSelected()
        
        // Test other options
        composeTestRule.onNodeWithText("Vegetarian").performClick()
        composeTestRule.onNodeWithText("Vegetarian").assertIsSelected()
    }

    @Test
    fun testTransportationModeSelection() {
        composeTestRule.setContent {
            UserDataScreen(navController = rememberNavController())
        }

        // Test transportation mode selection
        composeTestRule.onNodeWithText("Public Transport").performClick()
        
        // Verify selection
        composeTestRule.onNodeWithText("Public Transport").assertIsSelected()
        
        // Test car option with vehicle type
        composeTestRule.onNodeWithText("Car").performClick()
        composeTestRule.onNodeWithText("Car").assertIsSelected()
        
        // Check if vehicle type options appear
        composeTestRule.onNodeWithText("Electric").assertIsDisplayed()
        composeTestRule.onNodeWithText("Gasoline").assertIsDisplayed()
    }

    @Test
    fun testHeatingSourceSelection() {
        composeTestRule.setContent {
            UserDataScreen(navController = rememberNavController())
        }

        // Test heating source selection
        composeTestRule.onNodeWithText("Natural Gas").performClick()
        composeTestRule.onNodeWithText("Natural Gas").assertIsSelected()
        
        // Test renewable option
        composeTestRule.onNodeWithText("Renewable Energy").performClick()
        composeTestRule.onNodeWithText("Renewable Energy").assertIsSelected()
    }

    @Test
    fun testEnergyEfficiencySelection() {
        composeTestRule.setContent {
            UserDataScreen(navController = rememberNavController())
        }

        // Test energy efficiency selection
        composeTestRule.onNodeWithText("High").performClick()
        composeTestRule.onNodeWithText("High").assertIsSelected()
        
        // Test other options
        composeTestRule.onNodeWithText("Medium").performClick()
        composeTestRule.onNodeWithText("Medium").assertIsSelected()
    }

    @Test
    fun testFormSubmission() {
        composeTestRule.setContent {
            UserDataScreen(navController = rememberNavController())
        }

        // Fill out the form
        composeTestRule.onNodeWithText("Vegetarian").performClick()
        composeTestRule.onNodeWithText("Public Transport").performClick()
        composeTestRule.onNodeWithText("Electricity").performClick()
        composeTestRule.onNodeWithText("High").performClick()
        
        // Submit the form
        composeTestRule.onNodeWithText("Calculate My Footprint").performClick()
        
        // Wait for processing
        composeTestRule.waitForIdle()
        
        // Check if we navigated or got results
        // This might need adjustment based on actual navigation behavior
    }

    @Test
    fun testFormValidation() {
        composeTestRule.setContent {
            UserDataScreen(navController = rememberNavController())
        }

        // Try to submit without filling required fields
        composeTestRule.onNodeWithText("Calculate My Footprint").performClick()
        
        // Wait for validation
        composeTestRule.waitForIdle()
        
        // Submit button should still be visible (form didn't submit)
        composeTestRule.onNodeWithText("Calculate My Footprint").assertIsDisplayed()
    }
} 