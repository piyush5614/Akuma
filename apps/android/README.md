# FairFarm Android

## Web app mobile wrapper

The Android app is a full-screen WebView wrapper for the existing FairFarm web
application. The web source in `apps/web` is used unchanged. The APK loads the
configured web URL, preserves browser navigation with the Android back button,
enables JavaScript and local storage, and supports the web app's location
permission flow.

The debug wrapper uses `WEB_APP_URL` from `apps/android/gradle.properties`.
The current physical-phone value is `http://192.168.0.194:5173/`. Start the
existing web app with `npm run dev -- --host 0.0.0.0` and the backend with
`python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`.

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

## Install the APK on a phone

The fastest install path is USB debugging:

1. Enable **Developer options** and **USB debugging** on the Android phone.
2. Connect the phone to this computer and accept the debugging prompt.
3. Run:

```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $adb install -r "C:\Users\asus4\Desktop\FairFarm\artifacts\FairFarm-debug.apk"
```

Alternatively, copy `artifacts/FairFarm-debug.apk` to the phone using a USB
file transfer, Google Drive, or another approved transfer method. Open the
APK in the phone's Files app, allow installation from that source, and
approve the install prompt.

For a physical phone, the default emulator address `10.0.2.2` does not point
to the development computer. Set the app's `BASE_URL` to
`http://<computer-LAN-IP>:8000/api/v1`, rebuild, and keep the phone and
computer on the same Wi-Fi network. Allow TCP port 8000 through Windows
Firewall and start the backend with `--host 0.0.0.0`.

## Saathi chat

The Home tab now groups the common crop catalogue by vegetable, grain, and
fruit, accepts quantity, ranks markets, and can request next-crop ideas using
crop history and water availability. The Ask tab sends text questions to
`POST /api/v1/chat` using the same backend
as recommendations. It keeps the session id in the ViewModel, displays
localized replies, shows loading/offline errors, blocks duplicate sends, and
keeps the last 100 messages in the current app process. Start the backend
before testing with questions such as `Which nearby mandi gives the best net
return?` or `Should I sell my onion now?`.

Room persistence, native voice input/output, typed native result cards, and
GPS-derived context are planned follow-up work; the current chat screen uses
the existing manual location fallback and text input.

Saathi configuration uses the same backend URL as the rest of the app:
`BuildConfig.BASE_URL` from `gradle.properties` (the emulator default is
`http://10.0.2.2:8000/api/v1`). Backend provider selection is server-side via
`CHAT_PROVIDER`; rules mode needs no API key, while Anthropic or
OpenAI-compatible modes require their local environment keys.

Demo questions include `Which nearby mandi gives the best net return?`,
`Should I sell my onion now?`, and `What is net profit?`. All demo results are
labelled by the backend as demo data. The chat is text-only today, has
in-process history, and does not yet render typed native result cards.

## Permissions and troubleshooting

The app requests internet and coarse/fine location permissions. If GPS is
denied, use the manual location fallback. For a physical phone, use the
computer LAN IP and allow port 8000 through the firewall. Release builds
require HTTPS; debug builds allow cleartext only through the debug network
security configuration. Text-to-speech and speech recognition voice downloads
may be required for Marathi, Hindi, or English.
