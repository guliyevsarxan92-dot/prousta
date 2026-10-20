import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/models.dart';

class ElanCard extends StatelessWidget {
  final ElanModel elan;
  final VoidCallback? onTap;
  final VoidCallback? onFavoriteToggle;
  final bool isHorizontal;
  final bool isFeaturedOverlap;

  const ElanCard({
    super.key,
    required this.elan,
    this.onTap,
    this.onFavoriteToggle,
    this.isHorizontal = false,
    this.isFeaturedOverlap = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isHorizontal) {
      return _buildStandardHorizontalCard(context);
    }
    return _buildStandardGridCard(context);
  }

  // Standard Vertical Card: Photo on top -> Service Name (bashliq) -> Price (formattedPrice)
  Widget _buildStandardGridCard(BuildContext context) {
    final imageUrl = elan.esasShekil ??
        (elan.allImageUrls.isNotEmpty ? elan.allImageUrls.first : null);
    final priceText = elan.qiymet != null && elan.qiymet! > 0
        ? elan.formattedPrice
        : 'Razılaşma yolu ilə';

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF0F172A).withValues(alpha: 0.18),
            offset: const Offset(0, 8),
            blurRadius: 20,
            spreadRadius: 1.5,
          ),
          BoxShadow(
            color: const Color(0xFF007B52).withValues(alpha: 0.08),
            offset: const Offset(0, 3),
            blurRadius: 8,
            spreadRadius: 0.5,
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(14),
        child: Material(
          color: Colors.white,
          child: InkWell(
            onTap: onTap,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 1. Photo on Top
                Expanded(
                  child: SizedBox(
                    width: double.infinity,
                    child: Stack(
                      fit: StackFit.expand,
                      children: [
                        if (imageUrl != null && imageUrl.isNotEmpty)
                          CachedNetworkImage(
                            imageUrl: imageUrl,
                            fit: BoxFit.cover,
                            placeholder: (_, _) =>
                                Container(color: const Color(0xFFF1F5F9)),
                            errorWidget: (_, _, _) => _buildPlaceholder(),
                          )
                        else
                          _buildPlaceholder(),

                        // VİP badge (top-left)
                        if (elan.isVip)
                          Positioned(
                            top: 8,
                            left: 8,
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 7,
                                vertical: 3,
                              ),
                              decoration: BoxDecoration(
                                gradient: const LinearGradient(
                                  colors: [
                                    Color(0xFFF59E0B),
                                    Color(0xFFD97706),
                                  ],
                                ),
                                borderRadius: BorderRadius.circular(6),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withValues(alpha: 0.15),
                                    blurRadius: 4,
                                    offset: const Offset(0, 1),
                                  ),
                                ],
                              ),
                              child: const Text(
                                'VİP',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 9.5,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 0.3,
                                ),
                              ),
                            ),
                          ),

                        // Favorite Heart Button (top-right)
                        if (onFavoriteToggle != null)
                          Positioned(
                            top: 6,
                            right: 6,
                            child: GestureDetector(
                              onTap: onFavoriteToggle,
                              child: Container(
                                width: 30,
                                height: 30,
                                decoration: BoxDecoration(
                                  color: Colors.white.withValues(alpha: 0.92),
                                  shape: BoxShape.circle,
                                  boxShadow: [
                                    BoxShadow(
                                      color:
                                          Colors.black.withValues(alpha: 0.10),
                                      blurRadius: 4,
                                      offset: const Offset(0, 1),
                                    ),
                                  ],
                                ),
                                child: Icon(
                                  elan.isFavorit
                                      ? Icons.favorite_rounded
                                      : Icons.favorite_border_rounded,
                                  size: 16,
                                  color: elan.isFavorit
                                      ? const Color(0xFFEF4444)
                                      : const Color(0xFF64748B),
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),

                // 2. Service Name (Xidmətin adı) & Price (Qiyməti)
                Padding(
                  padding: const EdgeInsets.fromLTRB(10, 9, 10, 10),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        elan.bashliq,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 13.5,
                          color: Color(0xFF0F172A),
                          height: 1.2,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        priceText,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 14,
                          color: Color(0xFF007B52),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Standard Horizontal Card: Photo on left -> Service Name & Price on right
  Widget _buildStandardHorizontalCard(BuildContext context) {
    final imageUrl = elan.esasShekil ??
        (elan.allImageUrls.isNotEmpty ? elan.allImageUrls.first : null);
    final priceText = elan.qiymet != null && elan.qiymet! > 0
        ? elan.formattedPrice
        : 'Razılaşma yolu ilə';

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF0F172A).withValues(alpha: 0.18),
            offset: const Offset(0, 8),
            blurRadius: 20,
            spreadRadius: 1.5,
          ),
          BoxShadow(
            color: const Color(0xFF007B52).withValues(alpha: 0.08),
            offset: const Offset(0, 3),
            blurRadius: 8,
            spreadRadius: 0.5,
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(14),
        child: Material(
          color: Colors.white,
          child: InkWell(
            onTap: onTap,
            child: Row(
              children: [
                // 1. Photo on Left
                SizedBox(
                  width: 108,
                  height: 92,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      if (imageUrl != null && imageUrl.isNotEmpty)
                        CachedNetworkImage(
                          imageUrl: imageUrl,
                          fit: BoxFit.cover,
                          placeholder: (_, _) =>
                              Container(color: const Color(0xFFF1F5F9)),
                          errorWidget: (_, _, _) => _buildPlaceholder(),
                        )
                      else
                        _buildPlaceholder(),
                      if (elan.isVip)
                        Positioned(
                          top: 6,
                          left: 6,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [Color(0xFFF59E0B), Color(0xFFD97706)],
                              ),
                              borderRadius: BorderRadius.circular(5),
                            ),
                            child: const Text(
                              'VİP',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 8.5,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),

                // 2. Service Name & Price on Right
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 10,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(
                              child: Text(
                                elan.bashliq,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 14.5,
                                  color: Color(0xFF0F172A),
                                  height: 1.25,
                                ),
                              ),
                            ),
                            if (onFavoriteToggle != null)
                              GestureDetector(
                                onTap: onFavoriteToggle,
                                child: Padding(
                                  padding: const EdgeInsets.only(left: 8),
                                  child: Icon(
                                    elan.isFavorit
                                        ? Icons.favorite_rounded
                                        : Icons.favorite_border_rounded,
                                    color: elan.isFavorit
                                        ? const Color(0xFFEF4444)
                                        : const Color(0xFF94A3B8),
                                    size: 20,
                                  ),
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          priceText,
                          style: const TextStyle(
                            fontWeight: FontWeight.w700,
                            fontSize: 15,
                            color: Color(0xFF007B52),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Container(
      color: const Color(0xFFEAF6F1),
      child: const Center(
        child: Text(
          'prousta.az',
          style: TextStyle(
            fontSize: 11.5,
            fontWeight: FontWeight.w600,
            color: Color(0xFF007B52),
            letterSpacing: -0.3,
          ),
        ),
      ),
    );
  }
}
