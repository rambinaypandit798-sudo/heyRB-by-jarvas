import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/rbai_service.dart';

class SidebarDrawer extends StatefulWidget {
  final Function(String route) onNavigate;

  const SidebarDrawer({Key? key, required this.onNavigate}) : super(key: key);

  @override
  State<SidebarDrawer> createState() => _SidebarDrawerState();
}

class _SidebarDrawerState extends State<SidebarDrawer> {
  final TextEditingController _searchCtrl = TextEditingController();

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final service = Provider.of<RBAIService>(context);
    final userInitials = service.userName.isNotEmpty
        ? service.userName.split(' ').map((e) => e[0]).take(2).join('').toUpperCase()
        : 'RB';

    return Drawer(
      backgroundColor: const Color(0xFF0D1322),
      child: Column(
        children: [
          // User Profile Header
          Container(
            padding: const EdgeInsets.fromLTRB(18, 48, 18, 16),
            color: const Color(0xFF131B2E),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: const Color(0xFF0284C7),
                  child: Text(
                    userInitials,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w800,
                      fontSize: 13,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        service.userName,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 2),
                      const Row(
                        children: [
                          Icon(Icons.circle, color: Color(0xFF10B981), size: 7),
                          SizedBox(width: 4),
                          Text(
                            "Active OS Node",
                            style: TextStyle(
                              color: Color(0xFF94A3B8),
                              fontSize: 10,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: Colors.white10),

          // Strictly the 8 Unified Navigation Items
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              children: [
                _buildNavItem(Icons.home, "Home", () {
                  Navigator.pop(context);
                  widget.onNavigate("home");
                }, isActive: true),
                _buildNavItem(Icons.public, "Web Preview", () {
                  Navigator.pop(context);
                  widget.onNavigate("web");
                }),
                _buildNavItem(Icons.code, "Code Preview", () {
                  Navigator.pop(context);
                  widget.onNavigate("code");
                }),
                _buildNavItem(Icons.folder_open, "File Preview", () {
                  Navigator.pop(context);
                  widget.onNavigate("files");
                }),
                _buildNavItem(Icons.tune, "Settings", () {
                  Navigator.pop(context);
                  widget.onNavigate("settings");
                }),
                _buildNavItem(Icons.view_in_ar, "Projects", () {
                  Navigator.pop(context);
                  widget.onNavigate("projects");
                }),
                _buildNavItem(Icons.extension, "Skill Add", () {
                  Navigator.pop(context);
                  widget.onNavigate("skills");
                }),
                _buildNavItem(Icons.chat_bubble_outline, "Chats", () {
                  Navigator.pop(context);
                  widget.onNavigate("chats");
                }),
              ],
            ),
          ),

          // Chats History Search Bar & Prominent "+ New Chat" Button
          Container(
            padding: const EdgeInsets.all(12),
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: Colors.white10)),
            ),
            child: Column(
              children: [
                TextField(
                  controller: _searchCtrl,
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                  decoration: InputDecoration(
                    hintText: "Search chat history...",
                    hintStyle: const TextStyle(color: Colors.white38, fontSize: 11),
                    prefixIcon: const Icon(Icons.search, size: 16, color: Colors.white38),
                    filled: true,
                    fillColor: const Color(0xFF131B2E),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: const BorderSide(color: Colors.white10),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: const BorderSide(color: Colors.white10),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0284C7),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    icon: const Icon(Icons.add, size: 16),
                    label: const Text(
                      "New chat",
                      style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                    ),
                    onPressed: () {
                      Navigator.pop(context);
                      widget.onNavigate("new_chat");
                    },
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem(
    IconData icon,
    String title,
    VoidCallback onTap, {
    bool isActive = false,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 2),
      decoration: BoxDecoration(
        color: isActive ? Colors.white.withOpacity(0.06) : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
      ),
      child: ListTile(
        leading: Icon(
          icon,
          color: isActive ? const Color(0xFF00E5FF) : const Color(0xFF94A3B8),
          size: 19,
        ),
        title: Text(
          title,
          style: TextStyle(
            color: isActive ? const Color(0xFF00E5FF) : const Color(0xFFF8FAFC),
            fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
            fontSize: 13,
          ),
        ),
        onTap: onTap,
        dense: true,
        visualDensity: const VisualDensity(vertical: -2),
      ),
    );
  }
}
