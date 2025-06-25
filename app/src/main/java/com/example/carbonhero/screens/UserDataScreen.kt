package com.example.carbonhero.screens

import android.util.Log
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.carbonhero.ui.theme.CarbonHeroBackground
import com.google.firebase.auth.ktx.auth
import com.google.firebase.firestore.ktx.firestore
import com.google.firebase.ktx.Firebase
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import com.example.carbonhero.model.UserTestResult
import com.example.carbonhero.model.RetrofitInstance
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import com.google.gson.Gson
import androidx.compose.ui.text.style.TextAlign

sealed class Question {
    data class SingleChoice(
        val question: String,
        val options: List<String>,
        val fieldName: String
    ) : Question()
    
    data class MultipleChoice(
        val question: String,
        val options: List<String>,
        val fieldName: String
    ) : Question()
    
    data class TextInput(
        val question: String,
        val fieldName: String
    ) : Question()
    
    data class YesNo(
        val question: String,
        val fieldName: String
    ) : Question()
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UserDataScreen(navController: NavController) {
    val auth = Firebase.auth
    val db = Firebase.firestore
    val focusManager = LocalFocusManager.current
    val scrollState = rememberScrollState()
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    var currentQuestionIndex by remember { mutableStateOf(0) }
    var userData by remember { mutableStateOf(mutableMapOf<String, Any>()) }

    LaunchedEffect(Unit) {
        if (auth.currentUser == null) {
            navController.navigate("login") {
                popUpTo("user_data") { inclusive = true }
            }
            return@LaunchedEffect
        }
    }

    val questions = listOf(
        Question.SingleChoice(
            "What is your diet type?",
            listOf("Vegan", "Vegetarian", "Pescatarian", "Omnivore"),
            "diet_type"
        ),
        Question.SingleChoice(
            "What is your main mode of transportation?",
            listOf("Public transport", "Private car", "Walking/Bicycle"),
            "transportation_mode"
        ),
        Question.SingleChoice(
            "What type of vehicle do you own?",
            listOf("Petrol", "Diesel", "Electric", "I don't own a vehicle"),
            "vehicle_type"
        ),
        Question.SingleChoice(
            "What is your home heating source?",
            listOf("Coal", "Natural gas", "Electricity", "Wood"),
            "heating_source"
        ),
        Question.SingleChoice(
            "Is your home energy efficient?",
            listOf("No", "Sometimes", "Yes"),
            "home_energy_efficiency"
        ),
        Question.SingleChoice(
            "How often do you shower?",
            listOf("Daily", "Twice a day", "More frequently", "Less frequently"),
            "shower_frequency"
        ),
        Question.SingleChoice(
            "How many hours do you spend on screens daily?",
            listOf("Less than 4 hours", "4-8 hours", "8-16 hours", "More than 16 hours"),
            "screen_time"
        ),
        Question.SingleChoice(
            "How many hours do you use the internet daily?",
            listOf("Less than 4 hours", "4-8 hours", "8-16 hours", "More than 16 hours"),
            "internet_usage"
        ),
        Question.SingleChoice(
            "How many new clothes do you buy per year?",
            listOf("0-10", "11-20", "21-30", "31+"),
            "clothes_purchases"
        ),
        Question.SingleChoice(
            "What do you recycle?",
            listOf("Paper", "Plastic", "Glass", "Metal", "I do not recycle"),
            "recycling"
        ),
        Question.SingleChoice(
            "What size trash bags do you use?",
            listOf("Small", "Medium", "Large", "Extra large"),
            "trash_bag_size"
        )
    )

    // Test tamamlandığında backend'e veri gönderme fonksiyonu
    fun submitUserData() {
        isLoading = true
        errorMessage = null
        
        val userId = auth.currentUser?.uid
        if (userId == null) {
            errorMessage = "User not authenticated"
            isLoading = false
            return
        }

        // Check if all questions are answered
        val requiredFields = listOf(
            "diet_type", "transportation_mode", "vehicle_type", 
            "heating_source", "home_energy_efficiency", "shower_frequency",
            "screen_time", "internet_usage", "clothes_purchases",
            "recycling", "trash_bag_size"
        )

        val missingFields = requiredFields.filter { field ->
            !userData.containsKey(field) || userData[field] == null
        }

        if (missingFields.isNotEmpty()) {
            errorMessage = "Please answer all questions before submitting"
            isLoading = false
            return
        }

        // UserData veri sınıfını oluştur
        val dataToSubmit = com.example.carbonhero.model.UserData(
            userId = userId,
            diet_type = userData["diet_type"] as String,
            transportation_mode = userData["transportation_mode"] as String,
            vehicle_type = userData["vehicle_type"] as String,
            heating_source = userData["heating_source"] as String,
            home_energy_efficiency = userData["home_energy_efficiency"] as String,
            shower_frequency = userData["shower_frequency"] as String,
            screen_time = userData["screen_time"] as String,
            internet_usage = userData["internet_usage"] as String,
            clothes_purchases = userData["clothes_purchases"] as String,
            recycling = userData["recycling"] as String,
            trash_bag_size = userData["trash_bag_size"] as String
        )

        // Firestore'a kaydet
        db.collection("user_data")
            .document(userId)
            .set(userData)
            .addOnSuccessListener {
                // Backend API'ye gönder
                CoroutineScope(Dispatchers.IO).launch {
                    try {
                        val response = RetrofitInstance.api.submitUserData(dataToSubmit)
                        withContext(Dispatchers.Main) {
                            if (response.isSuccessful) {
                                navController.navigate("main") {
                                    popUpTo("user_data") { inclusive = true }
                                }
                            } else {
                                errorMessage = "Failed to submit data to server"
                            }
                            isLoading = false
                        }
                    } catch (e: Exception) {
                        withContext(Dispatchers.Main) {
                            errorMessage = "Error: ${e.message}"
                            isLoading = false
                        }
                    }
                }
            }
            .addOnFailureListener {
                errorMessage = "Failed to save data locally"
                isLoading = false
            }
    }

    // Test ekranı UI'ı
    CarbonHeroBackground {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(scrollState),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                if (currentQuestionIndex < questions.size) {
                    val currentQuestion = questions[currentQuestionIndex]
                    
                    Text(
                        text = "Question ${currentQuestionIndex + 1} of ${questions.size}",
                        style = MaterialTheme.typography.titleMedium,
                        color = Color.White
                    )

                    // Add back button if not on first question
                    if (currentQuestionIndex > 0) {
                        Button(
                            onClick = {
                                currentQuestionIndex--
                            },
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(bottom = 8.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color.White.copy(alpha = 0.1f)
                            )
                        ) {
                            Text("← Back to Previous Question", color = Color.White)
                        }
                    }

                    Text(
                        text = currentQuestion.question,
                        style = MaterialTheme.typography.headlineSmall,
                        color = Color.White,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(vertical = 16.dp)
                    )

                    when (currentQuestion) {
                        is Question.SingleChoice -> {
                            currentQuestion.options.forEach { option ->
                                val isSelected = userData[currentQuestion.fieldName] == option
                                Button(
                                    onClick = {
                                        userData[currentQuestion.fieldName] = option
                                        if (currentQuestionIndex < questions.size - 1) {
                                            currentQuestionIndex++
                                        } else {
                                            submitUserData()
                                        }
                                    },
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(vertical = 4.dp),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = if (isSelected) 
                                            Color(0xFF4CAF50).copy(alpha = 0.7f) 
                                        else 
                                            Color.White.copy(alpha = 0.2f)
                                    )
                                ) {
                                    Text(
                                        text = option,
                                        color = Color.White,
                                        style = MaterialTheme.typography.bodyLarge
                                    )
                                }
                            }
                        }
                    }

                    // Show progress
                    LinearProgressIndicator(
                        progress = (currentQuestionIndex + 1).toFloat() / questions.size,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 16.dp),
                        color = Color(0xFF4CAF50),
                        trackColor = Color.White.copy(alpha = 0.2f)
                    )
                }

                if (isLoading) {
                    CircularProgressIndicator(color = Color.White)
                }

                errorMessage?.let {
                    Text(
                        text = it,
                        color = Color.Red,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }
    }
} 