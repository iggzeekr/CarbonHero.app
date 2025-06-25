package com.example.carbonhero

import android.app.Application
import com.google.firebase.FirebaseApp

class CarbonHeroApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        FirebaseApp.initializeApp(this)
    }
} 