import 'dart:typed_data';

enum MessageRole { user, assistant, system }

class ChatMessage {
  final String id;
  final MessageRole role;
  final String text;
  final Uint8List? imageBytes;
  final List<dynamic>? toolCalls;
  final DateTime timestamp;

  ChatMessage({
    String? id,
    MessageRole? role,
    bool? isUser,
    required this.text,
    this.imageBytes,
    this.toolCalls,
    DateTime? timestamp,
  })  : id = id ?? DateTime.now().millisecondsSinceEpoch.toString(),
        role = role ?? ((isUser == false) ? MessageRole.assistant : MessageRole.user),
        timestamp = timestamp ?? DateTime.now();

  bool get isUser => role == MessageRole.user;
}
