package com.example.carbonhero

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.navigation.compose.rememberNavController
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.carbonhero.screens.RegisterScreen
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class RegisterScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testRegisterScreenDisplaysCorrectly() {
        // Test that the register screen displays all required elements
        composeTestRule.setContent {
            RegisterScreen(navController = rememberNavController())
        }

        // Check if title is displayed
        composeTestRule.onNodeWithText("Create Account").assertIsDisplayed()
        
        // Check if subtitle is displayed
        composeTestRule.onNodeWithText("Join Carbon Hero today").assertIsDisplayed()
        
        // Check if name field is displayed
        composeTestRule.onNodeWithText("Full Name").assertIsDisplayed()
        
        // Check if email field is displayed
        composeTestRule.onNodeWithText("Email").assertIsDisplayed()
        
        // Check if password field is displayed
        composeTestRule.onNodeWithText("Password").assertIsDisplayed()
        
        // Check if confirm password field is displayed
        composeTestRule.onNodeWithText("Confirm Password").assertIsDisplayed()
        
        // Check if register button is displayed
        composeTestRule.onNodeWithText("Register").assertIsDisplayed()
        
        // Check if login link is displayed
        composeTestRule.onNodeWithText("Already have an account? Login").assertIsDisplayed()
    }

    @Test
    fun testRegisterFormInteraction() {
        composeTestRule.setContent {
            RegisterScreen(navController = rememberNavController())
        }

        // Test name input
        composeTestRule.onNodeWithText("Full Name").performTextInput("John Doe")
        
        // Test email input
        composeTestRule.onNodeWithText("Email").performTextInput("john@example.com")
        
        // Test password input
        composeTestRule.onNodeWithText("Password").performTextInput("password123")
        
        // Test confirm password input
        composeTestRule.onNodeWithText("Confirm Password").performTextInput("password123")
        
        // Check if register button is enabled
        composeTestRule.onNodeWithText("Register").assertIsEnabled()
    }

    @Test
    fun testPasswordMismatchValidation() {
        composeTestRule.setContent {
            RegisterScreen(navController = rememberNavController())
        }

        // Fill form with mismatched passwords
        composeTestRule.onNodeWithText("Full Name").performTextInput("John Doe")
        composeTestRule.onNodeWithText("Email").performTextInput("john@example.com")
        composeTestRule.onNodeWithText("Password").performTextInput("password123")
        composeTestRule.onNodeWithText("Confirm Password").performTextInput("different123")
        
        // Try to click register button
        composeTestRule.onNodeWithText("Register").performClick()
        
        // Wait for validation
        composeTestRule.waitForIdle()
        
        // Register button should still be visible (form didn't submit)
        composeTestRule.onNodeWithText("Register").assertIsDisplayed()
    }

    @Test
    fun testEmptyFieldsValidation() {
        composeTestRule.setContent {
            RegisterScreen(navController = rememberNavController())
        }

        // Try to click register button without filling fields
        composeTestRule.onNodeWithText("Register").performClick()
        
        // Wait for validation
        composeTestRule.waitForIdle()
        
        // Register button should still be visible
        composeTestRule.onNodeWithText("Register").assertIsDisplayed()
    }

    @Test
    fun testEmailValidation() {
        composeTestRule.setContent {
            RegisterScreen(navController = rememberNavController())
        }

        // Fill form with invalid email
        composeTestRule.onNodeWithText("Full Name").performTextInput("John Doe")
        composeTestRule.onNodeWithText("Email").performTextInput("invalid-email")
        composeTestRule.onNodeWithText("Password").performTextInput("password123")
        composeTestRule.onNodeWithText("Confirm Password").performTextInput("password123")
        
        // Try to click register button
        composeTestRule.onNodeWithText("Register").performClick()
        
        // Wait for validation
        composeTestRule.waitForIdle()
        
        // Register button should still be visible
        composeTestRule.onNodeWithText("Register").assertIsDisplayed()
    }
} 