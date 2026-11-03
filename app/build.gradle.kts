plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// ===== The portal URL: single source of truth. Override with: ./gradlew assembleDebug -PportalUrl=https://... =====
val defaultPortalUrl = "https://ganjaflay.github.io/Watch-portal/"
val portalUrl: String = (project.findProperty("portalUrl") as String?)?.takeIf { it.isNotBlank() } ?: defaultPortalUrl

android {
    namespace = "com.nikolay.portalwatch"
    compileSdk = 36
    buildToolsVersion = "36.0.0"

    defaultConfig {
        applicationId = "com.nikolay.portalwatch"
        minSdk = 30
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
        buildConfigField("String", "PORTAL_URL", "\"$portalUrl\"")
    }

    buildFeatures { buildConfig = true }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("debug")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    // Kept dependency-free on purpose: plain platform WebView + framework Activity.
}
