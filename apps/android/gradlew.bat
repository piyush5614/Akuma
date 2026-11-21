@echo off
setlocal
if defined JAVA_HOME (
  "%JAVA_HOME%\bin\java.exe" -version >nul 2>&1
  if not errorlevel 1 set JAVA_CMD=%JAVA_HOME%\bin\java.exe
)
if not defined JAVA_CMD set JAVA_CMD=java
%JAVA_CMD% -version >nul 2>&1
if errorlevel 1 (
  echo Java 17 or newer is required. Install a JDK and set JAVA_HOME.
  exit /b 1
)
echo Gradle wrapper JAR is not bundled in this source snapshot. Run with a generated wrapper from Android Studio.
exit /b 1
