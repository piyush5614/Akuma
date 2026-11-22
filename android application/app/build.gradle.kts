plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

layout.buildDirectory.set(file("D:/AndroidStudioData/FairFarm/android-application/app-build"))

val webProjectDir = file("../../apps/web")
val webDistDir = webProjectDir.resolve("dist")
val webAssetsDir = layout.projectDirectory.dir("src/main/assets/fairfarm")

val buildFairFarmWeb = tasks.register<Exec>("buildFairFarmWeb") {
    workingDir(webProjectDir)
    commandLine("cmd", "/c", "npm", "run", "build")
}

val syncFairFarmWebAssets = tasks.register<Copy>("syncFairFarmWebAssets") {
    dependsOn(buildFairFarmWeb)
    from(webDistDir)
    into(webAssetsDir)
}

tasks.named("preBuild") {
    dependsOn(syncFairFarmWebAssets)
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
        }
        release {
            isMinifyEnabled = true
            buildConfigField("String", "BASE_URL", "\"https://api.example.invalid/api/v1/\"")
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
