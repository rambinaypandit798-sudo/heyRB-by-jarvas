package com.rbagent.jarvis;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.speech.tts.TextToSpeech;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import java.util.Locale;

/**
 * RB Agent by Jarvis — Native Android Companion & Pure Lovable UI Host.
 * Operator: Ram Binay Kumar Pandit
 *
 * Fully hardened for zero-crash startup, thread-safe JavaScriptInterface,
 * and Android 12/13/14 permission & lifecycle safety.
 */
public class MainActivity extends AppCompatActivity {
    private static final String TAG = "HeyRB_MainActivity";
    private static final String DEFAULT_LOCAL_URL = "http://127.0.0.1:8080";
    private static final int PERMISSION_REQUEST_CODE = 8765;

    private boolean isServiceRunning = false;
    private WebView webView;
    private ProgressBar progressBar;
    private LinearLayout errorLayout;
    private AndroidBridge bridge;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        try {
            // Immersive Dark Theme Window Settings
            Window window = getWindow();
            if (window != null) {
                window.clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS);
                window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
                window.setStatusBarColor(Color.parseColor("#0B0F19"));
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    window.setNavigationBarColor(Color.parseColor("#0B0F19"));
                }
            }
        } catch (Throwable t) {
            Log.w(TAG, "Window styling warning:", t);
        }

        try {
            // Clean root container — Zero injected headers or control buttons
            LinearLayout root = new LinearLayout(this);
            root.setOrientation(LinearLayout.VERTICAL);
            root.setBackgroundColor(Color.parseColor("#0B0F19"));

            // Progress bar for subtle web loading feedback
            progressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
            progressBar.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 4));
            progressBar.setMax(100);
            progressBar.setVisibility(View.GONE);
            root.addView(progressBar);

            // Error / Offline Retry Layout (Shown only if dev server is unreachable)
            errorLayout = new LinearLayout(this);
            errorLayout.setOrientation(LinearLayout.VERTICAL);
            errorLayout.setGravity(Gravity.CENTER);
            errorLayout.setPadding(40, 60, 40, 60);
            errorLayout.setVisibility(View.GONE);

            TextView errorTitle = new TextView(this);
            errorTitle.setText("Termux Dev Server Standby");
            errorTitle.setTextSize(18);
            errorTitle.setTextColor(Color.parseColor("#E2E8F0"));
            errorTitle.setGravity(Gravity.CENTER);
            errorLayout.addView(errorTitle);

            TextView errorDesc = new TextView(this);
            errorDesc.setText("Connect to Termux localhost (http://127.0.0.1:8080).\nEnsure 'npm run dev' is running.");
            errorDesc.setTextSize(13);
            errorDesc.setTextColor(Color.parseColor("#94A3B8"));
            errorDesc.setGravity(Gravity.CENTER);
            errorDesc.setPadding(0, 16, 0, 24);
            errorLayout.addView(errorDesc);

            Button retryButton = new Button(this);
            retryButton.setText("Reconnect to RB Agent");
            retryButton.setTextColor(Color.WHITE);
            retryButton.setBackgroundColor(Color.parseColor("#0EA5E9"));
            retryButton.setOnClickListener(v -> {
                if (errorLayout != null) errorLayout.setVisibility(View.GONE);
                if (webView != null) {
                    webView.setVisibility(View.VISIBLE);
                    webView.loadUrl(DEFAULT_LOCAL_URL);
                }
            });
            errorLayout.addView(retryButton);
            root.addView(errorLayout);

            // Pristine Edge-to-Edge Pure Lovable UI WebView Container
            webView = new WebView(this);
            LinearLayout.LayoutParams webParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0f);
            webView.setLayoutParams(webParams);
            webView.setBackgroundColor(Color.parseColor("#0B0F19"));

            WebSettings settings = webView.getSettings();
            settings.setJavaScriptEnabled(true);
            settings.setDomStorageEnabled(true);
            settings.setDatabaseEnabled(true);
            settings.setAllowFileAccess(true);
            settings.setMediaPlaybackRequiresUserGesture(false);
            settings.setCacheMode(WebSettings.LOAD_DEFAULT);

            // Initialize Thread-Safe Android Bridge for JS Execution
            bridge = new AndroidBridge(this);
            webView.addJavascriptInterface(bridge, "AndroidBridge");

            webView.setWebChromeClient(new WebChromeClient() {
                @Override
                public void onProgressChanged(WebView view, int newProgress) {
                    try {
                        if (progressBar != null) {
                            if (newProgress < 100) {
                                progressBar.setVisibility(View.VISIBLE);
                                progressBar.setProgress(newProgress);
                            } else {
                                progressBar.setVisibility(View.GONE);
                            }
                        }
                    } catch (Throwable ignored) {
                        // Non-fatal progress update suppression
                    }
                }

                @Override
                public void onPermissionRequest(PermissionRequest request) {
                    try {
                        // Grant web microphone/camera permissions requested by Lovable UI
                        if (request != null) {
                            request.grant(request.getResources());
                        }
                    } catch (Throwable t) {
                        Log.w(TAG, "Permission request error", t);
                    }
                }
            });

            webView.setWebViewClient(new WebViewClient() {
                @Override
                public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                    try {
                        if (request != null) {
                            Uri uri = request.getUrl();
                            String scheme = uri != null ? uri.getScheme() : null;
                            if (scheme != null && !scheme.equals("http") && !scheme.equals("https")) {
                                Intent intent = new Intent(Intent.ACTION_VIEW, uri);
                                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                                startActivity(intent);
                                return true;
                            }
                        }
                    } catch (Throwable t) {
                        Log.e(TAG, "Failed to launch intent for uri", t);
                    }
                    return false;
                }

                @Override
                public void onPageStarted(WebView view, String url, Bitmap favicon) {
                    try {
                        if (errorLayout != null) errorLayout.setVisibility(View.GONE);
                    } catch (Throwable ignored) {
                        // Non-fatal page start suppression
                    }
                }

                @Override
                public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                    try {
                        if (request != null && request.isForMainFrame()) {
                            if (webView != null) webView.setVisibility(View.GONE);
                            if (errorLayout != null) errorLayout.setVisibility(View.VISIBLE);
                        }
                    } catch (Throwable ignored) {
                        // Non-fatal network error layout suppression
                    }
                }
            });

            root.addView(webView);
            setContentView(root);

            // Load Pure Lovable Web Application
            webView.loadUrl(DEFAULT_LOCAL_URL);

            // Request runtime permissions safely and start background service
            checkPermissionsAndStartService();

        } catch (Throwable t) {
            Log.e(TAG, "Fatal error in onCreate prevented: " + t.getMessage(), t);
        }
    }

    private void checkPermissionsAndStartService() {
        try {
            boolean audioGranted = ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED;
            boolean notifGranted = true;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                notifGranted = ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED;
            }

            if (!audioGranted || !notifGranted) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    ActivityCompat.requestPermissions(this, new String[]{
                        Manifest.permission.RECORD_AUDIO,
                        Manifest.permission.POST_NOTIFICATIONS
                    }, PERMISSION_REQUEST_CODE);
                } else {
                    ActivityCompat.requestPermissions(this, new String[]{
                        Manifest.permission.RECORD_AUDIO
                    }, PERMISSION_REQUEST_CODE);
                }
            } else {
                startWakeWordServiceSilently();
            }
        } catch (Throwable t) {
            Log.w(TAG, "Permission check error:", t);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            try {
                boolean hasAudio = false;
                for (int i = 0; i < permissions.length; i++) {
                    if (Manifest.permission.RECORD_AUDIO.equals(permissions[i]) && grantResults[i] == PackageManager.PERMISSION_GRANTED) {
                        hasAudio = true;
                    }
                }
                if (hasAudio) {
                    startWakeWordServiceSilently();
                }
            } catch (Throwable t) {
                Log.w(TAG, "Error handling permission result:", t);
            }
        }
    }

    private void startWakeWordServiceSilently() {
        try {
            Intent serviceIntent = new Intent(this, ForegroundVoiceService.class);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent);
            } else {
                startService(serviceIntent);
            }
            isServiceRunning = true;
            Log.i(TAG, "Wake-word background service active.");
        } catch (Throwable t) {
            Log.w(TAG, "Could not start background wake-word service:", t);
        }
    }

    @Override
    protected void onDestroy() {
        try {
            if (bridge != null) {
                bridge.cleanup();
            }
            if (webView != null) {
                webView.destroy();
            }
        } catch (Throwable t) {
            Log.e(TAG, "onDestroy cleanup error:", t);
        }
        super.onDestroy();
    }

    @Override
    public void onBackPressed() {
        try {
            if (webView != null && webView.canGoBack()) {
                webView.goBack();
                return;
            }
        } catch (Throwable ignored) {
            // Non-fatal back navigation suppression
        }
        super.onBackPressed();
    }

    /**
     * Deep Native Android Bridge for pure Lovable web integration.
     * Fully thread-safe: all intent dispatch operations are routed through
     * activity.runOnUiThread with defensive null checks and Throwable catch blocks.
     */
    public class AndroidBridge {
        private final Activity activity;
        private TextToSpeech tts;
        private volatile boolean ttsReady = false;
        private final Object ttsLock = new Object();

        public AndroidBridge(Activity activity) {
            this.activity = activity;
            try {
                this.tts = new TextToSpeech(activity.getApplicationContext(), status -> {
                    synchronized (ttsLock) {
                        try {
                            if (status == TextToSpeech.SUCCESS && tts != null) {
                                tts.setLanguage(new Locale("hi", "IN"));
                                tts.setPitch(1.0f);
                                tts.setSpeechRate(1.0f);
                                ttsReady = true;
                                Log.i(TAG, "Android TTS initialized successfully.");
                            }
                        } catch (Throwable t) {
                            Log.w(TAG, "TTS init language set error:", t);
                        }
                    }
                });
            } catch (Throwable t) {
                Log.w(TAG, "TextToSpeech constructor warning:", t);
            }
        }

        @JavascriptInterface
        public boolean isNative() {
            return true;
        }

        @JavascriptInterface
        public boolean launchApp(final String packageName, final String uriString, final String action) {
            try {
                if (activity == null || activity.isFinishing()) return false;

                Intent intent = null;
                if (uriString != null && !uriString.trim().isEmpty()) {
                    intent = new Intent(Intent.ACTION_VIEW, Uri.parse(uriString.trim()));
                } else if (action != null && !action.trim().isEmpty()) {
                    intent = new Intent(action.trim());
                } else if (packageName != null && !packageName.trim().isEmpty()) {
                    intent = activity.getPackageManager().getLaunchIntentForPackage(packageName.trim());
                }

                if (intent != null) {
                    if (packageName != null && !packageName.trim().isEmpty() && uriString != null && !uriString.trim().isEmpty()) {
                        intent.setPackage(packageName.trim());
                    }
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    final Intent finalIntent = intent;
                    activity.runOnUiThread(() -> {
                        try {
                            activity.startActivity(finalIntent);
                        } catch (Throwable t) {
                            Log.e(TAG, "startActivity failed: " + t.getMessage());
                        }
                    });
                    return true;
                }
            } catch (Throwable t) {
                Log.e(TAG, "Error in launchApp: " + packageName + " / " + uriString, t);
            }
            return false;
        }

        @JavascriptInterface
        public boolean openYouTube(final String query) {
            try {
                if (activity == null || activity.isFinishing()) return false;

                activity.runOnUiThread(() -> {
                    try {
                        Intent intent;
                        if (query != null && !query.trim().isEmpty()) {
                            String uri = "vnd.youtube://results?search_query=" + Uri.encode(query.trim());
                            intent = new Intent(Intent.ACTION_VIEW, Uri.parse(uri));
                            intent.setPackage("com.google.android.youtube");
                        } else {
                            intent = activity.getPackageManager().getLaunchIntentForPackage("com.google.android.youtube");
                            if (intent == null) {
                                intent = new Intent(Intent.ACTION_VIEW, Uri.parse("vnd.youtube://"));
                            }
                        }
                        if (intent != null) {
                            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                            try {
                                activity.startActivity(intent);
                                return;
                            } catch (Throwable appNotFound) {
                                Log.w(TAG, "YouTube app launch failed, falling back to browser", appNotFound);
                            }
                        }

                        // Robust Web Fallback if YouTube app is missing or disabled
                        String webUrl = (query != null && !query.trim().isEmpty())
                            ? "https://www.youtube.com/results?search_query=" + Uri.encode(query.trim())
                            : "https://www.youtube.com";
                        Intent webIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(webUrl));
                        webIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        activity.startActivity(webIntent);
                    } catch (Throwable t) {
                        Log.e(TAG, "Error opening YouTube", t);
                    }
                });
                return true;
            } catch (Throwable t) {
                Log.e(TAG, "openYouTube outer error", t);
            }
            return false;
        }

        @JavascriptInterface
        public boolean openSettings(final String type) {
            try {
                if (activity == null || activity.isFinishing()) return false;

                activity.runOnUiThread(() -> {
                    try {
                        Intent intent;
                        if ("wifi".equalsIgnoreCase(type)) {
                            intent = new Intent(Settings.ACTION_WIFI_SETTINGS);
                        } else if ("bluetooth".equalsIgnoreCase(type)) {
                            intent = new Intent(Settings.ACTION_BLUETOOTH_SETTINGS);
                        } else if ("display".equalsIgnoreCase(type)) {
                            intent = new Intent(Settings.ACTION_DISPLAY_SETTINGS);
                        } else if ("sound".equalsIgnoreCase(type)) {
                            intent = new Intent(Settings.ACTION_SOUND_SETTINGS);
                        } else {
                            intent = new Intent(Settings.ACTION_SETTINGS);
                        }
                        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        activity.startActivity(intent);
                    } catch (Throwable t) {
                        Log.e(TAG, "Error opening Settings: " + type, t);
                    }
                });
                return true;
            } catch (Throwable t) {
                Log.e(TAG, "openSettings outer error", t);
            }
            return false;
        }

        @JavascriptInterface
        public void speakConfirmation(final String confirmationText) {
            final String text = (confirmationText != null && !confirmationText.trim().isEmpty())
                ? confirmationText
                : "हाँ, यह कर दिया है";
            synchronized (ttsLock) {
                try {
                    if (ttsReady && tts != null) {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "RB_AGENT_CONFIRMATION");
                        } else {
                            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null);
                        }
                    } else {
                        Log.w(TAG, "TTS not ready yet for confirmation: " + text);
                    }
                } catch (Throwable t) {
                    Log.e(TAG, "TTS speak error", t);
                }
            }
        }

        @JavascriptInterface
        public boolean isWakeWordActive() {
            return isServiceRunning;
        }

        @JavascriptInterface
        public void startWakeWordService() {
            activity.runOnUiThread(() -> startWakeWordServiceSilently());
        }

        public void cleanup() {
            synchronized (ttsLock) {
                try {
                    if (tts != null) {
                        tts.stop();
                        tts.shutdown();
                        tts = null;
                        ttsReady = false;
                    }
                } catch (Throwable t) {
                    Log.e(TAG, "Error during TTS cleanup", t);
                }
            }
        }
    }
}
