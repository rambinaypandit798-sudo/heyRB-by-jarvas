import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/rbai_service.dart';

class SubAgentsWorkspaceScreen extends StatefulWidget {
  const SubAgentsWorkspaceScreen({Key? key}) : super(key: key);

  @override
  State<SubAgentsWorkspaceScreen> createState() => _SubAgentsWorkspaceScreenState();
}

class _SubAgentsWorkspaceScreenState extends State<SubAgentsWorkspaceScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  int _selectedAgentIndex = 0;

  final TextEditingController _researchCtrl = TextEditingController(text: "latest Google Gemini 2.5 flash models");
  final TextEditingController _memoryCtrl = TextEditingController(text: "यह चीज़ सेव कर लो: Meeting with Ram Binay at 4 PM");
  final TextEditingController _previewCtrl = TextEditingController(text: "https://flutter.dev");
  final TextEditingController _callerCtrl = TextEditingController(text: "Ankit Sharma");
  final TextEditingController _githubCtrl = TextEditingController(text: "torvalds");

  String _agentOutput = "Select an agent and tap Execute to trigger real-time autonomous processing.";
  bool _isLoading = false;

  final List<Map<String, dynamic>> _agents = [
    {
      "name": "Research & Web Agent",
      "subtitle": "Real-time HTTP web search & Gemini models",
      "color": const Color(0xFF00E5FF),
      "icon": Icons.public,
      "tag": "research"
    },
    {
      "name": "Memory & Notes Agent",
      "subtitle": "NLP parsing ('यह चीज़ सेव कर लो') & SQLite store",
      "color": const Color(0xFF10B981),
      "icon": Icons.psychology,
      "tag": "memory"
    },
    {
      "name": "Preview / View Agent",
      "subtitle": "Live URL inspection & Markdown engine",
      "color": const Color(0xFFF59E0B),
      "icon": Icons.preview,
      "tag": "preview"
    },
    {
      "name": "Automation Agent",
      "subtitle": "Platform channels & Call Announcements",
      "color": const Color(0xFF8B5CF6),
      "icon": Icons.memory,
      "tag": "automation"
    },
    {
      "name": "Coding & GitHub Agent",
      "subtitle": "Termux script execution & GitHub REST API",
      "color": const Color(0xFFEC4899),
      "icon": Icons.code,
      "tag": "coding"
    },
  ];

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _researchCtrl.dispose();
    _memoryCtrl.dispose();
    _previewCtrl.dispose();
    _callerCtrl.dispose();
    _githubCtrl.dispose();
    super.dispose();
  }

  Future<void> _executeCurrentAgent(RBAIService service) async {
    setState(() {
      _isLoading = true;
      _agentOutput = "Processing request via node...";
    });

    try {
      final tag = _agents[_selectedAgentIndex]["tag"];
      Map<String, dynamic> res = {};

      if (tag == "research") {
        res = await service.runSubAgent("research", "run", {"query": _researchCtrl.text.trim()});
      } else if (tag == "memory") {
        res = await service.runSubAgent("memory", "run", {"text": _memoryCtrl.text.trim()});
      } else if (tag == "preview") {
        res = await service.runSubAgent("preview", "run", {"target": _previewCtrl.text.trim()});
      } else if (tag == "automation") {
        res = await service.runSubAgent("automation", "call_announcement", {
          "caller_name": _callerCtrl.text.trim(),
          "phone": "+91-9876543210"
        });
      } else if (tag == "coding") {
        res = await service.fetchGitHubRepos(_githubCtrl.text.trim());
      }

      setState(() {
        _agentOutput = const JsonEncoder.withIndent('  ').convert(res);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _agentOutput = "Execution Error: $e";
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final service = Provider.of<RBAIService>(context);

    return Scaffold(
      backgroundColor: const Color(0xFF070B12),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B111E),
        elevation: 0,
        title: const Row(
          children: [
            Icon(Icons.hub, color: Color(0xFF00E5FF), size: 20),
            SizedBox(width: 8),
            Text(
              "5 SUB-AGENTS WORKSPACE",
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w800,
                fontSize: 14,
                letterSpacing: 0.6,
              ),
            ),
          ],
        ),
        leading: IconButton(
          icon: const Icon(Icons.close, color: Colors.white70),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Row(
        children: [
          // Left Side Core Node
          Container(
            width: 140,
            decoration: const BoxDecoration(
              color: Color(0xFF080D18),
              border: Border(
                right: BorderSide(color: Color(0xFF1E293B)),
              ),
            ),
            padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 10),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                AnimatedBuilder(
                  animation: _pulseController,
                  builder: (context, child) {
                    final scale = 1.0 + (_pulseController.value * 0.08);
                    return Transform.scale(
                      scale: scale,
                      child: Container(
                        width: 88,
                        height: 88,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: const RadialGradient(
                            colors: [
                              Color(0xFF00E5FF),
                              Color(0xFF0077FE),
                            ],
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF00E5FF).withOpacity(0.5),
                              blurRadius: 20,
                              spreadRadius: 2,
                            ),
                          ],
                          border: Border.all(color: Colors.white, width: 2),
                        ),
                        child: const Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.bolt, color: Colors.white, size: 24),
                            SizedBox(height: 2),
                            Text(
                              "RB CORE",
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w900,
                                fontSize: 10,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 16),
                const Text(
                  "MASTER\nORCHESTRATOR",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Color(0xFF38BDF8),
                    fontSize: 9,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.8,
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  "Active User:\n${service.userName}",
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    color: Colors.white60,
                    fontSize: 8,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),

          // Right Side 5 Sub-Agents Nodes List & Execution
          Expanded(
            child: Column(
              children: [
                // Agent Selector Horizontal/Vertical Chips
                SizedBox(
                  height: 120,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
                    itemCount: _agents.length,
                    itemBuilder: (context, i) {
                      final agent = _agents[i];
                      final isSelected = _selectedAgentIndex == i;
                      final Color col = agent["color"];

                      return GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedAgentIndex = i;
                            _agentOutput = "Node switched to ${agent['name']}. Ready to execute.";
                          });
                        },
                        child: Container(
                          width: 140,
                          margin: const EdgeInsets.only(right: 8),
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: isSelected ? col.withOpacity(0.18) : const Color(0xFF0E1626),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: isSelected ? col : Colors.white12,
                              width: isSelected ? 2 : 1,
                            ),
                            boxShadow: isSelected
                                ? [BoxShadow(color: col.withOpacity(0.3), blurRadius: 10)]
                                : [],
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  Icon(agent["icon"], color: col, size: 18),
                                  const Spacer(),
                                  if (isSelected)
                                    Container(
                                      width: 6,
                                      height: 6,
                                      decoration: BoxDecoration(
                                        color: col,
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                ],
                              ),
                              Text(
                                agent["name"],
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w700,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),

                // Selected Agent Input Box
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _getControllerForIndex(_selectedAgentIndex),
                          style: const TextStyle(color: Colors.white, fontSize: 13),
                          decoration: InputDecoration(
                            filled: true,
                            fillColor: const Color(0xFF0E1626),
                            hintText: "Enter prompt or parameter...",
                            hintStyle: const TextStyle(color: Colors.white38, fontSize: 12),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(10),
                              borderSide: const BorderSide(color: Colors.white12),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(10),
                              borderSide: BorderSide(color: _agents[_selectedAgentIndex]["color"]),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton(
                        onPressed: _isLoading ? null : () => _executeCurrentAgent(service),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _agents[_selectedAgentIndex]["color"],
                          foregroundColor: Colors.black,
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        child: _isLoading
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                              )
                            : const Text("Execute", style: TextStyle(fontWeight: FontWeight.w800)),
                      ),
                    ],
                  ),
                ),

                // Output Terminal Console
                Expanded(
                  child: Container(
                    margin: const EdgeInsets.all(12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF030712),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.white10),
                    ),
                    child: SingleChildScrollView(
                      child: Text(
                        _agentOutput,
                        style: const TextStyle(
                          color: Color(0xFF38BDF8),
                          fontFamily: 'monospace',
                          fontSize: 11,
                          height: 1.4,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  TextEditingController _getControllerForIndex(int idx) {
    if (idx == 0) return _researchCtrl;
    if (idx == 1) return _memoryCtrl;
    if (idx == 2) return _previewCtrl;
    if (idx == 3) return _callerCtrl;
    return _githubCtrl;
  }
}
