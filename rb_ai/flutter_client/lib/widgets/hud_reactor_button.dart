import 'dart:math' as math;
import 'package:flutter/material.dart';

class HudReactorButton extends StatefulWidget {
  final VoidCallback onTap;
  final double size;

  const HudReactorButton({
    Key? key,
    required this.onTap,
    this.size = 110.0,
  }) : super(key: key);

  @override
  State<HudReactorButton> createState() => _HudReactorButtonState();
}

class _HudReactorButtonState extends State<HudReactorButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 10),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return SizedBox(
            width: widget.size,
            height: widget.size,
            child: Stack(
              alignment: Alignment.center,
              children: [
                // Outer Rotating Tech Ring (Clockwise)
                Transform.rotate(
                  angle: _controller.value * 2 * math.pi,
                  child: CustomPaint(
                    size: Size(widget.size, widget.size),
                    painter: ArcReactorOuterRingPainter(),
                  ),
                ),

                // Middle Counter-Rotating Ring (Anti-clockwise)
                Transform.rotate(
                  angle: -_controller.value * 2 * math.pi * 1.5,
                  child: CustomPaint(
                    size: Size(widget.size * 0.85, widget.size * 0.85),
                    painter: ArcReactorMidRingPainter(),
                  ),
                ),

                // Inner Glowing Core with Typography
                Container(
                  width: widget.size * 0.62,
                  height: widget.size * 0.62,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const RadialGradient(
                      colors: [
                        Color(0xFF0F172A),
                        Color(0xFF020617),
                      ],
                    ),
                    border: Border.all(
                      color: const Color(0xFF00E5FF),
                      width: 2.5,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF00E5FF).withOpacity(0.5),
                        blurRadius: 20,
                        spreadRadius: 2,
                      ),
                      BoxShadow(
                        color: const Color(0xFF0077FE).withOpacity(0.3),
                        blurRadius: 35,
                        spreadRadius: 6,
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.bolt,
                        color: Color(0xFF00E5FF),
                        size: 22,
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        "RB Agent",
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: 14,
                          letterSpacing: 0.8,
                          shadows: [
                            Shadow(
                              color: Color(0xFF00E5FF),
                              blurRadius: 8,
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        "tap to open agents",
                        style: TextStyle(
                          color: const Color(0xFF38BDF8).withOpacity(0.9),
                          fontSize: 8.5,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 0.2,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class ArcReactorOuterRingPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;

    final paintCyan = Paint()
      ..color = const Color(0xFF00E5FF).withOpacity(0.7)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    // Draw dashed tech arcs
    const segmentCount = 12;
    const sweep = (2 * math.pi) / segmentCount;
    for (int i = 0; i < segmentCount; i++) {
      if (i % 2 == 0) {
        canvas.drawArc(
          Rect.fromCircle(center: center, radius: radius),
          i * sweep,
          sweep * 0.7,
          false,
          paintCyan,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class ArcReactorMidRingPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;

    final paintBlue = Paint()
      ..color = const Color(0xFF0077FE).withOpacity(0.6)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.2;

    const segmentCount = 8;
    const sweep = (2 * math.pi) / segmentCount;
    for (int i = 0; i < segmentCount; i++) {
      if (i % 2 != 0) {
        canvas.drawArc(
          Rect.fromCircle(center: center, radius: radius),
          i * sweep,
          sweep * 0.5,
          false,
          paintBlue,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
