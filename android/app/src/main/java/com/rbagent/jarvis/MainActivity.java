package com.rbagent.jarvis;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
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

/**
 * RB Agent by Jarvis — Native Android Companion & Dashboard.
 * Operator: Ram Binay Kumar Pandit
 */
public class MainActivity extends AppCompatActivity {
    private static final String TAG = "HeyRB_MainActivity";
    private static final String DEFAULT_LOCAL_URL = "http://127.0.0.1:8080";

    private boolean isServiceRunning = false;
    private TextView statusTextView;
    private Button toggleButton;
    private WebView webView;
    private ProgressBar progressBar;
    private LinearLayout errorLayout;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.parseColor("#0B0F19"));

        // Top Control Header
        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.VERTICAL);
        header.setPadding(32, 24, 32, 24);
        header.setBackgroundColor(Color.parseColor("#111827"));

        TextView title = new TextView(this);
        title.setText("RB Agent by Jarvis");
        title.setTextSize(20);
        title.setTextColor(Color.parseColor("#38BDF8"));
        title.setTypeface(null, android.graphics.Typeface.BOLD);
        header.addView(title);

        TextView owner = new TextView(this);
        owner.setText("Operator: Ram Binay Kumar Pandit • Android Bridge Active");
        owner.setTextSize(12);
        owner.setTextColor(Color.parseColor("#94A3B8"));
        owner.setPadding(0, 4, 0, 16);
        header.addView(owner);

        LinearLayout controlsRow = new LinearLayout(this);
        controlsRow.setOrientation(LinearLayout.HORIZONTAL);
        controlsRow.setGravity(Gravity.CENTER_VERTICAL);

        statusTextView = new TextView(this);
        statusTextView.setText("● Standby");
        statusTextView.setTextSize(13);
        statusTextView.setTextColor(Color.parseColor("#38BDF8"));
        LinearLayout.LayoutParams statusParams = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        statusTextView.setLayoutParams(statusParams);
        controlsRow.addView(statusTextView);

        toggleButton = new Button(this);
        toggleButton.setText("Start Wake-Word Service");
        toggleButton.setTextSize(12);
        toggleButton.setTextColor(Color.WHITE);
        toggleButton.setBackgroundColor(Color.parseColor("#0EA5E9"));
        toggleButton.setOnClickListener(v -> toggleService());
        controlsRow.addView(toggleButton);

        header.addView(controlsRow);
        root.addView(header);

        // Progress bar for Web loading
        progressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progressBar.setLayoutParams(new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, 6));
        progressBar.setMax(100);
        progressBar.setVisibility(View.GONE);
        root.addView(progressBar);

        // Error / Offline Retry Layout
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

        // Web View Container
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

        webView.loadUrl(DEFAULT_LOCAL_URL);
    }

    private void toggleService() {
        Intent serviceIntent = new Intent(this, ForegroundVoiceService.class);
        if (!isServiceRunning) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent);
            } else {
                startService(serviceIntent);
            }
            isServiceRunning = true;
            statusTextView.setText("● Listening ('Hey RB')");
            statusTextView.setTextColor(Color.parseColor("#22C55E"));
            toggleButton.setText("Stop Voice Service");
            toggleButton.setBackgroundColor(Color.parseColor("#EF4444"));
        } else {
            stopService(serviceIntent);
            isServiceRunning = false;
            statusTextView.setText("● Standby");
            statusTextView.setTextColor(Color.parseColor("#38BDF8"));
            toggleButton.setText("Start Wake-Word Service");
            toggleButton.setBackgroundColor(Color.parseColor("#0EA5E9"));
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
