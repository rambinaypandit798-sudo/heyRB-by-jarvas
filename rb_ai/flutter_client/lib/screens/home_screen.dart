import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import '../services/rbai_service.dart';
import '../widgets/hud_reactor_button.dart';
import '../widgets/sub_agents_workspace.dart';
import '../widgets/sidebar_drawer.dart';
import '../widgets/chat_view.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ImagePicker _picker = ImagePicker();
  Uint8List? _selectedImageBytes;
  bool _isTorchOn = false;

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _handleSend(RBAIService service) {
    final text = _textController.text.trim();
    if (text.isEmpty && _selectedImageBytes == null) return;

    service.sendPrompt(
      text,
      imageBytes: _selectedImageBytes,
      isVoice: false,
    );

    _textController.clear();
    setState(() {
      _selectedImageBytes = null;
    });
    _scrollToBottom();
  }

  Future<void> _pickImage() async {
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.camera,
      maxWidth: 1024,
      imageQuality: 80,
    );
    if (photo != null) {
      final bytes = await photo.readAsBytes();
      setState(() {
        _selectedImageBytes = bytes;
      });
    }
  }

  void _openSubAgentsWorkspace() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const SubAgentsWorkspaceScreen()),
    );
  }

  void _showSettingsDialog(RBAIService service) {
    final nameCtrl = TextEditingController(text: service.userName);
    final urlCtrl = TextEditingController(text: service.baseUrl);
    String accent = service.voiceAccent;
    double pitch = service.voicePitch;
    double rate = service.voiceRate;
    bool wake = service.wakePhraseEnabled;
    bool call = service.callAnnouncementEnabled;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) => AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
          title: const Row(
            children: [
              Icon(Icons.settings, color: Color(0xFF0077FE)),
              SizedBox(width: 8),
              Text(
                "Advanced Settings",
                style: TextStyle(color: Color(0xFF0F172A), fontWeight: FontWeight.w800, fontSize: 16),
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("Dynamic User Name", style: TextStyle(fontWeight: FontWeight.w700, fontSize: 12, color: Color(0xFF475569))),
                const SizedBox(height: 4),
                TextField(
                  controller: nameCtrl,
                  style: const TextStyle(color: Color(0xFF0F172A), fontSize: 13),
                  decoration: InputDecoration(
                    filled: true,
                    fillColor: const Color(0xFFF8FAFC),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
                  ),
                ),
                const SizedBox(height: 12),
                const Text("Voice Accent & Language", style: TextStyle(fontWeight: FontWeight.w700, fontSize: 12, color: Color(0xFF475569))),
                const SizedBox(height: 4),
                DropdownButtonFormField<String>(
                  value: accent,
                  items: const [
                    DropdownMenuItem(value: "hi-IN", child: Text("Hindi (India) - hi-IN")),
                    DropdownMenuItem(value: "en-IN", child: Text("English (India) - en-IN")),
                    DropdownMenuItem(value: "en-US", child: Text("English (US) - en-US")),
                  ],
                  onChanged: (v) => setModalState(() => accent = v ?? "hi-IN"),
                  decoration: InputDecoration(
                    filled: true,
                    fillColor: const Color(0xFFF8FAFC),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
                const SizedBox(height: 12),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text("'Hey RB' Background Wake-Word", style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                  subtitle: const Text("Continuous low-power voice trigger", style: TextStyle(fontSize: 10)),
                  value: wake,
                  activeColor: const Color(0xFF0077FE),
                  onChanged: (v) => setModalState(() => wake = v),
                ),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text("Call Announcement Feature", style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                  subtitle: const Text("Speaks: '[Name], इनका फोन आया है'", style: TextStyle(fontSize: 10)),
                  value: call,
                  activeColor: const Color(0xFF0077FE),
                  onChanged: (v) => setModalState(() => call = v),
                ),
                const SizedBox(height: 8),
                const Text("Server URL", style: TextStyle(fontWeight: FontWeight.w700, fontSize: 12, color: Color(0xFF475569))),
                TextField(
                  controller: urlCtrl,
                  style: const TextStyle(fontSize: 12),
                  decoration: const InputDecoration(hintText: "http://127.0.0.1:8765"),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text("Cancel", style: TextStyle(color: Color(0xFF64748B))),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1E3A8A),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              onPressed: () async {
                service.setBaseUrl(urlCtrl.text.trim());
                await service.saveSettings(
                  newUserName: nameCtrl.text.trim(),
                  newAccent: accent,
                  newPitch: pitch,
                  newRate: rate,
                  newWakePhrase: wake,
                  newCallAnnounce: call,
                );
                Navigator.pop(ctx);
              },
              child: const Text("Save Configuration"),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final service = Provider.of<RBAIService>(context);

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      drawer: SidebarDrawer(
        onNavigate: (route) {
          if (route == "settings") {
            _showSettingsDialog(service);
          } else if (route == "web" || route == "code" || route == "files") {
            _openSubAgentsWorkspace();
          }
        },
      ),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        title: const Row(
          children: [
            Icon(Icons.hub, color: Color(0xFF0077FE), size: 22),
            SizedBox(width: 8),
            Text(
              "RB.AGENT",
              style: TextStyle(
                color: Color(0xFF0F172A),
                fontWeight: FontWeight.w900,
                fontSize: 17,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 14),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: service.isConnected ? const Color(0xFFECFDF5) : const Color(0xFFFEF2F2),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: service.isConnected ? const Color(0xFFA7F3D0) : const Color(0xFFFECACA),
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.circle,
                  size: 8,
                  color: service.isConnected ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                ),
                const SizedBox(width: 5),
                Text(
                  service.isConnected ? "LIVE" : "OFFLINE",
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    color: service.isConnected ? const Color(0xFF059669) : const Color(0xFFDC2626),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // 1. Compact Greeting Banner
            Container(
              margin: const EdgeInsets.fromLTRB(16, 12, 16, 4),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF0284C7), Color(0xFF0F172A)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFF00E5FF).withOpacity(0.2)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "नमस्ते, ${service.userName}",
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 15,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 2),
                        const Text(
                          "आज आपका क्या प्लान है?",
                          style: TextStyle(
                            color: Color(0xFF94A3B8),
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.bolt, color: Color(0xFF00E5FF), size: 18),
                ],
              ),
            ),

            // 2. Central Compact Arc Reactor HUD (< 30% height)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: HudReactorButton(
                size: 96,
                onTap: _openSubAgentsWorkspace,
              ),
            ),

            const SizedBox(height: 6),

            // Chat View
            Expanded(
              child: ChatView(
                messages: service.messages,
                scrollController: _scrollController,
              ),
            ),

            // Live Scrolling Subtitles & Captions Bar with TTS Pause/Resume
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              color: const Color(0xFF0F172A),
              child: Row(
                children: [
                  const Icon(Icons.closed_caption, color: Color(0xFF38BDF8), size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      service.currentSubtitle,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Color(0xFF38BDF8),
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  GestureDetector(
                    onTap: () {
                      if (service.state == AssistantState.speaking) {
                        service.pauseTts();
                      } else {
                        service.speakText(service.currentSubtitle);
                      }
                    },
                    child: Icon(
                      service.state == AssistantState.speaking ? Icons.pause : Icons.play_arrow,
                      color: const Color(0xFF38BDF8),
                      size: 18,
                    ),
                  ),
                ],
              ),
            ),

            // Image Thumbnail preview if selected
            if (_selectedImageBytes != null)
              Container(
                padding: const EdgeInsets.all(8),
                color: Colors.white,
                child: Row(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.memory(
                        _selectedImageBytes!,
                        width: 44,
                        height: 44,
                        fit: BoxFit.cover,
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      "Photo ready for Multimodal AI",
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.close, size: 16),
                      onPressed: () => setState(() => _selectedImageBytes = null),
                    ),
                  ],
                ),
              ),

            // Text & Mic Input Bar (No bottom navigation bar!)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              color: Colors.white,
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.camera_alt, color: Color(0xFF0077FE)),
                    onPressed: _pickImage,
                  ),
                  Expanded(
                    child: TextField(
                      controller: _textController,
                      style: const TextStyle(fontSize: 13, color: Color(0xFF0F172A)),
                      decoration: InputDecoration(
                        hintText: "Say 'यह चीज़ सेव कर लो' or ask RB...",
                        hintStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                        filled: true,
                        fillColor: const Color(0xFFF1F5F9),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                      ),
                      onSubmitted: (_) => _handleSend(service),
                    ),
                  ),
                  const SizedBox(width: 6),
                  IconButton(
                    icon: Icon(
                      service.state == AssistantState.listening ? Icons.mic : Icons.mic_none,
                      color: service.state == AssistantState.listening ? Colors.red : const Color(0xFF0077FE),
                    ),
                    onPressed: () {
                      if (service.state == AssistantState.listening) {
                        service.stopListening();
                      } else {
                        service.startListeningDirectly();
                      }
                    },
                  ),
                  IconButton(
                    icon: const Icon(Icons.send, color: Color(0xFF0077FE)),
                    onPressed: () => _handleSend(service),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
