package com.example.carbonhero

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.navigation.compose.rememberNavController
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.carbonhero.screens.LoginScreen
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class LoginScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testLoginScreenDisplaysCorrectly() {
        // Test that the login screen displays all required elements
        composeTestRule.setContent {
            LoginScreen(navController = rememberNavController())
        }

        // Check if subtitle is displayed
        composeTestRule.onNodeWithText("Your path to sustainable living").assertIsDisplayed()
        
        // Check if welcome message is displayed
        composeTestRule.onNodeWithText("Welcome Back").assertIsDisplayed()
        
        // Check if email field is displayed
        composeTestRule.onNodeWithText("Email").assertIsDisplayed()
        
        // Check if password field is displayed
        composeTestRule.onNodeWithText("Password").assertIsDisplayed()
        
        // Check if login button is displayed
        composeTestRule.onNodeWithText("Login").assertIsDisplayed()
        
        // Check if register link is displayed (fix exact text)
        composeTestRule.onNodeWithText("Don't have an account? Register").assertIsDisplayed()
    }

    @Test
    fun testLoginFormInteraction() {
        composeTestRule.setContent {
            LoginScreen(navController = rememberNavController())
        }

        // Test email input
        composeTestRule.onNodeWithText("Email").performTextInput("test@example.com")
        
        // Test password input
        composeTestRule.onNodeWithText("Password").performTextInput("password123")
        
        // Check if login button is enabled (not loading)
        composeTestRule.onNodeWithText("Login").assertIsEnabled()
    }

    @Test
    fun testEmptyFieldsValidation() {
        composeTestRule.setContent {
            LoginScreen(navController = rememberNavController())
        }

        // Try to click login button without filling fields
        composeTestRule.onNodeWithText("Login").performClick()
        
        // Wait a bit for any potential error messages
        composeTestRule.waitForIdle()
        
        // The login button should still be visible (indicating form didn't submit)
        composeTestRule.onNodeWithText("Login").assertIsDisplayed()
    }
} 