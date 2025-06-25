package com.example.carbonhero.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.navigation.NavController
import com.google.firebase.auth.ktx.auth
import com.google.firebase.firestore.ktx.firestore
import com.google.firebase.ktx.Firebase
import kotlinx.coroutines.delay

@Composable
fun SplashScreen(navController: NavController) {
    val auth = Firebase.auth
    val db = Firebase.firestore
    var isChecking by remember { mutableStateOf(true) }

    // Firebase kullanıcı kontrolü
    LaunchedEffect(Unit) {
        val user = auth.currentUser
        if (user == null) {
            delay(1000) // Animasyon için küçük bekleme (isteğe bağlı)
            navController.navigate("login_screen") {
                popUpTo("splash_screen") { inclusive = true }
            }
        } else {
            db.collection("user_data")
                .whereEqualTo("userId", user.uid)
                .get()
                .addOnSuccessListener { documents ->
                    val target = if (!documents.isEmpty) "main_screen" else "user_data_screen"
                    navController.navigate(target) {
                        popUpTo("splash_screen") { inclusive = true }
                    }
                }
                .addOnFailureListener {
                    navController.navigate("login_screen") {
                        popUpTo("splash_screen") { inclusive = true }
                    }
                }
        }
    }

    // UI - Yükleniyor göstergesi
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        CircularProgressIndicator(
            color = Color(0xFF4CAF50)
        )
    }
}
