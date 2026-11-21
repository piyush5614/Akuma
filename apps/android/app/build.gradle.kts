plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android { namespace = "com.fairfarm"; compileSdk = 35
    defaultConfig { applicationId = "com.fairfarm"; minSdk = 24; targetSdk = 35; versionCode = 1; versionName = "1.0.0" }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { buildConfig = true }
    buildTypes {
        debug {
            isMinifyEnabled = false
            buildConfigField("String", "BASE_URL", "\"${property("BASE_URL")}\"")
            buildConfigField("String", "WEB_APP_URL", "\"${property("WEB_APP_URL")}\"")
        }
        release {
            isMinifyEnabled = true
            buildConfigField("String", "BASE_URL", "\"https://api.example.invalid/api/v1/\"")
            buildConfigField("String", "WEB_APP_URL", "\"https://app.example.invalid/\"")
        }
    }
    packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.activity:activity-ktx:1.10.0")
    implementation("androidx.fragment:fragment-ktx:1.8.5")
    testImplementation("junit:junit:4.13.2")
}
