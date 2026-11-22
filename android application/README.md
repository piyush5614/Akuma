# FairFarm Android Application

This folder is a complete Android Studio project. It wraps the existing FairFarm
web application in a full-screen Android WebView, so all web routes, login,
dashboard, maps, forms, data import, language controls, and chat behavior remain
the same as the web app.

The web source under `apps/web` is not included or modified by this project.

## Requirements

- Android Studio with JDK 17
- Android SDK API 35
- The FairFarm backend running on port 8000

## Open in Android Studio

1. Open Android Studio.
2. Choose **Open** and select this `android application` folder.
3. Allow Gradle sync to finish.
4. Choose an emulator or physical Android device.

The project expects JDK 17. Configure `local.properties` only if Android Studio
does not detect the SDK automatically:

```properties
sdk.dir=C:\\Users\\<you>\\AppData\\Local\\Android\\Sdk
```

## Disk location

The project and Gradle cache are configured for D: storage:

- Gradle cache: `D:\AndroidStudioData\GradleUserHome`
- Root build output: `D:\AndroidStudioData\FairFarm\android-application\root-build`
- App build output: `D:\AndroidStudioData\FairFarm\android-application\app-build`

Keep at least 5 GB free on D: for Android SDK, Gradle dependencies, and build
artifacts. For a different disk or folder, update `org.gradle.user.home` and
the `layout.buildDirectory` paths in the Gradle files.

## Start the backend

From the FairFarm repository root:

```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Emulator configuration

The default `gradle.properties` uses:

```properties
BASE_URL=http://10.0.2.2:8000/api/v1/
```

Android emulator `10.0.2.2` maps to the computer's localhost.

## Physical phone configuration

1. Put the phone and computer on the same Wi-Fi network.
2. Find the computer IPv4 address with `ipconfig`.
3. Update `gradle.properties`:

```properties
BASE_URL=http://<computer-ip>:8000/api/v1/
```

4. Sync Gradle and rebuild.
5. Allow TCP port 8000 through Windows Firewall.

## Build and install

```powershell
Set-Location "android application"
.\gradlew.bat testDebugUnitTest
.\gradlew.bat lintDebug
.\gradlew.bat assembleDebug
adb install -r app\build\outputs\apk\debug\app-debug.apk
```

The wrapper supports browser JavaScript, local storage, Android back navigation,
web geolocation prompts, file inputs for CSV import, and external map links.
