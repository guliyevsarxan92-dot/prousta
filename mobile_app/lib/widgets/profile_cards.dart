import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import '../models/models.dart';

/// Profile top header banner with avatar, full name, and subtitle.
class ProustaProfileHeader extends StatelessWidget {
  final AppUser user;
  final String subtitle;
  final VoidCallback onEditPressed;

  const ProustaProfileHeader({
    super.key,
    required this.user,
    required this.subtitle,
    required this.onEditPressed,
  });

  @override
  Widget build(BuildContext context) {
    final topPad = MediaQuery.of(context).padding.top;
    final bannerHeight = 86.0 + topPad;
    return Stack(
      children: <Widget>[
        Container(
          height: bannerHeight,
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF0A4D34), Color(0xFF007B52), Color(0xFF0FA968)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Stack(
            children: [
              Positioned(
                top: -35,
                right: -25,
                child: Container(
                  width: 130,
                  height: 130,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white.withValues(alpha: 0.08),
                  ),
                ),
              ),
              Positioned(
                bottom: 10,
                left: -30,
                child: Container(
                  width: 95,
                  height: 95,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white.withValues(alpha: 0.06),
                  ),
                ),
              ),
            ],
          ),
        ),
        Container(
          width: double.infinity,
          margin: EdgeInsets.only(top: bannerHeight - 44),
          child: Column(
            children: <Widget>[
              GestureDetector(
                onTap: onEditPressed,
                child: ProustaAvatar(
                  imageUrl: user.profil.avatar,
                  fallbackInitial: user.fullName.isNotEmpty
                      ? user.fullName[0].toUpperCase()
                      : 'U',
                  borderColor: Colors.white,
                  backgroundColor: const Color(0xFFEAF6F1),
                  radius: 42,
                  borderWidth: 4.5,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    user.fullName,
                    style: const TextStyle(
                      fontSize: 19,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(width: 5),
                  const Icon(
                    Icons.verified_rounded,
                    color: Color(0xFF0FA968),
                    size: 18,
                  ),
                ],
              ),
              const SizedBox(height: 3),
              Text(
                subtitle,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF64748B),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// Personal details, logout, and account deletion card on ProfileScreen.
class ProustaUserInfoCard extends StatelessWidget {
  final String city;
  final String email;
  final String phone;
  final String username;
  final VoidCallback onLogout;
  final VoidCallback onDeleteAccount;

  const ProustaUserInfoCard({
    super.key,
    required this.city,
    required this.email,
    required this.phone,
    required this.username,
    required this.onLogout,
    required this.onDeleteAccount,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          const Padding(
            padding: EdgeInsets.only(left: 6.0, bottom: 6.0),
            child: Text(
              'Şəxsi məlumatlar',
              style: TextStyle(
                color: Color(0xFF0F172A),
                fontWeight: FontWeight.w800,
                fontSize: 15.5,
              ),
            ),
          ),
          Card(
            elevation: 2.5,
            margin: EdgeInsets.zero,
            color: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
            child: Column(
              children: <Widget>[
                ...ListTile.divideTiles(
                  color: const Color(0xFFF1F5F9),
                  tiles: [
                    ListTile(
                      dense: true,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 2,
                      ),
                      leading: const Icon(
                        Icons.my_location_rounded,
                        color: Color(0xFF007B52),
                        size: 20,
                      ),
                      title: const Text(
                        'Şəhər / Ünvan',
                        style: TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                          color: Color(0xFF64748B),
                        ),
                      ),
                      subtitle: Text(
                        city,
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 14,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    ),
                    ListTile(
                      dense: true,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 2,
                      ),
                      leading: const Icon(
                        Icons.email_outlined,
                        color: Color(0xFF007B52),
                        size: 20,
                      ),
                      title: const Text(
                        'E-poçt və İstifadəçi adı',
                        style: TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                          color: Color(0xFF64748B),
                        ),
                      ),
                      subtitle: Text(
                        '$email ($username)',
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 14,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    ),
                    ListTile(
                      dense: true,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 2,
                      ),
                      leading: const Icon(
                        Icons.phone_outlined,
                        color: Color(0xFF007B52),
                        size: 20,
                      ),
                      title: const Text(
                        'Telefon nömrəsi',
                        style: TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                          color: Color(0xFF64748B),
                        ),
                      ),
                      subtitle: Text(
                        phone,
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 14,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    ),
                    ListTile(
                      onTap: onLogout,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 2,
                      ),
                      leading: const Icon(
                        Icons.power_settings_new_rounded,
                        color: Color(0xFFEF4444),
                        size: 21,
                      ),
                      title: const Text(
                        'Hesabdan çıxış et',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14.5,
                          color: Color(0xFFEF4444),
                        ),
                      ),
                      trailing: const Icon(
                        Icons.chevron_right_rounded,
                        color: Color(0xFFEF4444),
                      ),
                    ),
                    ListTile(
                      onTap: onDeleteAccount,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 2,
                      ),
                      leading: const Icon(
                        Icons.delete_forever_rounded,
                        color: Color(0xFF94A3B8),
                        size: 21,
                      ),
                      title: const Text(
                        'Hesabı sil',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                          color: Color(0xFF64748B),
                        ),
                      ),
                      trailing: const Icon(
                        Icons.chevron_right_rounded,
                        color: Color(0xFF94A3B8),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Triple-ring profile avatar widget.
class ProustaAvatar extends StatelessWidget {
  final String? imageUrl;
  final String fallbackInitial;
  final Color borderColor;
  final Color? backgroundColor;
  final double radius;
  final double borderWidth;

  const ProustaAvatar({
    super.key,
    required this.imageUrl,
    required this.fallbackInitial,
    this.borderColor = Colors.white,
    this.backgroundColor,
    this.radius = 40,
    this.borderWidth = 4,
  });

  @override
  Widget build(BuildContext context) {
    final hasImage = imageUrl != null && imageUrl!.trim().isNotEmpty;
    return CircleAvatar(
      radius: radius + borderWidth,
      backgroundColor: borderColor,
      child: CircleAvatar(
        radius: radius,
        backgroundColor: backgroundColor ?? const Color(0xFFEAF6F1),
        child: CircleAvatar(
          radius: radius - 3,
          backgroundColor: const Color(0xFFEAF6F1),
          backgroundImage: hasImage
              ? CachedNetworkImageProvider(imageUrl!)
              : null,
          child: !hasImage
              ? Text(
                  fallbackInitial,
                  style: TextStyle(
                    fontSize: radius * 0.65,
                    fontWeight: FontWeight.w700,
                    color: const Color(0xFF007B52),
                  ),
                )
              : null,
        ),
      ),
    );
  }
}
