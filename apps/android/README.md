# FairFarm Android

The Android farmer app uses Kotlin, Jetpack Compose Material 3, Retrofit with
kotlinx.serialization, a repository/ViewModel boundary, Room-ready offline
dependencies, GPS permissions, OpenStreetMap dependencies, and debug-only
cleartext access for the emulator.

## Requirements

- Android Studio with JDK 17 and an Android SDK at API 35.
- An emulator uses `http://10.0.2.2:8000/api/v1/`; a physical phone needs the
  computer LAN address in `gradle.properties`.
- The verified local toolchain uses JDK 17, Android SDK API 35, and Gradle
  8.14.3.

## Run and build

Open `apps/android` in Android Studio and sync Gradle. Start the backend on port
8000, then run the `app` configuration. Build and validate with:

```text
gradlew.bat testDebugUnitTest lintDebug
gradlew.bat assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

The checked-in Gradle wrapper is usable on Windows. The Part 10 verification
completed `assembleDebug`, `testDebugUnitTest`, and `lintDebug`; the generated
debug APK is copied to `artifacts/FairFarm-debug.apk`.

## Saathi chat

The Ask tab sends text questions to `POST /api/v1/chat` using the same backend
as recommendations. It keeps the session id in the ViewModel, displays
localized replies, shows loading/offline errors, blocks duplicate sends, and
keeps the last 100 messages in the current app process. Start the backend
before testing with questions such as `Which nearby mandi gives the best net
return?` or `Should I sell my onion now?`.

Room persistence, native voice input/output, typed native result cards, and
GPS-derived context are planned follow-up work; the current chat screen uses
the existing manual location fallback and text input.

## Permissions and troubleshooting

The app requests internet and coarse/fine location permissions. If GPS is
denied, use the manual location fallback. For a physical phone, use the
computer LAN IP and allow port 8000 through the firewall. Release builds
require HTTPS; debug builds allow cleartext only through the debug network
security configuration. Text-to-speech and speech recognition voice downloads
may be required for Marathi, Hindi, or English.
