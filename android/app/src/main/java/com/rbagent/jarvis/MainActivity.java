package com.rbagent.jarvis;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
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
import java.util.Locale;

/**
 * RB Agent by Jarvis — Native Android Companion & Pure Lovable UI Host.
 * Operator: Ram Binay Kumar Pandit
 */
public class MainActivity extends AppCompatActivity {
    private static final String TAG = "HeyRB_MainActivity";
    private static final String DEFAULT_LOCAL_URL = "http://127.0.0.1:8080";

    private boolean isServiceRunning = false;
    private WebView webView;
    private ProgressBar progressBar;
    private LinearLayout errorLayout;
    private AndroidBridge bridge;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Immersive Dark Theme Window Settings
        Window window = getWindow();
        window.clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS);
        window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        window.setStatusBarColor(Color.parseColor("#0B0F19"));
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            window.setNavigationBarColor(Color.parseColor("#0B0F19"));
        }

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
            errorLayout.setVisibility(View.GONE);
            webView.setVisibility(View.VISIBLE);
            webView.loadUrl(DEFAULT_LOCAL_URL);
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

        // Initialize Android Bridge for Deep System & Intent Integration
        bridge = new AndroidBridge(this);
        webView.addJavascriptInterface(bridge, "AndroidBridge");

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                if (newProgress < 100) {
                    progressBar.setVisibility(View.VISIBLE);
                    progressBar.setProgress(newProgress);
                } else {
                    progressBar.setVisibility(View.GONE);
                }
            }
        });

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                String scheme = uri.getScheme();
                if (scheme != null && !scheme.equals("http") && !scheme.equals("https")) {
                    try {
                        Intent intent = new Intent(Intent.ACTION_VIEW, uri);
                        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        startActivity(intent);
                        return true;
                    } catch (Exception e) {
                        Log.e(TAG, "Failed to launch intent for uri: " + uri, e);
                    }
                }
                return false;
            }

            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                errorLayout.setVisibility(View.GONE);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    webView.setVisibility(View.GONE);
                    errorLayout.setVisibility(View.VISIBLE);
                }
            }
        });

        root.addView(webView);
        setContentView(root);

        // Load Pure Lovable UI
        webView.loadUrl(DEFAULT_LOCAL_URL);

        // Start background wake-word service seamlessly without native UI intrusion
        startWakeWordServiceSilently();
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
        } catch (Exception e) {
            Log.w(TAG, "Could not start background wake-word service:", e);
        }
    }

    @Override
    protected void onDestroy() {
        if (bridge != null) {
            bridge.cleanup();
        }
        super.onDestroy();
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    /**
     * Deep Native Android Bridge for pure Lovable web integration.
     * Exposes app launch, device settings, and voice confirmation to JS.
     */
    public class AndroidBridge {
        private final Activity activity;
        private TextToSpeech tts;
        private boolean ttsReady = false;

        public AndroidBridge(Activity activity) {
            this.activity = activity;
            this.tts = new TextToSpeech(activity.getApplicationContext(), status -> {
                if (status == TextToSpeech.SUCCESS && tts != null) {
                    tts.setLanguage(new Locale("hi", "IN"));
                    tts.setPitch(1.0f);
                    tts.setSpeechRate(1.0f);
                    ttsReady = true;
                    Log.i(TAG, "Android TTS initialized successfully.");
                }
            });
        }

        @JavascriptInterface
        public boolean isNative() {
            return true;
        }

        @JavascriptInterface
        public boolean launchApp(String packageName, String uriString, String action) {
            try {
                Intent intent;
                if (uriString != null && !uriString.trim().isEmpty()) {
                    intent = new Intent(Intent.ACTION_VIEW, Uri.parse(uriString));
                } else if (action != null && !action.trim().isEmpty()) {
                    intent = new Intent(action);
                } else if (packageName != null && !packageName.trim().isEmpty()) {
                    intent = activity.getPackageManager().getLaunchIntentForPackage(packageName);
                } else {
                    return false;
                }

                if (intent != null) {
                    if (packageName != null && !packageName.trim().isEmpty() && uriString != null && !uriString.trim().isEmpty()) {
                        intent.setPackage(packageName);
                    }
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    activity.startActivity(intent);
                    return true;
                }
            } catch (Exception e) {
                Log.e(TAG, "Error in launchApp: " + packageName + " / " + uriString, e);
            }
            return false;
        }

        @JavascriptInterface
        public boolean openYouTube(String query) {
            try {
                Intent intent;
                if (query != null && !query.trim().isEmpty()) {
                    String uri = "vnd.youtube://results?search_query=" + Uri.encode(query);
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
                    activity.startActivity(intent);
                    return true;
                }
            } catch (Exception e) {
                Log.e(TAG, "Error opening YouTube", e);
            }
            return false;
        }

        @JavascriptInterface
        public boolean openSettings(String type) {
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
                return true;
            } catch (Exception e) {
                Log.e(TAG, "Error opening Settings: " + type, e);
            }
            return false;
        }

        @JavascriptInterface
        public void speakConfirmation(String confirmationText) {
            final String text = (confirmationText != null && !confirmationText.trim().isEmpty())
                ? confirmationText
                : "हाँ, यह कर दिया है";
            if (ttsReady && tts != null) {
                tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "RB_AGENT_CONFIRMATION");
            } else {
                Log.w(TAG, "TTS not ready for confirmation: " + text);
            }
        }

        @JavascriptInterface
        public boolean isWakeWordActive() {
            return isServiceRunning;
        }

        public void cleanup() {
            if (tts != null) {
                tts.stop();
                tts.shutdown();
                ttsReady = false;
            }
        }
    }
}
