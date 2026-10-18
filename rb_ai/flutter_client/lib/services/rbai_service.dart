import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/message.dart';

enum AssistantState { idle, listening, thinking, speaking }

class RBAIService extends ChangeNotifier {
  String baseUrl = "http://127.0.0.1:8765";
  AssistantState _state = AssistantState.idle;
  bool isConnected = false;
  Map<String, dynamic> deviceStatus = {};

  // Dynamic User Name
  String _userName = "Ram Binay kumar Pandit";
  String get userName => _userName;

  // Persistent Settings
  String voiceAccent = "hi-IN";
  double voicePitch = 1.0;
  double voiceRate = 0.5;
  bool wakePhraseEnabled = true;
  bool callAnnouncementEnabled = true;

  // Turn-Taking & Subtitles
  String _currentSubtitle = "RB Agent ready • Turn-taking enabled";
  String get currentSubtitle => _currentSubtitle;
  bool isTtsPaused = false;
  int _lastSpokenWordIndex = 0;

  final List<ChatMessage> _messages = [];
  List<ChatMessage> get messages => List.unmodifiable(_messages);
  AssistantState get state => _state;

  // Speech & Voice
  late stt.SpeechToText _speech;
  late FlutterTts _tts;
  bool _speechEnabled = false;
  String _lastHeardWords = "";

  RBAIService() {
    _speech = stt.SpeechToText();
    _tts = FlutterTts();
    _initService();
  }

  Future<void> _initService() async {
    await _loadLocalPreferences();
    await _initVoice();
    await checkConnection();
    // Auto speak initial greeting on startup
    autoSpeakGreeting();
  }

  Future<void> _loadLocalPreferences() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _userName = prefs.getString("user_name") ?? "Ram Binay kumar Pandit";
      voiceAccent = prefs.getString("voice_accent") ?? "hi-IN";
      voicePitch = prefs.getDouble("voice_pitch") ?? 1.0;
      voiceRate = prefs.getDouble("voice_rate") ?? 0.5;
      wakePhraseEnabled = prefs.getBool("wake_phrase_enabled") ?? true;
      callAnnouncementEnabled = prefs.getBool("call_announcement_enabled") ?? true;
      baseUrl = prefs.getString("base_url") ?? "http://127.0.0.1:8765";
      notifyListeners();
    } catch (e) {
      debugPrint("[RBAIService Preferences Error]: $e");
    }
  }

  Future<void> setUserName(String name) async {
    if (name.trim().isEmpty) return;
    _userName = name.trim();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString("user_name", _userName);
      await http.post(
        Uri.parse('$baseUrl/api/user'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({"user_name": _userName}),
      );
    } catch (_) {}
    notifyListeners();
  }

  void setBaseUrl(String url) async {
    baseUrl = url;
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString("base_url", baseUrl);
    } catch (_) {}
    checkConnection();
    notifyListeners();
  }

  void _setState(AssistantState newState) {
    _state = newState;
    notifyListeners();
  }

  Future<void> _initVoice() async {
    try {
      _speechEnabled = await _speech.initialize(
        onError: (err) => debugPrint('[RB.AI STT Error]: $err'),
        onStatus: (status) {
          debugPrint('[RB.AI STT Status]: $status');
          if (status == 'notListening' && _state == AssistantState.listening) {
            // If background wake-word enabled, restart listening
            if (wakePhraseEnabled) {
              startListeningForWakeWord();
            }
          }
        },
      );

      await _tts.setLanguage(voiceAccent);
      await _tts.setPitch(voicePitch);
      await _tts.setSpeechRate(voiceRate);

      // Track progress for pause/resume word offset
      _tts.setProgressHandler((text, start, end, word) {
        _lastSpokenWordIndex = start;
        _currentSubtitle = "Speaking: $word";
        notifyListeners();
      });

      _tts.setCompletionHandler(() {
        _setState(AssistantState.idle);
        _currentSubtitle = "RB Agent finished speaking. Strict listening mode active.";
        notifyListeners();
        // Strict Turn-Taking rule: Immediately start listening, never interrupt proactively
        startListeningDirectly();
      });

      _tts.setCancelHandler(() {
        _setState(AssistantState.idle);
        notifyListeners();
      });
    } catch (e) {
      debugPrint('[RB.AI Voice Init]: $e');
    }
  }

  Future<bool> checkConnection() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/status')).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        isConnected = true;
        deviceStatus = json.decode(res.body);
        if (deviceStatus["user_name"] != null && deviceStatus["user_name"].toString().isNotEmpty) {
          _userName = deviceStatus["user_name"];
        }
        notifyListeners();
        return true;
      }
    } catch (_) {
      isConnected = false;
      notifyListeners();
    }
    return false;
  }

  // Auto-Speak Greeting
  Future<void> autoSpeakGreeting() async {
    final greeting = "नमस्ते, $_userName आज आपका क्या प्लान है";
    _currentSubtitle = greeting;
    notifyListeners();
    await speakText(greeting);
  }

  // Voice TTS with Pause / Resume Word Offset Fix
  Future<void> speakText(String text) async {
    if (text.isEmpty) return;
    _setState(AssistantState.speaking);
    _currentSubtitle = text;
    isTtsPaused = false;
    notifyListeners();

    // Clean text of markdown symbols
    final clean = text.replaceAll(RegExp(r'[*#`_\[\]]'), '');
    await _tts.speak(clean);
  }

  Future<void> pauseTts() async {
    if (_state == AssistantState.speaking) {
      await _tts.stop();
      isTtsPaused = true;
      _currentSubtitle = "Playback paused at character $_lastSpokenWordIndex";
      _setState(AssistantState.idle);
      notifyListeners();
    }
  }

  // Wake Phrase "Hey RB" Continuous Background Listener
  void startListeningForWakeWord() async {
    if (!_speechEnabled) await _initVoice();
    if (!wakePhraseEnabled) return;

    _setState(AssistantState.listening);
    _currentSubtitle = "Listening for 'Hey RB' or speech...";
    notifyListeners();

    await _speech.listen(
      onResult: (result) {
        _lastHeardWords = result.recognizedWords;
        _currentSubtitle = "Heard: $_lastHeardWords";
        notifyListeners();

        final lower = _lastHeardWords.toLowerCase();
        if (lower.contains("hey rb") || lower.contains("rb")) {
          debugPrint("Wake word detected in: $_lastHeardWords");
          _speech.stop();
          sendPrompt(_lastHeardWords, isVoice: true);
        }
      },
      listenFor: const Duration(seconds: 40),
      pauseFor: const Duration(seconds: 5),
      listenOptions: stt.SpeechListenOptions(partialResults: true),
    );
  }

  // Strict Turn-Taking Direct Speech Input
  void startListeningDirectly() async {
    if (!_speechEnabled) await _initVoice();

    _setState(AssistantState.listening);
    _currentSubtitle = "Listening for user response...";
    notifyListeners();

    await _speech.listen(
      onResult: (result) {
        _lastHeardWords = result.recognizedWords;
        _currentSubtitle = "User: $_lastHeardWords";
        notifyListeners();

        if (result.finalResult && _lastHeardWords.trim().isNotEmpty) {
          _speech.stop();
          sendPrompt(_lastHeardWords, isVoice: true);
        }
      },
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 4),
      listenOptions: stt.SpeechListenOptions(partialResults: true),
    );
  }

  void stopListening() {
    _speech.stop();
    _setState(AssistantState.idle);
    _currentSubtitle = "Microphone stopped.";
    notifyListeners();
  }

  // Call Announcement Feature
  Future<void> announceIncomingCall(String callerName, {String phone = ""}) async {
    final speech = "$_userName, $callerName का फोन आया है";
    _currentSubtitle = "Incoming Call: $callerName";
    notifyListeners();

    try {
      await http.post(
        Uri.parse('$baseUrl/api/call_announcement'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({"caller_name": callerName, "phone": phone}),
      );
    } catch (_) {}

    await speakText(speech);
  }

  // Send Prompt with Memory & Gemini Routing
  Future<void> sendPrompt(String text, {Uint8List? imageBytes, bool isVoice = false}) async {
    if (text.isEmpty && imageBytes == null) return;

    _messages.add(ChatMessage(
      text: text,
      isUser: true,
      imageBytes: imageBytes,
    ));
    _setState(AssistantState.thinking);
    _currentSubtitle = "Thinking & orchestrating...";
    notifyListeners();

    try {
      final payload = {
        "text": text,
        "is_voice": isVoice,
        "image": imageBytes != null ? base64Encode(imageBytes) : null,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/api/chat'),
        headers: {"Content-Type": "application/json"},
        body: json.encode(payload),
      ).timeout(const Duration(seconds: 35));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final responseText = data["response"] ?? "Action completed.";
        final toolCalls = data["tool_calls"] ?? [];

        _messages.add(ChatMessage(
          text: responseText,
          isUser: false,
          toolCalls: toolCalls,
        ));

        _setState(AssistantState.speaking);
        _currentSubtitle = responseText;
        notifyListeners();

        // Speak aloud
        await speakText(responseText);
      } else {
        _messages.add(ChatMessage(
          text: "Server Error (${response.statusCode}): ${response.body}",
          isUser: false,
        ));
        _setState(AssistantState.idle);
        notifyListeners();
      }
    } catch (e) {
      _messages.add(ChatMessage(
        text: "Connection failed to RB Server: $e",
        isUser: false,
      ));
      _setState(AssistantState.idle);
      notifyListeners();
    }
  }

  // 5 Sub-Agents API Bridge
  Future<Map<String, dynamic>> runSubAgent(String agent, String action, Map<String, dynamic> params) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/agents'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({"agent": agent, "action": action, "params": params}),
      ).timeout(const Duration(seconds: 20));
      return json.decode(utf8.decode(res.bodyBytes));
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  // GitHub Repos API
  Future<Map<String, dynamic>> fetchGitHubRepos(String username) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/api/github?username=${Uri.encodeComponent(username)}'),
      ).timeout(const Duration(seconds: 15));
      return json.decode(utf8.decode(res.bodyBytes));
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  // Telegram API
  Future<Map<String, dynamic>> configureTelegram(String token, String action) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/telegram'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({"token": token, "action": action}),
      );
      return json.decode(res.body);
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  // WhatsApp Automation
  Future<void> launchWhatsApp(String phone, String message) async {
    final cleanPhone = phone.replaceAll(RegExp(r'\D'), '');
    final url = Uri.parse("https://wa.me/$cleanPhone?text=${Uri.encodeComponent(message)}");
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  // Hardware Action API
  Future<Map<String, dynamic>> triggerHardwareAction(String action, [Map<String, dynamic>? args]) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/action'),
        headers: {"Content-Type": "application/json"},
        body: json.encode({"action": action, "args": args ?? {}}),
      );
      return json.decode(res.body);
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  // Save Settings Persistently
  Future<void> saveSettings({
    required String newUserName,
    required String newAccent,
    required double newPitch,
    required double newRate,
    required bool newWakePhrase,
    required bool newCallAnnounce,
  }) async {
    _userName = newUserName;
    voiceAccent = newAccent;
    voicePitch = newPitch;
    voiceRate = newRate;
    wakePhraseEnabled = newWakePhrase;
    callAnnouncementEnabled = newCallAnnounce;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString("user_name", _userName);
    await prefs.setString("voice_accent", voiceAccent);
    await prefs.setDouble("voice_pitch", voicePitch);
    await prefs.setDouble("voice_rate", voiceRate);
    await prefs.setBool("wake_phrase_enabled", wakePhraseEnabled);
    await prefs.setBool("call_announcement_enabled", callAnnouncementEnabled);

    try {
      await http.post(
        Uri.parse('$baseUrl/api/settings'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          "user_name": _userName,
          "voice_accent": voiceAccent,
          "voice_pitch": voicePitch,
          "voice_rate": voiceRate,
          "wake_phrase_enabled": wakePhraseEnabled,
          "call_announcement_enabled": callAnnouncementEnabled,
        }),
      );
    } catch (_) {}

    notifyListeners();
  }
}
