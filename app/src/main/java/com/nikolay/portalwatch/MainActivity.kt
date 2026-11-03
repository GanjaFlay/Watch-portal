package com.nikolay.portalwatch

import android.annotation.SuppressLint
import android.app.Activity
import android.graphics.Color
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.InputDevice
import android.view.KeyEvent
import android.view.MotionEvent
import android.view.View
import android.view.ViewConfiguration
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.view.WindowManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.TextView
import android.window.OnBackInvokedCallback
import android.window.OnBackInvokedDispatcher
import kotlin.math.roundToInt

class MainActivity : Activity() {

    private lateinit var root: FrameLayout
    private lateinit var webView: WebView
    private lateinit var reloadButton: TextView

    private val handler = Handler(Looper.getMainLooper())
    private val hideReload = Runnable { setReloadVisible(false) }

    /** True when the last main-frame load failed (network error). */
    private var loadFailed = false
    /** URL that failed, so retry/onResume can reload the right page. */
    private var failedUrl: String? = null

    private var backCallback: OnBackInvokedCallback? = null
    private var backCallbackRegistered = false

    private val portalUrl: String get() = BuildConfig.PORTAL_URL

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        root = FrameLayout(this).apply { setBackgroundColor(Color.BLACK) }

        webView = WebView(this).apply {
            setBackgroundColor(Color.BLACK)
            isVerticalScrollBarEnabled = false
            isHorizontalScrollBarEnabled = false
            isFocusable = true
            isFocusableInTouchMode = true
        }
        with(webView.settings) {
            javaScriptEnabled = true
            domStorageEnabled = true          // localStorage / sessionStorage
            @Suppress("DEPRECATION")
            databaseEnabled = true
            mediaPlaybackRequiresUserGesture = false
            cacheMode = WebSettings.LOAD_DEFAULT
            loadWithOverviewMode = true
            useWideViewPort = true
            builtInZoomControls = false
            displayZoomControls = false
            setSupportZoom(false)
            mixedContentMode = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE
        }
        webView.webChromeClient = WebChromeClient()
        webView.webViewClient = PortalClient()

        root.addView(
            webView,
            FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT)
        )

        val size = dp(40)
        reloadButton = TextView(this).apply {
            text = "\u21BB" // ↻
            textSize = 20f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            setBackgroundResource(R.drawable.reload_bg)
            contentDescription = "Reload"
            alpha = 0f
            visibility = View.GONE
            setOnClickListener { reloadPortal() }
        }
        root.addView(
            reloadButton,
            FrameLayout.LayoutParams(size, size, Gravity.BOTTOM or Gravity.CENTER_HORIZONTAL).apply {
                bottomMargin = dp(8)
            }
        )

        setContentView(root)
        goImmersive()
        setupBackHandling()

        if (savedInstanceState != null) {
            webView.restoreState(savedInstanceState)
        } else {
            webView.loadUrl(portalUrl)
        }
        setReloadVisible(true) // show briefly on launch so the user knows it exists
    }

    // ---------- WebView client ----------

    private inner class PortalClient : WebViewClient() {
        override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
            val scheme = request.url.scheme?.lowercase()
            // Keep http(s), file, data, about inside the WebView; drop other schemes (intent:, tel:, ...)
            return !(scheme == "http" || scheme == "https" || scheme == "file" || scheme == "data" || scheme == "about")
        }

        override fun onPageStarted(view: WebView, url: String?, favicon: android.graphics.Bitmap?) {
            if (url != null && !url.startsWith("data:") && url != ERROR_BASE) {
                loadFailed = false
                failedUrl = null
            }
        }

        override fun onReceivedError(view: WebView, request: WebResourceRequest, error: WebResourceError) {
            if (request.isForMainFrame) {
                loadFailed = true
                failedUrl = request.url.toString()
                showErrorPage(error.description?.toString() ?: "Unknown error")
            }
        }

        override fun doUpdateVisitedHistory(view: WebView, url: String?, isReload: Boolean) {
            updateBackCallback()
        }
    }

    private fun showErrorPage(reason: String) {
        val target = failedUrl ?: portalUrl
        val online = isOnline()
        val html = """
            <!doctype html><html><head>
            <meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
            <style>
              html,body{margin:0;height:100%;background:#000;color:#eee;font-family:sans-serif}
              body{display:flex;align-items:center;justify-content:center;text-align:center;padding:15%;box-sizing:border-box}
              h1{font-size:20px;margin:0 0 6px}
              p{font-size:12px;color:#999;margin:0 0 14px;word-break:break-word}
              a{display:inline-block;padding:14px 26px;border-radius:30px;background:#1e88e5;color:#fff;
                text-decoration:none;font-size:16px;font-weight:bold}
            </style></head><body><div>
              <h1>${if (online) "Can't load portal" else "Offline"}</h1>
              <p>${escape(reason)}</p>
              <a href="${escape(target)}">Retry</a>
            </div></body></html>
        """.trimIndent()
        webView.loadDataWithBaseURL(ERROR_BASE, html, "text/html", "utf-8", null)
        setReloadVisible(true)
    }

    // ---------- Reload ----------

    private fun reloadPortal() {
        val url = webView.url
        if (loadFailed || url == null || url.startsWith("data:") || url == ERROR_BASE) {
            webView.loadUrl(failedUrl ?: portalUrl)
        } else {
            webView.reload()
        }
        setReloadVisible(true)
    }

    private fun setReloadVisible(show: Boolean) {
        handler.removeCallbacks(hideReload)
        if (show) {
            reloadButton.visibility = View.VISIBLE
            reloadButton.animate().alpha(1f).setDuration(150).start()
            handler.postDelayed(hideReload, 3000)
        } else {
            reloadButton.animate().alpha(0f).setDuration(250)
                .withEndAction { reloadButton.visibility = View.GONE }.start()
        }
    }

    override fun dispatchTouchEvent(ev: MotionEvent): Boolean {
        when (ev.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                // Tap near the bottom edge reveals the reload button (does not consume the touch).
                if (root.height > 0 && ev.y > root.height * 0.82f) setReloadVisible(true)
            }
            MotionEvent.ACTION_POINTER_DOWN -> {
                // Two-finger tap = reload.
                if (ev.pointerCount == 2) {
                    reloadPortal()
                    val cancel = MotionEvent.obtain(ev).apply { action = MotionEvent.ACTION_CANCEL }
                    super.dispatchTouchEvent(cancel)
                    cancel.recycle()
                    return true
                }
            }
        }
        return super.dispatchTouchEvent(ev)
    }

    // ---------- Hardware buttons: long-press a stem button = reload ----------

    override fun onKeyDown(keyCode: Int, event: KeyEvent): Boolean {
        if (isStemKey(keyCode)) {
            event.startTracking()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }

    override fun onKeyLongPress(keyCode: Int, event: KeyEvent): Boolean {
        if (isStemKey(keyCode)) {
            reloadPortal()
            return true
        }
        return super.onKeyLongPress(keyCode, event)
    }

    override fun onKeyUp(keyCode: Int, event: KeyEvent): Boolean {
        if (isStemKey(keyCode)) {
            if (!event.isCanceled && event.isTracking) setReloadVisible(true) // short press: show button
            return true
        }
        return super.onKeyUp(keyCode, event)
    }

    private fun isStemKey(keyCode: Int) = keyCode == KeyEvent.KEYCODE_STEM_1 ||
        keyCode == KeyEvent.KEYCODE_STEM_2 || keyCode == KeyEvent.KEYCODE_STEM_3

    // ---------- Rotary bezel/crown -> scroll ----------

    override fun dispatchGenericMotionEvent(ev: MotionEvent): Boolean {
        if (ev.action == MotionEvent.ACTION_SCROLL && ev.isFromSource(InputDevice.SOURCE_ROTARY_ENCODER)) {
            val factor = ViewConfiguration.get(this).scaledVerticalScrollFactor
            val delta = -ev.getAxisValue(MotionEvent.AXIS_SCROLL) * factor
            webView.evaluateJavascript(
                "window.scrollBy({top:${delta.roundToInt()},behavior:'auto'});", null
            )
            return true
        }
        return super.dispatchGenericMotionEvent(ev)
    }

    // ---------- Back / swipe-to-dismiss ----------

    private fun setupBackHandling() {
        if (Build.VERSION.SDK_INT >= 33) {
            backCallback = OnBackInvokedCallback { handleBack() }
        }
    }

    /** Predictive-back pattern: intercept back only while the WebView has history. */
    private fun updateBackCallback() {
        if (Build.VERSION.SDK_INT < 33) return
        val cb = backCallback ?: return
        val want = webView.canGoBack()
        if (want && !backCallbackRegistered) {
            onBackInvokedDispatcher.registerOnBackInvokedCallback(OnBackInvokedDispatcher.PRIORITY_DEFAULT, cb)
            backCallbackRegistered = true
        } else if (!want && backCallbackRegistered) {
            onBackInvokedDispatcher.unregisterOnBackInvokedCallback(cb)
            backCallbackRegistered = false
        }
    }

    private fun handleBack() {
        if (webView.canGoBack()) webView.goBack() else finish()
        handler.post { updateBackCallback() }
    }

    @Deprecated("Used on API < 33")
    @Suppress("DEPRECATION")
    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    // ---------- Lifecycle ----------

    override fun onResume() {
        super.onResume()
        goImmersive()
        webView.onResume()
        webView.resumeTimers()
        if (loadFailed) webView.loadUrl(failedUrl ?: portalUrl)
    }

    override fun onPause() {
        webView.onPause()
        super.onPause()
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) {
            goImmersive()
            webView.requestFocus()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)
        root.removeView(webView)
        webView.destroy()
        super.onDestroy()
    }

    // ---------- Helpers ----------

    private fun goImmersive() {
        window.setDecorFitsSystemWindows(false)
        window.insetsController?.let {
            it.hide(WindowInsets.Type.systemBars())
            it.systemBarsBehavior = WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
    }

    private fun isOnline(): Boolean {
        val cm = getSystemService(ConnectivityManager::class.java) ?: return false
        val caps = cm.getNetworkCapabilities(cm.activeNetwork) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).roundToInt()

    private fun escape(s: String) = s.replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace("\"", "&quot;")

    companion object {
        private const val ERROR_BASE = "about:portal-error"
    }
}
