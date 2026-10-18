package com.rbagent.os;

import android.app.Activity;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.LinearLayout;
import android.graphics.Color;

/**
 * Control Screen for RB Agent Android Companion.
 */
public class MainActivity extends Activity {
    private boolean isServiceRunning = false;
    private TextView statusTextView;
    private Button toggleButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(40, 60, 40, 40);
        layout.setBackgroundColor(Color.parseColor("#F8FAFC"));

        TextView title = new TextView(this);
        title.setText("RB Agent by Jarvis");
        title.setTextSize(22);
        title.setTextColor(Color.parseColor("#0F172A"));
        layout.addView(title);

        TextView owner = new TextView(this);
        owner.setText("Operator: Ram Binay Kumar Pandit");
        owner.setTextSize(14);
        owner.setTextColor(Color.parseColor("#64748B"));
        owner.setPadding(0, 8, 0, 40);
        layout.addView(owner);

        statusTextView = new TextView(this);
        statusTextView.setText("Status: Foreground Service Standby");
        statusTextView.setTextSize(16);
        statusTextView.setTextColor(Color.parseColor("#0284C7"));
        statusTextView.setPadding(0, 0, 0, 30);
        layout.addView(statusTextView);

        toggleButton = new Button(this);
        toggleButton.setText("Start Wake-Word Service");
        toggleButton.setBackgroundColor(Color.parseColor("#0EA5E9"));
        toggleButton.setTextColor(Color.WHITE);
        toggleButton.setOnClickListener(v -> toggleService());
        layout.addView(toggleButton);

        setContentView(layout);
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
            statusTextView.setText("Status: Listening for 'Hey RB' in Background");
            toggleButton.setText("Stop Wake-Word Service");
            toggleButton.setBackgroundColor(Color.parseColor("#EF4444"));
        } else {
            stopService(serviceIntent);
            isServiceRunning = false;
            statusTextView.setText("Status: Service Stopped");
            toggleButton.setText("Start Wake-Word Service");
            toggleButton.setBackgroundColor(Color.parseColor("#0EA5E9"));
        }
    }
}
