import 'package:flutter/material.dart';

class ProustaWordmark extends StatelessWidget {
  final double fontSize;
  final bool centered;
  final bool lightMode;

  const ProustaWordmark({
    super.key,
    this.fontSize = 19.5,
    this.centered = false,
    this.lightMode = false,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveSize = fontSize > 22 ? 21.0 : fontSize;

    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment:
          centered ? MainAxisAlignment.center : MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.baseline,
      textBaseline: TextBaseline.alphabetic,
      children: [
        RichText(
          text: TextSpan(
            style: TextStyle(
              fontSize: effectiveSize,
              fontFamily: 'Roboto',
              height: 1.05,
              shadows: lightMode
                  ? null
                  : [
                      Shadow(
                        color: const Color(0xFF007B52).withValues(alpha: 0.10),
                        offset: const Offset(0, 1),
                        blurRadius: 2,
                      ),
                    ],
            ),
            children: [
              TextSpan(
                text: 'prousta',
                style: TextStyle(
                  color: lightMode ? Colors.white : const Color(0xFF0B3B28),
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.5,
                ),
              ),
              TextSpan(
                text: '.',
                style: TextStyle(
                  color: lightMode
                      ? const Color(0xFF34D399)
                      : const Color(0xFF10B981),
                  fontWeight: FontWeight.w900,
                  letterSpacing: -0.2,
                ),
              ),
              TextSpan(
                text: 'az',
                style: TextStyle(
                  color: lightMode
                      ? const Color(0xFF6EE7B7)
                      : const Color(0xFF00875A),
                  fontWeight: FontWeight.w700,
                  fontSize: effectiveSize * 0.92,
                  letterSpacing: -0.3,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
