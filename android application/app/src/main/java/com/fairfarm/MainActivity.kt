package com.fairfarm

import android.Manifest
import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.View
import android.webkit.GeolocationPermissions
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.ValueCallback
import android.widget.FrameLayout
import android.widget.ProgressBar
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat

class MainActivity : ComponentActivity() {
    private lateinit var webView: WebView
    private lateinit var localWebServer: LocalWebServer
    private lateinit var progressBar: ProgressBar
    private var pendingGeolocationOrigin: String? = null
    private var pendingGeolocationCallback: GeolocationPermissions.Callback? = null
    private var pendingFileCallback: ValueCallback<Array<Uri>>? = null

    private val filePicker = registerForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        val callback = pendingFileCallback
        pendingFileCallback = null
        callback?.onReceiveValue(if (uri != null) arrayOf(uri) else null)
    }

    private val locationPermission = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val granted = permissions[Manifest.permission.ACCESS_FINE_LOCATION] == true ||
            permissions[Manifest.permission.ACCESS_COARSE_LOCATION] == true
        val origin = pendingGeolocationOrigin
        val callback = pendingGeolocationCallback
        if (granted && origin != null && callback != null) {
            callback.invoke(origin, true, false)
        } else {
            callback?.invoke(origin, false, false)
        }
        pendingGeolocationOrigin = null
        pendingGeolocationCallback = null
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        progressBar = ProgressBar(this).apply {
            isIndeterminate = true
            setPadding(0, 0, 0, 0)
        }
        val container = FrameLayout(this)
        webView = WebView(this)
        webView.layoutParams = android.view.ViewGroup.LayoutParams(
            android.view.ViewGroup.LayoutParams.MATCH_PARENT,
            android.view.ViewGroup.LayoutParams.MATCH_PARENT
        )
        val progressLayout = FrameLayout.LayoutParams(
            96,
            96,
            android.view.Gravity.CENTER
        )
        progressBar.layoutParams = progressLayout
        container.addView(webView)
        container.addView(progressBar)
        webView.overScrollMode = View.OVER_SCROLL_NEVER
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            mediaPlaybackRequiresUserGesture = false
            setSupportZoom(true)
            builtInZoomControls = true
            displayZoomControls = false
            cacheMode = WebSettings.LOAD_DEFAULT
            allowFileAccess = false
            allowContentAccess = false
        }
        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView, url: String?, favicon: android.graphics.Bitmap?) {
                progressBar.visibility = View.VISIBLE
            }

            override fun onPageFinished(view: WebView, url: String?) {
                progressBar.visibility = View.GONE
            }

            override fun onReceivedError(
                view: WebView,
                request: android.webkit.WebResourceRequest,
                error: android.webkit.WebResourceError
            ) {
                if (!request.isForMainFrame) return
                progressBar.visibility = View.GONE
                showErrorPage(
                    "FairFarm could not load",
                    "The app's local interface failed to start. Rebuild or reinstall the APK, then try again.",
                    error.description?.toString() ?: "Unknown WebView error"
                )
            }

            override fun onReceivedHttpError(
                view: WebView,
                request: android.webkit.WebResourceRequest,
                errorResponse: android.webkit.WebResourceResponse
            ) {
                if (!request.isForMainFrame) return
                progressBar.visibility = View.GONE
                showErrorPage(
                    "FairFarm server error",
                    "The local web interface returned HTTP ${errorResponse.statusCode}.",
                    errorResponse.reasonPhrase ?: "Unable to load the FairFarm interface"
                )
            }

            override fun shouldOverrideUrlLoading(
                view: WebView,
                request: WebResourceRequest
            ): Boolean {
                val appHost = Uri.parse(localWebServer.url()).host
                val requestedUrl = request.url
                if (requestedUrl.scheme == "http" || requestedUrl.scheme == "https") {
                    if (requestedUrl.host != appHost) {
                        startActivity(
                            Intent(Intent.ACTION_VIEW, requestedUrl)
                        )
                        return true
                    }
                }
                return false
            }
        }
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView,
                filePathCallback: ValueCallback<Array<Uri>>,
                fileChooserParams: FileChooserParams
            ): Boolean {
                pendingFileCallback?.onReceiveValue(null)
                pendingFileCallback = filePathCallback
                filePicker.launch(
                    if (fileChooserParams.acceptTypes.isNotEmpty()) {
                        fileChooserParams.acceptTypes.firstOrNull()?.ifBlank { "*/*" } ?: "*/*"
                    } else {
                        "*/*"
                    }
                )
                return true
            }

            override fun onGeolocationPermissionsShowPrompt(
                origin: String,
                callback: GeolocationPermissions.Callback
            ) {
                val fineGranted = ContextCompat.checkSelfPermission(
                    this@MainActivity,
                    Manifest.permission.ACCESS_FINE_LOCATION
                ) == PackageManager.PERMISSION_GRANTED
                val coarseGranted = ContextCompat.checkSelfPermission(
                    this@MainActivity,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                ) == PackageManager.PERMISSION_GRANTED

                if (fineGranted || coarseGranted) {
                    callback.invoke(origin, true, false)
                } else {
                    pendingGeolocationOrigin = origin
                    pendingGeolocationCallback = callback
                    locationPermission.launch(
                        arrayOf(
                            Manifest.permission.ACCESS_FINE_LOCATION,
                            Manifest.permission.ACCESS_COARSE_LOCATION
                        )
                    )
                }
            }
        }

        localWebServer = LocalWebServer(this, BuildConfig.BASE_URL)
        setContentView(container)
        if (localWebServer.start()) {
            webView.loadUrl(localWebServer.url())
        } else {
            progressBar.visibility = View.GONE
            showErrorPage(
                "FairFarm could not start",
                "The app-local web server could not open port 4173.",
                "Close other FairFarm app instances and reopen this app."
            )
        }

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                }
            }
        })
    }

    private fun showErrorPage(title: String, message: String, detail: String) {
        val html = """
            <!doctype html>
            <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
            <style>
              body{margin:0;height:100vh;display:grid;place-items:center;background:#f6f8fc;font-family:system-ui,sans-serif;color:#111827}
              article{max-width:420px;margin:24px;padding:28px;border:1px solid #e4e8f0;border-radius:18px;background:#fff;box-shadow:0 18px 50px rgba(31,98,220,.12);text-align:center}
              h1{font-size:24px;margin:0 0 10px}p{line-height:1.55;color:#687184}small{display:block;margin-top:14px;color:#9aa3b2}
              button{min-height:48px;border:0;border-radius:10px;padding:0 18px;background:#1f62dc;color:white;font-weight:800}
            </style></head><body><article>
              <h1>${title}</h1><p>${message}</p><button onclick="location.reload()">Try again</button><small>${detail}</small>
            </article></body></html>
        """.trimIndent()
        webView.loadDataWithBaseURL(localWebServer.url(), html, "text/html", "utf-8", null)
    }

    override fun onDestroy() {
        if (this::localWebServer.isInitialized) localWebServer.stop()
        if (this::webView.isInitialized) webView.destroy()
        super.onDestroy()
    }
}
