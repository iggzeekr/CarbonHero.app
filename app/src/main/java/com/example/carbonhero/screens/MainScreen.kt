package com.example.carbonhero.screens

import android.util.Log
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.DirectionsTransit
import androidx.compose.material.icons.filled.Eco
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.ExitToApp
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Lightbulb
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Power
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.Shower
import androidx.compose.material.icons.filled.ShoppingBag
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.Tv
import androidx.compose.material.icons.filled.WaterDrop
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.google.firebase.auth.ktx.auth
import com.google.firebase.firestore.ktx.firestore
import com.google.firebase.ktx.Firebase
import com.example.carbonhero.ui.theme.CarbonHeroBackground
import kotlinx.coroutines.tasks.await
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.ScrollState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.foundation.clickable
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.foundation.Image
import com.example.carbonhero.R
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.launch
import com.example.carbonhero.network.RetrofitInstance
import com.example.carbonhero.model.UserDataUpdate
import androidx.compose.foundation.background
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.platform.LocalContext
import android.widget.Toast
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CardElevation
import com.example.carbonhero.model.UserStatsResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import com.example.carbonhero.network.RecommendationResponse
import com.example.carbonhero.network.Recommendation
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.isActive

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(navController: NavController) {
    var selectedTab by remember { mutableStateOf(0) }
    var userStats by remember { mutableStateOf<UserStatsResponse?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }
    var userScore by remember { mutableStateOf(0) }
    var refreshRecommendations by remember { mutableStateOf(0) }
    var refreshLeaderboard by remember { mutableStateOf(0) }
    val currentUser = Firebase.auth.currentUser
    val userId = currentUser?.uid
    Log.d("MainScreen", "userId: $userId")
    val scope = rememberCoroutineScope()
    val context = LocalContext.current

    // Firebase auth state listener to handle authentication changes
    LaunchedEffect(Unit) {
        Firebase.auth.addAuthStateListener { auth ->
            val user = auth.currentUser
            if (user == null) {
                Log.d("MainScreen", "User signed out, navigating to login")
                navController.navigate("login") {
                    popUpTo("main") { inclusive = true }
                }
            } else {
                Log.d("MainScreen", "User signed in: ${user.uid}")
                // Refresh token to prevent timeout
                user.getIdToken(true).addOnCompleteListener { task ->
                    if (task.isSuccessful) {
                        Log.d("MainScreen", "Token refreshed successfully")
                    } else {
                        Log.e("MainScreen", "Token refresh failed", task.exception)
                    }
                }
            }
        }
    }

    // Ana ekranda ve profilde kullanılacak userStats'ı backend'den çek
    LaunchedEffect(userId) {
        if (userId != null) {
            try {
                isLoading = true
                val response = RetrofitInstance.api.getUserFootprint(userId)
                if (response.isSuccessful) {
                    userStats = response.body()
                } else {
                    error = "Veri alınamadı"
                }
            } catch (e: Exception) {
                error = e.message
            } finally {
                isLoading = false
            }
        }
    }

    CarbonHeroBackground {
        Scaffold(
            containerColor = Color.Transparent,
            contentColor = Color.White,
            topBar = {
                TopAppBar(
                    title = { Text("Carbon Hero", color = Color.White) },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = Color.Transparent
                    ),
                    actions = {
                        IconButton(onClick = {
                            Firebase.auth.signOut()
                            navController.navigate("login") {
                                popUpTo("main") { inclusive = true }
                            }
                        }) {
                            Icon(
                                imageVector = Icons.Default.ExitToApp,
                                contentDescription = "Logout",
                                tint = Color.White
                            )
                        }
                    }
                )
            },
            bottomBar = {
                NavigationBar(
                    containerColor = Color(0xFF1B5E20).copy(alpha = 0.9f)
                ) {
                    NavigationBarItem(
                        icon = { Icon(Icons.Default.Star, contentDescription = "Challenges") },
                        label = { Text("Challenges") },
                        selected = selectedTab == 0,
                        onClick = { selectedTab = 0 },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Color.White,
                            unselectedIconColor = Color.White.copy(alpha = 0.7f),
                            selectedTextColor = Color.White,
                            unselectedTextColor = Color.White.copy(alpha = 0.7f),
                            indicatorColor = Color(0xFF4CAF50).copy(alpha = 0.3f)
                        )
                    )
                    NavigationBarItem(
                        icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
                        label = { Text("Home") },
                        selected = selectedTab == 1,
                        onClick = { selectedTab = 1 },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Color.White,
                            unselectedIconColor = Color.White.copy(alpha = 0.7f),
                            selectedTextColor = Color.White,
                            unselectedTextColor = Color.White.copy(alpha = 0.7f),
                            indicatorColor = Color(0xFF4CAF50).copy(alpha = 0.3f)
                        )
                    )
                    NavigationBarItem(
                        icon = { Icon(Icons.Default.Person, contentDescription = "Profile") },
                        label = { Text("Profile") },
                        selected = selectedTab == 2,
                        onClick = { selectedTab = 2 },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Color.White,
                            unselectedIconColor = Color.White.copy(alpha = 0.7f),
                            selectedTextColor = Color.White,
                            unselectedTextColor = Color.White.copy(alpha = 0.7f),
                            indicatorColor = Color(0xFF4CAF50).copy(alpha = 0.3f)
                        )
                    )
                    NavigationBarItem(
                        icon = { Icon(Icons.Default.Lightbulb, contentDescription = "Recommendations") },
                        label = { Text("Tips") },
                        selected = selectedTab == 3,
                        onClick = { selectedTab = 3 },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Color.White,
                            unselectedIconColor = Color.White.copy(alpha = 0.7f),
                            selectedTextColor = Color.White,
                            unselectedTextColor = Color.White.copy(alpha = 0.7f),
                            indicatorColor = Color(0xFF4CAF50).copy(alpha = 0.3f)
                        )
                    )
                    NavigationBarItem(
                        icon = { Icon(Icons.Default.Favorite, contentDescription = "Leaderboard") },
                        label = { Text("Ranking") },
                        selected = selectedTab == 4,
                        onClick = { selectedTab = 4 },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Color.White,
                            unselectedIconColor = Color.White.copy(alpha = 0.7f),
                            selectedTextColor = Color.White,
                            unselectedTextColor = Color.White.copy(alpha = 0.7f),
                            indicatorColor = Color(0xFF4CAF50).copy(alpha = 0.3f)
                        )
                    )
                }
            }
        ) { paddingValues ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                when {
                    isLoading -> {
                        CircularProgressIndicator(
                            modifier = Modifier.align(Alignment.Center),
                            color = Color.White
                        )
                    }
                    error != null -> {
                        Text(
                            text = error!!,
                            color = Color.Red,
                            modifier = Modifier
                                .align(Alignment.Center)
                                .padding(16.dp)
                        )
                    }
                    else -> {
                        when (selectedTab) {
                            0 -> ChallengesTab(
                                userScore = userStats?.total_score ?: 0,
                                onScoreUpdated = { newScore ->
                                    userScore = newScore
                                    // Update userStats to persist the score across tab changes
                                    userStats = userStats?.copy(total_score = newScore)
                                    refreshLeaderboard++
                                },
                                userStats = userStats
                            )
                            1 -> HomeTab(userStats = userStats)
                            2 -> ProfileTab(
                                userData = userStats?.user_data,
                                onFieldUpdate = { field, value ->
                                    // Handle profile updates at MainScreen level to avoid scope cancellation
                                    scope.launch {
                                        try {
                                            Log.d("MainScreen", "Updating field: $field = $value")
                                            withContext(Dispatchers.IO) {
                                                val result = updateUserFieldApi(userId!!, field, value)
                                                if (result && isActive) {
                                                    val response = RetrofitInstance.api.getUserFootprint(userId)
                                                    if (response.isSuccessful && isActive) {
                                                        val newUserStats = response.body()
                                                        withContext(Dispatchers.Main) {
                                                            if (isActive) {
                                                                Log.d("MainScreen", "Profile updated! New stats: ${newUserStats?.current_footprint}")
                                                                Log.d("MainScreen", "New breakdown: ${newUserStats?.breakdown}")
                                                                userStats = newUserStats
                                                                refreshRecommendations++
                                                                Log.d("MainScreen", "Refreshing recommendations trigger: $refreshRecommendations")
                                                                Toast.makeText(context, "$field updated!", Toast.LENGTH_SHORT).show()
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        } catch (e: CancellationException) {
                                            // Coroutine was cancelled, do nothing
                                        } catch (e: Exception) {
                                            Log.e("MainScreen", "Error updating profile", e)
                                            if (isActive) {
                                                Toast.makeText(context, "Update failed: ${e.message}", Toast.LENGTH_SHORT).show()
                                            }
                                        }
                                    }
                                }
                            )
                            3 -> RecommendationTab(userId, selectedTab, refreshRecommendations)
                            4 -> LeaderboardTab(userScore, refreshLeaderboard)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ChallengesTab(userScore: Int = 0, onScoreUpdated: (Int) -> Unit = {}, userStats: UserStatsResponse? = null) {
    var selectedCategory by remember { mutableStateOf<String?>(null) }
    var totalScore by remember { mutableStateOf(userScore) }
    val currentUser = Firebase.auth.currentUser
    val scope = rememberCoroutineScope()

    // Update total score when userScore changes
    LaunchedEffect(userScore) {
        totalScore = userScore
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.White.copy(alpha = 0.9f)
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = "Challenges",
                    modifier = Modifier.size(48.dp),
                    tint = Color(0xFF1B5E20)
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Daily Challenges",
                    style = MaterialTheme.typography.headlineMedium,
                    color = Color(0xFF1B5E20)
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Total Score: $totalScore points",
                    style = MaterialTheme.typography.titleMedium,
                    color = Color(0xFF4CAF50),
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Complete challenges to reduce your carbon footprint",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.Gray,
                    textAlign = TextAlign.Center
                )
            }
        }

        if (selectedCategory == null) {
            // Category Selection View
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                val challengesByCategory = getPersonalizedChallengesByCategory(userStats)
                val categoryIcons = mapOf(
                    "Diet" to Icons.Default.Restaurant,
                    "Transportation" to Icons.Default.DirectionsCar,
                    "Housing" to Icons.Default.Lightbulb,
                    "Lifestyle" to Icons.Default.WaterDrop,
                    "Waste" to Icons.Default.Delete
                )
                
                challengesByCategory.forEach { (category, challenges) ->
                    item {
                        CategoryButton(
                            category = category,
                            icon = categoryIcons[category] ?: Icons.Default.Star,
                            challengeCount = challenges.size,
                            onClick = { selectedCategory = category }
                        )
                    }
                }
            }
        } else {
            // Selected Category Challenges View
            Column {
                // Back Button
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { selectedCategory = null }
                        .padding(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back",
                        tint = Color.White
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Back to Categories",
                        color = Color.White,
                        style = MaterialTheme.typography.titleMedium
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                // Category Title
                Text(
                    text = "$selectedCategory Challenges",
                    style = MaterialTheme.typography.headlineMedium,
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 16.dp)
                )
                
                // Challenges in Selected Category
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    val challenges = getPersonalizedChallengesByCategory(userStats)[selectedCategory] ?: emptyList()
                    items(challenges) { challenge ->
                        ChallengeCard(
                            challenge = challenge,
                            onComplete = {
                                // Challenge tamamlanınca backend'den güncel skoru çek
                                if (currentUser != null) {
                                    scope.launch {
                                        try {
                                            val response = RetrofitInstance.api.getUserFootprint(currentUser.uid)
                                            if (response.isSuccessful) {
                                                val newScore = response.body()?.total_score ?: 0
                                                totalScore = newScore
                                                onScoreUpdated(newScore)
                                            }
                                        } catch (_: Exception) {}
                                    }
                                }
                            }
                        )
                    }
                }
            }
        }
    }
}

private data class Challenge(
    val title: String,
    val description: String,
    val carbonSavings: Double,
    val difficulty: String,
    val icon: ImageVector,
    val category: String
)

private fun getPersonalizedChallengesByCategory(userStats: UserStatsResponse?): Map<String, List<Challenge>> {
    val baseChallenges = mapOf(
        "Diet" to listOf(
            Challenge("Plant-Based Meal", "Try a completely plant-based meal today", 3.5, "Easy", Icons.Default.Restaurant, "Diet"),
            Challenge("Reduce Meat Consumption", "Skip meat for one meal today", 2.0, "Medium", Icons.Default.Restaurant, "Diet"),
            Challenge("Local Produce Challenge", "Buy only locally grown produce today", 2.5, "Easy", Icons.Default.Restaurant, "Diet")
        ),
        "Transportation" to listOf(
            Challenge("Walk or Bike", "Choose walking or biking instead of driving for short trips", 2.0, "Easy", Icons.Default.DirectionsCar, "Transportation"),
            Challenge("Public Transport", "Use public transport instead of private car", 2.5, "Medium", Icons.Default.DirectionsTransit, "Transportation"),
            Challenge("Carpool Challenge", "Share a ride with someone today", 2.0, "Medium", Icons.Default.DirectionsCar, "Transportation")
        ),
        "Housing" to listOf(
            Challenge("Energy Saver", "Turn off lights and unplug devices when not in use", 1.0, "Easy", Icons.Default.Lightbulb, "Housing"),
            Challenge("Temperature Control", "Reduce heating/cooling by 2 degrees", 1.5, "Medium", Icons.Default.Thermostat, "Housing"),
            Challenge("LED Bulb Switch", "Replace one regular bulb with LED today", 0.5, "Easy", Icons.Default.Lightbulb, "Housing")
        ),
        "Lifestyle" to listOf(
            Challenge("Reduce Water Usage", "Take shorter showers and turn off taps when not in use", 0.8, "Easy", Icons.Default.WaterDrop, "Lifestyle"),
            Challenge("Digital Detox", "Reduce screen time by 1 hour today", 1.0, "Medium", Icons.Default.Tv, "Lifestyle"),
            Challenge("Second-Hand Shopping", "Buy something second-hand instead of new", 4.0, "Medium", Icons.Default.ShoppingBag, "Lifestyle")
        ),
        "Waste" to listOf(
            Challenge("Zero Waste Meal", "Prepare a meal using all ingredients with no waste", 1.5, "Medium", Icons.Default.Restaurant, "Waste"),
            Challenge("Recycle More", "Properly separate and recycle all waste today", 1.0, "Easy", Icons.Default.Delete, "Waste"),
            Challenge("Compost Challenge", "Start composting your food waste", 3.0, "Medium", Icons.Default.Delete, "Waste")
        )
    )
    
    // If no user stats, return base challenges
    if (userStats == null) return baseChallenges
    
    // Personalize challenges based on user's carbon footprint breakdown
    val breakdown = userStats.breakdown ?: return baseChallenges
    
    val personalizedChallenges = mutableMapOf<String, List<Challenge>>()
    
    // Diet challenges - if diet footprint is high
    val dietFootprint = breakdown["diet"] ?: 0.0
    if (dietFootprint > 2.0) {
        personalizedChallenges["Diet"] = baseChallenges["Diet"]!! + Challenge(
            "Vegan Day Challenge",
            "Go completely vegan for one day",
            5.0,
            "Hard",
            Icons.Default.Restaurant,
            "Diet"
        )
    } else {
        personalizedChallenges["Diet"] = baseChallenges["Diet"]!!
    }
    
    // Transportation challenges - if transportation footprint is high
    val transportFootprint = breakdown["transportation"] ?: 0.0
    if (transportFootprint > 3.0) {
        personalizedChallenges["Transportation"] = baseChallenges["Transportation"]!! + Challenge(
            "No Car Day",
            "Don't use your car at all today",
            4.0,
            "Hard",
            Icons.Default.DirectionsCar,
            "Transportation"
        )
    } else {
        personalizedChallenges["Transportation"] = baseChallenges["Transportation"]!!
    }
    
    // Housing challenges - if housing footprint is high
    val housingFootprint = breakdown["housing"] ?: 0.0
    if (housingFootprint > 2.5) {
        personalizedChallenges["Housing"] = baseChallenges["Housing"]!! + Challenge(
            "Energy Audit",
            "Conduct a home energy audit today",
            2.0,
            "Hard",
            Icons.Default.Lightbulb,
            "Housing"
        )
    } else {
        personalizedChallenges["Housing"] = baseChallenges["Housing"]!!
    }
    
    // Lifestyle challenges - if lifestyle footprint is high
    val lifestyleFootprint = breakdown["lifestyle"] ?: 0.0
    if (lifestyleFootprint > 1.0) {
        personalizedChallenges["Lifestyle"] = baseChallenges["Lifestyle"]!! + Challenge(
            "Minimalist Challenge",
            "Don't buy anything non-essential today",
            1.0,
            "Medium",
            Icons.Default.ShoppingBag,
            "Lifestyle"
        )
    } else {
        personalizedChallenges["Lifestyle"] = baseChallenges["Lifestyle"]!!
    }
    
    // Waste challenges - if waste footprint is high
    val wasteFootprint = breakdown["waste"] ?: 0.0
    if (wasteFootprint > 0.8) {
        personalizedChallenges["Waste"] = baseChallenges["Waste"]!! + Challenge(
            "Zero Waste Day",
            "Produce no waste at all today",
            2.5,
            "Hard",
            Icons.Default.Delete,
            "Waste"
        )
    } else {
        personalizedChallenges["Waste"] = baseChallenges["Waste"]!!
    }
    
    return personalizedChallenges
}

@Composable
private fun CategoryButton(
    category: String,
    icon: ImageVector,
    challengeCount: Int,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.9f)
        ),
        shape = RoundedCornerShape(16.dp),
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = category,
                modifier = Modifier.size(48.dp),
                tint = Color(0xFF1B5E20)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "$category Challenges",
                    style = MaterialTheme.typography.titleLarge,
                    color = Color(0xFF1B5E20),
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "$challengeCount challenges available",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.Gray
                )
            }
            Icon(
                imageVector = Icons.Default.ArrowBack,
                contentDescription = "Enter",
                modifier = Modifier.size(24.dp),
                tint = Color(0xFF1B5E20)
            )
        }
    }
}

@Composable
private fun ChallengeCard(challenge: Challenge, onComplete: () -> Unit = {}) {
    var completed by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val context = LocalContext.current
    val currentUser = Firebase.auth.currentUser

    // Dynamic points calculation
    val difficultyBonus = when (challenge.difficulty.lowercase()) {
        "easy" -> 0
        "medium" -> 10
        "hard" -> 20
        else -> 0
    }
    val points = (challenge.carbonSavings * 20).toInt() + difficultyBonus
    val personalizedDescription = "${challenge.description} (Estimated savings: ${challenge.carbonSavings} kg CO₂, Difficulty: ${challenge.difficulty.capitalize()})"

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (completed) Color(0xFF4CAF50).copy(alpha = 0.1f) else Color.White.copy(alpha = 0.9f)
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = challenge.icon,
                        contentDescription = challenge.title,
                        tint = if (completed) Color(0xFF4CAF50) else Color(0xFF1B5E20),
                        modifier = Modifier.size(32.dp)
                    )
                    Column {
                        Text(
                            text = challenge.title,
                            style = MaterialTheme.typography.titleMedium,
                            color = if (completed) Color(0xFF4CAF50) else Color(0xFF1B5E20)
                        )
                        Text(
                            text = personalizedDescription,
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.Gray
                        )
                    }
                }
                Column(
                    horizontalAlignment = Alignment.End
                ) {
                    Text(
                        text = "$points",
                        style = MaterialTheme.typography.titleLarge,
                        color = if (completed) Color(0xFF4CAF50) else Color(0xFF1B5E20)
                    )
                    Text(
                        text = "points",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Gray
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Button(
                onClick = {
                    if (!completed && !isLoading && currentUser != null) {
                        scope.launch {
                            try {
                                isLoading = true
                                val response = RetrofitInstance.api.completeChallenge(
                                    currentUser.uid,
                                    challenge.title
                                )
                                if (response.isSuccessful) {
                                    completed = true
                                    val responseBody = response.body()
                                    val pointsEarned = responseBody?.get("points_earned") as? Int ?: points
                                    val totalScore = responseBody?.get("total_score") as? Int ?: 0

                                    onComplete()
                                    Toast.makeText(context, "Challenge completed! +$pointsEarned points", Toast.LENGTH_SHORT).show()
                                } else {
                                    Toast.makeText(context, "Failed to complete challenge", Toast.LENGTH_SHORT).show()
                                }
                            } catch (e: Exception) {
                                Toast.makeText(context, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                            } finally {
                                isLoading = false
                            }
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (completed) Color(0xFF4CAF50) else Color(0xFF1B5E20),
                    disabledContainerColor = Color(0xFF4CAF50)
                ),
                enabled = !completed && !isLoading
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(16.dp),
                        color = Color.White,
                        strokeWidth = 2.dp
                    )
                } else {
                    Text(
                        text = if (completed) "✓ Completed" else "Complete Challenge",
                        color = Color.White
                    )
                }
            }
        }
    }
}

@Composable
fun HomeTab(userStats: UserStatsResponse?) {
    val scrollState = rememberScrollState()
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp)
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.White.copy(alpha = 0.9f)
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Your Carbon Footprint",
                    style = MaterialTheme.typography.headlineMedium,
                    color = Color(0xFF1B5E20)
                )
                Spacer(modifier = Modifier.height(16.dp))
                when {
                    userStats == null -> CircularProgressIndicator()
                    else -> {
                        val stats = userStats
                        Log.d("MainScreen", "UserStats: $stats")
                        Log.d("MainScreen", "Breakdown: ${stats.breakdown}")
                        Text(
                            text = "Total: ${String.format("%.1f", stats.current_footprint)} tons CO₂/year",
                            style = MaterialTheme.typography.titleLarge,
                            color = Color(0xFF1B5E20)
                        )
                        Spacer(modifier = Modifier.height(24.dp))
                        Text(
                            text = "Average: ${String.format("%.1f", stats.average_footprint)} tons/year",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color(0xFF1B5E20)
                        )
                        Text(
                            text = "Trend: ${String.format("%.1f", stats.trend)} tons (${String.format("%.1f", stats.trend_percentage)}%)",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color(0xFF1B5E20)
                        )
                        CategoryBreakdownChart(stats.breakdown)
                    }
                }
            }
        }
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.White.copy(alpha = 0.9f)
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Reduction Tips",
                    style = MaterialTheme.typography.headlineMedium,
                    color = Color(0xFF1B5E20)
                )
                Spacer(modifier = Modifier.height(16.dp))
                ReductionTipsList()
            }
        }
    }
}

@Composable
private fun ReductionTipsList() {
    Column(
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        ReductionTip(
            "Use Public Transport",
            "Reduce your transportation emissions by using public transit",
            Icons.Default.DirectionsTransit
        )
        ReductionTip(
            "Energy Efficient Appliances",
            "Switch to energy-efficient appliances to reduce electricity consumption",
            Icons.Default.Power
        )
        ReductionTip(
            "Reduce Waste",
            "Practice recycling and composting to minimize waste",
            Icons.Default.Delete
        )
    }
}

@Composable
private fun ReductionTip(title: String, description: String, icon: ImageVector) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = title,
            tint = Color(0xFF1B5E20),
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                color = Color(0xFF1B5E20)
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = Color.Gray
            )
        }
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun ProfileTab(userData: Map<String, Any?>?, onFieldUpdate: ((String, String) -> Unit)? = null) {
    var localUserData by remember { mutableStateOf(userData?.toMutableMap() ?: mutableMapOf()) }
    
    // Update local state when userData changes
    LaunchedEffect(userData) {
        userData?.let {
            localUserData = it.toMutableMap()
        }
    }
    val fields = listOf(
        Triple("Diet Type", "diet_type", listOf("Vegan", "Vegetarian", "Pescatarian", "Omnivore")),
        Triple("Transportation Mode", "transportation_mode", listOf("Public transport", "Private car", "Walking/Bicycle")),
        Triple("Vehicle Type", "vehicle_type", listOf("Petrol", "Diesel", "Electric", "I don't own a vehicle")),
        Triple("Heating Source", "heating_source", listOf("Coal", "Natural gas", "Electricity", "Wood")),
        Triple("Home Energy Efficiency", "home_energy_efficiency", listOf("No", "Sometimes", "Yes")),
        Triple("Shower Frequency", "shower_frequency", listOf("Daily", "Twice a day", "More frequently", "Less frequently")),
        Triple("Screen Time", "screen_time", listOf("Less than 4 hours", "4-8 hours", "8-16 hours", "More than 16 hours")),
        Triple("Internet Usage", "internet_usage", listOf("Less than 4 hours", "4-8 hours", "8-16 hours", "More than 16 hours")),
        Triple("Clothes Purchases", "clothes_purchases", listOf("0-10", "11-20", "21-30", "31+")),
        Triple("Recycling", "recycling", listOf("Paper", "Plastic", "Glass", "Metal", "I do not recycle")),
        Triple("Trash Bag Size", "trash_bag_size", listOf("Small", "Medium", "Large", "Extra large"))
    )
    val icons = mapOf(
        "diet_type" to Icons.Default.Restaurant,
        "transportation_mode" to Icons.Default.DirectionsTransit,
        "vehicle_type" to Icons.Default.DirectionsCar,
        "heating_source" to Icons.Default.Thermostat,
        "home_energy_efficiency" to Icons.Default.Eco,
        "shower_frequency" to Icons.Default.Shower,
        "screen_time" to Icons.Default.Tv,
        "internet_usage" to Icons.Default.Wifi,
        "clothes_purchases" to Icons.Default.ShoppingBag,
        "recycling" to Icons.Default.Delete,
        "trash_bag_size" to Icons.Default.Delete
    )
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.White.copy(alpha = 0.9f)
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Profile picture placeholder
                Image(
                    painter = painterResource(id = R.drawable.ic_profile_placeholder),
                    contentDescription = "Profile Picture",
                    modifier = Modifier
                        .size(96.dp)
                        .clip(CircleShape)
                        .background(Color(0xFF1B5E20))
                        .padding(8.dp),
                    contentScale = ContentScale.Crop
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "Welcome, ${localUserData["username"] ?: "User"}",
                    style = MaterialTheme.typography.headlineSmall,
                    color = Color(0xFF1B5E20)
                )
                Spacer(modifier = Modifier.height(24.dp))
                fields.forEach { (label, key, options) ->
                    EditableProfileCard(
                        label = label,
                        value = localUserData[key]?.toString() ?: "Not specified",
                        options = options,
                        icon = icons[key] ?: Icons.Default.Info,
                        onValueChange = { newValue ->
                            // Update local state immediately for UI responsiveness
                            localUserData = localUserData.toMutableMap().apply { put(key, newValue) }
                            
                            // Call the callback to handle backend update at MainScreen level
                            onFieldUpdate?.invoke(key, newValue)
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun EditableProfileCard(
    label: String,
    value: String,
    options: List<String>,
    icon: ImageVector,
    onValueChange: (String) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
            .clickable { expanded = true },
        shape = RoundedCornerShape(16.dp),
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = label,
                tint = Color(0xFF1B5E20),
                modifier = Modifier.size(32.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(label, style = MaterialTheme.typography.titleMedium, color = Color(0xFF1B5E20))
                Text(value, style = MaterialTheme.typography.bodyMedium, color = Color.Gray)
            }
        }
        DropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            options.forEach { option ->
                DropdownMenuItem(
                    onClick = {
                        onValueChange(option)
                        expanded = false
                    },
                    text = { Text(option) }
                )
            }
        }
    }
}

// Backend'e güncelleme isteği atan fonksiyon (örnek, gerçek API entegrasyonunu eklemelisin)
suspend fun updateUserFieldApi(userId: String, field: String, value: String): Boolean {
    Log.d("updateUserFieldApi", "Sending update request: userId=$userId, field=$field, value=$value")
    return try {
        val response = RetrofitInstance.api.updateUserData(userId, UserDataUpdate(field, value))
        if (response.isSuccessful) {
            val responseBody = response.body()
            Log.d("updateUserFieldApi", "Update request successful!")
            Log.d("updateUserFieldApi", "New footprint: ${responseBody?.get("new_footprint")}")
            Log.d("updateUserFieldApi", "New breakdown: ${responseBody?.get("new_breakdown")}")
            Log.d("updateUserFieldApi", "New recommendations count: ${(responseBody?.get("recommendations") as? List<*>)?.size}")
            true
        } else {
            Log.e("updateUserFieldApi", "Update request failed: ${response.code()} ${response.message()}")
            false
        }
    } catch (e: Exception) {
        Log.e("updateUserFieldApi", "Exception during update request: ${e.message}", e)
        false
    }
}

// UserStats'ı Map'e dönüştüren yardımcı fonksiyon
data class UserStatsHelper(
    val current_footprint: Double?,
    val average_footprint: Double?,
    val trend: Double?,
    val trend_percentage: Double?,
    val improvement_percentage: Double?,
    val challenges: Any?,
    val recent_footprints: Any?,
    val breakdown: Map<String, Double>?
)

fun com.example.carbonhero.model.UserStats.toMap(): MutableMap<String, Any?> {
    val map = mutableMapOf<String, Any?>()
    map["current_footprint"] = current_footprint
    map["average_footprint"] = average_footprint
    map["trend"] = trend
    map["trend_percentage"] = trend_percentage
    map["improvement_percentage"] = improvement_percentage
    map["challenges"] = challenges
    map["recent_footprints"] = recent_footprints
    breakdown?.forEach { (k, v) -> map[k] = v }
    return map
}

@Composable
private fun RecommendationItem(
    recommendation: Recommendation,
    categoryColor: Color
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = categoryColor.copy(alpha = 0.1f)
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            Text(
                text = recommendation.message ?: "No message available",
                style = MaterialTheme.typography.bodyMedium,
                color = Color(0xFF1B5E20)
            )
            Spacer(modifier = Modifier.height(4.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                if ((recommendation.improvement_potential ?: 0.0) > 0) {
                    Text(
                        text = "Potential: ${String.format("%.1f", recommendation.improvement_potential)} tons/year",
                        style = MaterialTheme.typography.bodySmall,
                        color = categoryColor,
                        fontWeight = FontWeight.Bold
                    )
                }
                if ((recommendation.similarity_score ?: 0.0) > 0) {
                    Text(
                        text = "Match: ${String.format("%.0f", (recommendation.similarity_score ?: 0.0) * 100)}%",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Gray
                    )
                }
            }
        }
    }
}

@Composable
private fun SimilarUserItem(user: Map<String, Any>) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = Icons.Default.Person,
            contentDescription = null,
            tint = Color(0xFF1B5E20),
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = "User ${user["userId"]}",
                style = MaterialTheme.typography.bodyMedium,
                color = Color(0xFF1B5E20)
            )
            Text(
                text = "Carbon Footprint: ${(user["carbon_footprint"] as Double).toInt()} units",
                style = MaterialTheme.typography.bodySmall,
                color = Color.Gray
            )
        }
        Text(
            text = "${(user["similarity_score"] as Double * 100).toInt()}%",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFF1B5E20)
        )
    }
}

@Composable
fun CategoryBreakdownChart(breakdown: Map<String, Double>?) {
    Log.d("CategoryBreakdownChart", "Received breakdown: $breakdown")
    if (breakdown == null) {
        Log.d("CategoryBreakdownChart", "Breakdown is null")
        return
    }
    // Sadece kategori anahtarlarını filtrele
    val categoryKeys = listOf("diet", "waste", "transportation", "lifestyle", "housing")
    val filteredBreakdown = breakdown.filter { (category, _) ->
        categoryKeys.contains(category.lowercase())
    }
    val total = filteredBreakdown.values.sum()
    Log.d("CategoryBreakdownChart", "Total: $total")
    
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
    ) {
        Text(
            text = "Category Breakdown",
            style = MaterialTheme.typography.titleMedium,
            color = Color(0xFF1B5E20)
        )
        Spacer(modifier = Modifier.height(16.dp))
        
        filteredBreakdown.forEach { (category, value) ->
            val percent = if (total > 0) (value / total * 100) else 0.0
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White.copy(alpha = 0.9f)
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = when (category.lowercase()) {
                            "diet" -> Icons.Default.Restaurant
                            "transportation" -> Icons.Default.DirectionsCar
                            "housing" -> Icons.Default.Home
                            "lifestyle" -> Icons.Default.Favorite
                            "waste" -> Icons.Default.Delete
                            else -> Icons.Default.Info
                        },
                        contentDescription = category,
                        tint = Color(0xFF1B5E20),
                        modifier = Modifier.size(32.dp)
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = category,
                            style = MaterialTheme.typography.titleMedium,
                            color = Color(0xFF1B5E20)
                        )
                        Text(
                            text = "${String.format("%.1f", value)} tons/year",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.Gray
                        )
                    }
                    Text(
                        text = "${String.format("%.1f", percent)}%",
                        style = MaterialTheme.typography.titleMedium,
                        color = Color(0xFF1B5E20)
                    )
                }
            }
        }
    }
}

@Composable
fun RecommendationTab(userId: String?, selectedTab: Int, refreshTrigger: Int = 0) {
    var recommendations by remember { mutableStateOf<RecommendationResponse?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    val context = LocalContext.current
    
    LaunchedEffect(userId, selectedTab, refreshTrigger) {
        if (userId != null && selectedTab == 3) {
            try {
                isLoading = true
                Log.d("RecommendationTab", "Loading recommendations for user: $userId")
                val response = RetrofitInstance.api.getUserRecommendations(userId)
                recommendations = response
                Log.d("RecommendationTab", "Loaded ${response.recommendations.size} recommendations")
                isLoading = false
            } catch (e: Exception) {
                error = e.message
                Log.e("RecommendationTab", "Error loading recommendations", e)
                isLoading = false
            }
        }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.White.copy(alpha = 0.9f)
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = "Recommendations",
                    modifier = Modifier.size(48.dp),
                    tint = Color(0xFF1B5E20)
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Smart Recommendations",
                    style = MaterialTheme.typography.headlineMedium,
                    color = Color(0xFF1B5E20)
                )
                Text(
                    text = "Personalized tips based on similar users",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.Gray,
                    textAlign = TextAlign.Center
                )
            }
        }
        
        when {
            isLoading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        CircularProgressIndicator(color = Color(0xFF4CAF50))
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = "Analyzing your carbon footprint...",
                            color = Color.White,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }
            error != null -> {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = Color.Red.copy(alpha = 0.1f)
                    )
                ) {
                    Text(
                        text = "Error loading recommendations: $error",
                        color = Color.Red,
                        modifier = Modifier.padding(16.dp)
                    )
                }
            }
            else -> {
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Define all 5 categories
                    val allCategories = listOf("Diet", "Transportation", "Housing", "Lifestyle", "Waste")
                    val categorizedRecs = recommendations?.recommendations?.groupBy { it.category } ?: emptyMap()
                    
                    // Show all categories
                    allCategories.forEach { category ->
                        item {
                            val categoryRecs = categorizedRecs[category] ?: emptyList()
                            if (categoryRecs.isNotEmpty()) {
                                // Has recommendations
                                CategoryRecommendationCard(
                                    category = category,
                                    recommendations = categoryRecs
                                )
                            } else {
                                // No recommendations - doing great!
                                CategoryDoingGreatCard(category = category)
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun LeaderboardTab(userScore: Int = 0, refreshTrigger: Int = 0) {
    var leaderboard by remember { mutableStateOf<List<com.example.carbonhero.model.LeaderboardUser>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    
    LaunchedEffect(refreshTrigger) {
        try {
            isLoading = true
            Log.d("LeaderboardTab", "Loading leaderboard...")
            val response = RetrofitInstance.api.getLeaderboard()
            if (response.isSuccessful) {
                val leaderboardResponse = response.body()
                Log.d("LeaderboardTab", "Response: ${leaderboardResponse?.status}")
                Log.d("LeaderboardTab", "Leaderboard size: ${leaderboardResponse?.leaderboard?.size}")
                leaderboard = leaderboardResponse?.leaderboard ?: emptyList()
                Log.d("LeaderboardTab", "Leaderboard loaded successfully with ${leaderboard.size} users")
            } else {
                error = "Failed to load leaderboard: ${response.code()}"
                Log.e("LeaderboardTab", "API Error: ${response.code()} - ${response.message()}")
            }
        } catch (e: Exception) {
            error = e.message
            Log.e("LeaderboardTab", "Exception loading leaderboard", e)
        } finally {
            isLoading = false
        }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
            Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.White.copy(alpha = 0.9f)
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = "Leaderboard",
                    modifier = Modifier.size(48.dp),
                    tint = Color(0xFF1B5E20)
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Leaderboard",
                    style = MaterialTheme.typography.headlineMedium,
                    color = Color(0xFF1B5E20)
                )
                Text(
                    text = "Your Score: $userScore points",
                    style = MaterialTheme.typography.titleMedium,
                    color = Color(0xFF4CAF50),
                    fontWeight = FontWeight.Bold
                )
            }
        }
        
        when {
            isLoading -> {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.CenterHorizontally),
                    color = Color(0xFF4CAF50)
                )
            }
            error != null -> {
                Text(
                    text = error!!,
                    color = Color.Red,
                    modifier = Modifier.align(Alignment.CenterHorizontally)
                )
            }
            else -> {
                LazyColumn {
                    items(leaderboard.size) { index ->
                        val user = leaderboard[index]
                        LeaderboardItem(
                            rank = user.rank,
                            username = user.username,
                            points = user.points,
                            carbonFootprint = user.getCarbonFootprintValue()
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun LeaderboardItem(
    rank: Int,
    username: String, 
    points: Int,
    carbonFootprint: Double
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.9f)
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "#$rank",
                style = MaterialTheme.typography.titleLarge,
                color = Color(0xFF1B5E20),
                fontWeight = FontWeight.Bold,
                modifier = Modifier.width(40.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = "User",
                tint = Color(0xFF1B5E20),
                modifier = Modifier.size(32.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = username,
                    style = MaterialTheme.typography.titleMedium,
                    color = Color(0xFF1B5E20)
                )
                Text(
                    text = "Carbon: ${String.format("%.1f", carbonFootprint)} tons/year",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray
                )
            }
            Text(
                text = "$points pts",
                style = MaterialTheme.typography.titleMedium,
                color = Color(0xFF4CAF50),
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
private fun CategoryRecommendationCard(
    category: String,
    recommendations: List<Recommendation>
) {
    val categoryIcon = when (category.lowercase()) {
        "diet" -> Icons.Default.Restaurant
        "transportation" -> Icons.Default.DirectionsCar  
        "housing" -> Icons.Default.Lightbulb
        "lifestyle" -> Icons.Default.WaterDrop
        "waste" -> Icons.Default.Delete
        else -> Icons.Default.Info
    }
    
    val categoryColor = when (category.lowercase()) {
        "diet" -> Color(0xFF4CAF50)
        "transportation" -> Color(0xFF2196F3)
        "housing" -> Color(0xFFFF9800)
        "lifestyle" -> Color(0xFF9C27B0)
        "waste" -> Color(0xFF795548)
        else -> Color(0xFF1B5E20)
    }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.9f)
        ),
        shape = RoundedCornerShape(16.dp),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Category Header
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(bottom = 12.dp)
            ) {
                Icon(
                    imageVector = categoryIcon,
                    contentDescription = category,
                    tint = categoryColor,
                    modifier = Modifier.size(32.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    text = "$category Recommendations",
                    style = MaterialTheme.typography.titleLarge,
                    color = categoryColor,
                    fontWeight = FontWeight.Bold
                )
            }
            
            // Recommendations
            recommendations.forEach { rec ->
                RecommendationItem(
                    recommendation = rec,
                    categoryColor = categoryColor
                )
                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@Composable
private fun CategoryDoingGreatCard(category: String) {
    val categoryIcon = when (category.lowercase()) {
        "diet" -> Icons.Default.Restaurant
        "transportation" -> Icons.Default.DirectionsCar  
        "housing" -> Icons.Default.Lightbulb
        "lifestyle" -> Icons.Default.WaterDrop
        "waste" -> Icons.Default.Delete
        else -> Icons.Default.Info
    }
    
    val categoryColor = when (category.lowercase()) {
        "diet" -> Color(0xFF4CAF50)
        "transportation" -> Color(0xFF2196F3)
        "housing" -> Color(0xFFFF9800)
        "lifestyle" -> Color(0xFF9C27B0)
        "waste" -> Color(0xFF795548)
        else -> Color(0xFF1B5E20)
    }
    
    val encouragingMessages = when (category.lowercase()) {
        "diet" -> "Great food choices! Your plant-based meals are making a real difference."
        "transportation" -> "Excellent travel habits! Keep using eco-friendly transportation."
        "housing" -> "Your home energy usage is fantastic! Well done on efficiency."
        "lifestyle" -> "Amazing lifestyle choices! You're living sustainably."
        "waste" -> "Perfect waste management! Your recycling efforts are paying off."
        else -> "You're doing great in this category!"
    }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.9f)
        ),
        shape = RoundedCornerShape(16.dp),
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Category Header
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(bottom = 12.dp)
            ) {
                Icon(
                    imageVector = categoryIcon,
                    contentDescription = category,
                    tint = categoryColor,
                    modifier = Modifier.size(32.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    text = "$category Status",
                    style = MaterialTheme.typography.titleLarge,
                    color = categoryColor,
                    fontWeight = FontWeight.Bold
                )
            }
            
            // Success Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF4CAF50).copy(alpha = 0.1f)
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Star,
                        contentDescription = "Success",
                        tint = Color(0xFF4CAF50),
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = "You're doing great!",
                            style = MaterialTheme.typography.titleMedium,
                            color = Color(0xFF1B5E20),
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = encouragingMessages,
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color(0xFF1B5E20)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun NoRecommendationsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.9f)
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier.padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.Eco,
                contentDescription = "Good job",
                modifier = Modifier.size(64.dp),
                tint = Color(0xFF4CAF50)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Great Job!",
                style = MaterialTheme.typography.headlineMedium,
                color = Color(0xFF1B5E20),
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "You're doing amazing! Keep up your eco-friendly lifestyle. Check back later for new personalized recommendations.",
                style = MaterialTheme.typography.bodyMedium,
                color = Color.Gray,
                textAlign = TextAlign.Center
            )
        }
    }
}