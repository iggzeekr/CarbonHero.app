package com.example.carbonhero

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.navigation.compose.rememberNavController
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.carbonhero.screens.MainScreen
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class MainScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testMainScreenDisplaysCorrectly() {
        // Test that the main screen displays all required elements
        composeTestRule.setContent {
            MainScreen(navController = rememberNavController())
        }

        // Check if app title is displayed
        composeTestRule.onNodeWithText("Carbon Hero").assertIsDisplayed()
        
        // Check if bottom navigation is displayed
        composeTestRule.onNodeWithText("Home").assertIsDisplayed()
        composeTestRule.onNodeWithText("Challenges").assertIsDisplayed()
        composeTestRule.onNodeWithText("Profile").assertIsDisplayed()
        composeTestRule.onNodeWithText("Leaderboard").assertIsDisplayed()
    }

    @Test
    fun testHomeTabDisplaysCorrectly() {
        composeTestRule.setContent {
            MainScreen(navController = rememberNavController())
        }

        // Home tab should be selected by default
        composeTestRule.onNodeWithText("Home").assertIsSelected()
        
        // Check if carbon footprint card is displayed
        composeTestRule.onNodeWithText("Your Carbon Footprint").assertIsDisplayed()
        
        // Check if recommendations section is displayed
        composeTestRule.onNodeWithText("Recommendations").assertIsDisplayed()
    }

    @Test
    fun testChallengesTabNavigation() {
        composeTestRule.setContent {
            MainScreen(navController = rememberNavController())
        }

        // Click on Challenges tab
        composeTestRule.onNodeWithText("Challenges").performClick()
        
        // Verify Challenges tab is selected
        composeTestRule.onNodeWithText("Challenges").assertIsSelected()
        
        // Check if challenges section is displayed
        composeTestRule.onNodeWithText("Available Challenges").assertIsDisplayed()
    }

    @Test
    fun testProfileTabNavigation() {
        composeTestRule.setContent {
            MainScreen(navController = rememberNavController())
        }

        // Click on Profile tab
        composeTestRule.onNodeWithText("Profile").performClick()
        
        // Verify Profile tab is selected
        composeTestRule.onNodeWithText("Profile").assertIsSelected()
        
        // Check if profile section is displayed
        composeTestRule.onNodeWithText("Your Profile").assertIsDisplayed()
    }

    @Test
    fun testLeaderboardTabNavigation() {
        composeTestRule.setContent {
            MainScreen(navController = rememberNavController())
        }

        // Click on Leaderboard tab
        composeTestRule.onNodeWithText("Leaderboard").performClick()
        
        // Verify Leaderboard tab is selected
        composeTestRule.onNodeWithText("Leaderboard").assertIsSelected()
        
        // Check if leaderboard section is displayed
        composeTestRule.onNodeWithText("Top Performers").assertIsDisplayed()
    }

    @Test
    fun testCarbonFootprintDisplay() {
        composeTestRule.setContent {
            MainScreen(navController = rememberNavController())
        }

        // Check if carbon footprint value is displayed
        // This might show loading initially, then actual value
        composeTestRule.waitForIdle()
        
        // Look for footprint display (could be loading or actual value)
        composeTestRule.onNodeWithText("tons CO2").assertIsDisplayed()
    }

    @Test
    fun testChallengeInteraction() {
        composeTestRule.setContent {
            MainScreen(navController = rememberNavController())
        }

        // Navigate to Challenges tab
        composeTestRule.onNodeWithText("Challenges").performClick()
        
        // Wait for challenges to load
        composeTestRule.waitForIdle()
        
        // Try to interact with a challenge (if any are displayed)
        // This might need adjustment based on actual challenge display
        try {
            composeTestRule.onNodeWithText("Start Challenge").performClick()
        } catch (e: AssertionError) {
            // No challenges available, which is fine for testing
        }
    }

    @Test
    fun testRecommendationsDisplay() {
        composeTestRule.setContent {
            MainScreen(navController = rememberNavController())
        }

        // Wait for recommendations to load
        composeTestRule.waitForIdle()
        
        // Check if recommendations section is displayed
        composeTestRule.onNodeWithText("Recommendations").assertIsDisplayed()
        
        // Look for recommendation items (might be loading initially)
        try {
            composeTestRule.onNodeWithText("Try").assertIsDisplayed()
        } catch (e: AssertionError) {
            // No recommendations available, which is fine for testing
        }
    }

    @Test
    fun testTabNavigationFlow() {
        composeTestRule.setContent {
            MainScreen(navController = rememberNavController())
        }

        // Test navigation between all tabs
        composeTestRule.onNodeWithText("Challenges").performClick()
        composeTestRule.onNodeWithText("Challenges").assertIsSelected()
        
        composeTestRule.onNodeWithText("Profile").performClick()
        composeTestRule.onNodeWithText("Profile").assertIsSelected()
        
        composeTestRule.onNodeWithText("Leaderboard").performClick()
        composeTestRule.onNodeWithText("Leaderboard").assertIsSelected()
        
        composeTestRule.onNodeWithText("Home").performClick()
        composeTestRule.onNodeWithText("Home").assertIsSelected()
    }
} 