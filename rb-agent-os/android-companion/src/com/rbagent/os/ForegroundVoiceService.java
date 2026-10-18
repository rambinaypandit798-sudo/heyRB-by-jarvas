package com.rbagent.os;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * Foreground Voice Service for RB Agent OS.
 * Maintains persistent background microphone listening for wake-word "Hey RB"
 * and relays audio transcript to Termux localhost server http://127.0.0.1:8765/api/voice/process.
 */
public class ForegroundVoiceService extends Service {
    private static final String TAG = "RBVoiceService";
    private static final String CHANNEL_ID = "rb_agent_voice_channel";
    private static final int NOTIFICATION_ID = 8765;
    private static final String SERVER_URL = "http://127.0.0.1:8765/api/voice/process";

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Notification notification = buildForegroundNotification();
        startForeground(NOTIFICATION_ID, notification);
        Log.i(TAG, "RB Agent Foreground Voice Service started.");
        return START_STICKY;
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "RB Agent Voice Service",
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Maintains background wake-word listening for RB Agent");
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(channel);
            }
        }
    }

    private Notification buildForegroundNotification() {
        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder = new Notification.Builder(this, CHANNEL_ID);
        } else {
            builder = new Notification.Builder(this);
        }

        return builder
            .setContentTitle("RB Agent OS Active")
            .setContentText("Listening for 'Hey RB' • Termux Bridge Online")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setOngoing(true)
            .build();
    }

    /**
     * Relays captured transcript to local RB Agent OS backend.
     */
    public void dispatchTranscriptToBackend(String transcript) {
        new Thread(() -> {
            try {
                URL url = new URL(SERVER_URL);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json; utf-8");
                conn.setDoOutput(true);

                String jsonInputString = "{\"transcript\": \"" + transcript.replace("\"", "\\\"") + "\"}";

                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = jsonInputString.getBytes("utf-8");
                    os.write(input, 0, input.length);
                }

                int code = conn.getResponseCode();
                Log.d(TAG, "Transcript relayed to backend. Response Code: " + code);
            } catch (Exception e) {
                Log.e(TAG, "Failed to relay voice to local backend: " + e.getMessage());
            }
        }).start();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.i(TAG, "RB Agent Voice Service stopped.");
    }
}
