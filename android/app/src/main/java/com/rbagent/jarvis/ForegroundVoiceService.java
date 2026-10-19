package com.rbagent.jarvis;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * Foreground Voice Service for RB Agent by Jarvis.
 * Maintains background wake-word listening ("Hey RB")
 * and relays audio transcript to Termux localhost server http://127.0.0.1:8765/api/voice/process.
 *
 * Hardened for Android 12+ (PendingIntent mutability) and Android 14+ (FGS microphone type safety).
 */
public class ForegroundVoiceService extends Service {
    private static final String TAG = "HeyRB_VoiceService";
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
        try {
            Notification notification = buildForegroundNotification();
            if (Build.VERSION.SDK_INT >= 34) {
                // Android 14+ requires explicit foregroundServiceType
                startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE);
            } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE);
            } else {
                startForeground(NOTIFICATION_ID, notification);
            }
            Log.i(TAG, "RB Agent by Jarvis Foreground Voice Service running with notification.");
            return START_STICKY;
        } catch (SecurityException se) {
            Log.w(TAG, "Microphone permission not granted yet for ForegroundVoiceService: " + se.getMessage());
            stopSelf();
            return START_NOT_STICKY;
        } catch (Throwable t) {
            Log.e(TAG, "Unexpected error starting ForegroundVoiceService: " + t.getMessage(), t);
            stopSelf();
            return START_NOT_STICKY;
        }
    }

    private void createNotificationChannel() {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "RB Agent Voice Service",
                    NotificationManager.IMPORTANCE_LOW
                );
                channel.setDescription("Maintains background wake-word listening for RB Agent by Jarvis");
                NotificationManager manager = getSystemService(NotificationManager.class);
                if (manager != null) {
                    manager.createNotificationChannel(channel);
                }
            }
        } catch (Throwable t) {
            Log.e(TAG, "Failed to create notification channel", t);
        }
    }

    private Notification buildForegroundNotification() {
        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder = new Notification.Builder(this, CHANNEL_ID);
        } else {
            builder = new Notification.Builder(this);
        }

        // Deep-link intent to restore MainActivity upon tapping notification
        Intent notificationIntent = new Intent(this, MainActivity.class);
        notificationIntent.setAction(Intent.ACTION_MAIN);
        notificationIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        notificationIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);

        // Android 12+ (API 31+) explicitly requires FLAG_IMMUTABLE or FLAG_MUTABLE
        int pendingIntentFlags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            pendingIntentFlags |= PendingIntent.FLAG_IMMUTABLE;
        }
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, notificationIntent, pendingIntentFlags);

        return builder
            .setContentTitle("RB Agent by Jarvis Active")
            .setContentText("Listening for 'Hey RB' • Termux Bridge Online")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .build();
    }

    /**
     * Relays captured transcript to local RB Agent backend without blocking main thread.
     */
    public void dispatchTranscriptToBackend(final String transcript) {
        if (transcript == null || transcript.trim().isEmpty()) return;
        new Thread(() -> {
            HttpURLConnection conn = null;
            try {
                URL url = new URL(SERVER_URL);
                conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json; utf-8");
                conn.setConnectTimeout(3000);
                conn.setReadTimeout(3000);
                conn.setDoOutput(true);

                String jsonInputString = "{\"transcript\": \"" + transcript.replace("\"", "\\\"") + "\"}";

                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = jsonInputString.getBytes("utf-8");
                    os.write(input, 0, input.length);
                }

                int code = conn.getResponseCode();
                Log.d(TAG, "Transcript relayed to backend. Response Code: " + code);
            } catch (Throwable e) {
                Log.d(TAG, "Local voice bridge standby: " + e.getMessage());
            } finally {
                if (conn != null) {
                    try {
                        conn.disconnect();
                    } catch (Throwable ignored) {
                        // Non-fatal connection close suppression
                    }
                }
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
        Log.i(TAG, "RB Agent by Jarvis Voice Service stopped cleanly.");
    }
}
