import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../services/rbai_service.dart';

class VoiceVisualizerOrb extends StatefulWidget {
  final AssistantState state;
  final VoidCallback onTap;

  const VoiceVisualizerOrb({
    Key? key,
    required this.state,
    required this.onTap,
  }) : super(key: key);

  @override
  State<VoiceVisualizerOrb> createState() => _VoiceVisualizerOrbState();
}

class _VoiceVisualizerOrbState extends State<VoiceVisualizerOrb>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Color getPrimaryColor() {
    switch (widget.state) {
      case AssistantState.listening:
        return const Color(0xFF00FFCC);
      case AssistantState.thinking:
        return const Color(0xFFBD00FF);
      case AssistantState.speaking:
        return const Color(0xFF00E5FF);
      case AssistantState.idle:
      default:
        return const Color(0xFF0077FE);
    }
  }

  String getStatusText() {
    switch (widget.state) {
      case AssistantState.listening:
        return "Listening... (Say 'Hey RB')";
      case AssistantState.thinking:
        return "RB.AI is thinking...";
      case AssistantState.speaking:
        return "Speaking...";
      case AssistantState.idle:
      default:
        return "Tap or say 'Hey RB'";
    }
  }

  @override
  Widget build(BuildContext context) {
    final primaryColor = getPrimaryColor();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        GestureDetector(
          onTap: widget.onTap,
          child: AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              final scale = widget.state == AssistantState.listening ||
                      widget.state == AssistantState.speaking
                  ? 1.0 + 0.12 * math.sin(_controller.value * 2 * math.pi)
                  : 1.0 + 0.04 * math.sin(_controller.value * 2 * math.pi);

              return Transform.scale(
                scale: scale,
                child: Container(
                  width: 140,
                  height: 140,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      colors: [
                        primaryColor.withOpacity(0.9),
                        primaryColor.withOpacity(0.4),
                        Colors.transparent,
                      ],
                      stops: const [0.3, 0.7, 1.0],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: primaryColor.withOpacity(0.6),
                        blurRadius: 35,
                        spreadRadius: 8,
                      ),
                    ],
                  ),
                  child: Center(
                    child: Container(
                      width: 75,
                      height: 75,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFF0A0E17),
                        border: Border.all(color: primaryColor, width: 2),
                      ),
                      child: Icon(
                        widget.state == AssistantState.listening
                            ? Icons.mic
                            : widget.state == AssistantState.thinking
                                ? Icons.psychology
                                : Icons.graphic_eq,
                        color: primaryColor,
                        size: 38,
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 16),
        Text(
          getStatusText(),
          style: TextStyle(
            color: primaryColor,
            fontSize: 14,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.8,
          ),
        ),
      ],
    );
  }
}
