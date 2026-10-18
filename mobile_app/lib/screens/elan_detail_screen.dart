import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/models.dart';
import '../providers/auth_provider.dart';
import '../providers/elan_provider.dart';
import '../services/api_service.dart';
import 'auth_screen.dart';
import 'messages_screen.dart';
import 'seller_elanlar_screen.dart';

class ElanDetailScreen extends StatefulWidget {
  final int elanId;
  final ElanModel? initialElan;

  const ElanDetailScreen({
    super.key,
    required this.elanId,
    this.initialElan,
  });

  @override
  State<ElanDetailScreen> createState() => _ElanDetailScreenState();
}

class _ElanDetailScreenState extends State<ElanDetailScreen>
    with TickerProviderStateMixin {
  ElanModel? _elan;
  bool _isLoading = true;
  String? _error;
  int _currentImageIndex = 0;
  final PageController _pageController = PageController();

  // Smooth fast badge animation
  late final AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _elan = widget.initialElan;
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 280),
      vsync: this,
      value: 1.0,
    );
    _fetchDetail();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _pageController.dispose();
    super.dispose();
  }

  Future<void> _fetchDetail() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final fullElan = await ApiService.getElanDetail(widget.elanId);
      if (mounted) {
        setState(() {
          _elan = fullElan;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString().replaceAll('Exception: ', '');
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _handleFavoriteToggle() async {
    final elan = _elan;
    if (elan == null) return;

    final auth = context.read<AuthProvider>();
    if (!auth.isAuthenticated) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const AuthScreen()),
      );
      return;
    }

    try {
      final isFav =
          await context.read<ElanProvider>().toggleFavorite(elan.id);
      if (mounted) {
        setState(() {
          elan.isFavorit = isFav;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Xəta: $e')),
        );
      }
    }
  }

  Future<void> _makePhoneCall(ElanModel elan) async {
    if (elan.telefon.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Telefon nömrəsi qeyd olunmayıb')),
      );
      return;
    }
    ApiService.registerElanClick(elan.id, 'zeng');
    final cleanPhone = elan.telefon.replaceAll(RegExp(r'[^\d+]'), '');
    final uri = Uri.parse('tel:$cleanPhone');
    try {
      await launchUrl(uri);
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Zəng edilə bilmədi: ${elan.telefon}')),
        );
      }
    }
  }

  Future<void> _openWhatsApp(ElanModel elan) async {
    if (elan.telefon.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Telefon nömrəsi qeyd olunmayıb')),
      );
      return;
    }
    ApiService.registerElanClick(elan.id, 'wp');
    String digits = elan.telefon.replaceAll(RegExp(r'\D'), '');
    if (digits.startsWith('0') && digits.length == 10) {
      digits = '994${digits.substring(1)}';
    } else if (digits.length == 9) {
      digits = '994$digits';
    } else if (!digits.startsWith('994') && digits.isNotEmpty) {
      digits = '994$digits';
    }

    final text = Uri.encodeComponent(
      'Salam, Prousta.az-dakı "${elan.bashliq}" (#${elan.nomre}) elanınızla bağlı yazıram.',
    );
    final uri = Uri.parse('https://wa.me/$digits?text=$text');
    try {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('WhatsApp açıla bilmədi')),
        );
      }
    }
  }

  void _openMessage(ElanModel elan) {
    final auth = context.read<AuthProvider>();
    if (!auth.isAuthenticated) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const AuthScreen()),
      );
      return;
    }

    final info = elan.istifadeciInfo;
    final sellerId = info?['id'] is int
        ? info!['id'] as int
        : int.tryParse(info?['id']?.toString() ?? '') ?? 0;

    if (sellerId == 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Elan sahibi haqqında məlumat tapılmadı')),
      );
      return;
    }

    if (auth.user?.id == sellerId) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Öz elanınıza mesaj göndərə bilməzsiniz')),
      );
      return;
    }

    final sellerName = _extractSellerName(info);

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ChatDetailScreen(
          otherUserId: sellerId,
          otherUserName: sellerName,
          elanId: elan.id,
          elanTitle: elan.bashliq,
        ),
      ),
    );
  }

  String _extractSellerName(Map<String, dynamic>? info) {
    if (info == null) return 'Peşəkar Usta';
    final adSoyad = info['ad_soyad']?.toString().trim() ?? '';
    if (adSoyad.isNotEmpty) return adSoyad;
    final ad = info['ad']?.toString().trim() ?? '';
    final soyad = info['soyad']?.toString().trim() ?? '';
    final combined = '$ad $soyad'.trim();
    if (combined.isNotEmpty) return combined;
    final username = info['username']?.toString().trim() ?? '';
    if (username.isNotEmpty) return username;
    return 'Peşəkar Usta';
  }

  @override
  Widget build(BuildContext context) {
    final elan = _elan;

    if (_isLoading && elan == null) {
      return const Scaffold(
        backgroundColor: Color(0xFFF7FAF9),
        body: Center(
          child: CircularProgressIndicator(color: Color(0xFF007B52)),
        ),
      );
    }

    if (_error != null && elan == null) {
      return Scaffold(
        backgroundColor: const Color(0xFFF7FAF9),
        appBar: AppBar(),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(_error!, textAlign: TextAlign.center),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: _fetchDetail,
                  child: const Text('Yenidən cəhd et'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    if (elan == null) return const SizedBox.shrink();

    final images = elan.allImageUrls;
    final info = elan.istifadeciInfo;
    final sellerId = info?['id'] is int
        ? info!['id'] as int
        : int.tryParse(info?['id']?.toString() ?? '') ?? 0;
    final currentUserId = context.watch<AuthProvider>().user?.id;
    final isOwner =
        currentUserId != null && sellerId != 0 && currentUserId == sellerId;
    final sellerName = _extractSellerName(info);
    final sellerAvatar = info?['avatar']?.toString() ??
        (images.isNotEmpty ? images.first : null);
    final ratingScore = (4.8 + (elan.id % 3) * 0.1).toStringAsFixed(1);
    const double galleryHeight = 310.0;

    return Scaffold(
      backgroundColor: const Color(0xFFF7FAF9),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 780),
          child: Stack(
            children: [
              // 1. Top Portfolio Image Gallery
              Column(
                children: [
                  SizedBox(
                    height: galleryHeight,
                    width: double.infinity,
                    child: Stack(
                      fit: StackFit.expand,
                      children: [
                        if (images.isNotEmpty)
                          PageView.builder(
                            controller: _pageController,
                            itemCount: images.length,
                            onPageChanged: (idx) {
                              setState(() => _currentImageIndex = idx);
                            },
                            itemBuilder: (context, index) {
                              return CachedNetworkImage(
                                imageUrl: images[index],
                                fit: BoxFit.cover,
                                placeholder: (_, _) => Container(
                                  color: const Color(0xFFEAF6F1),
                                ),
                                errorWidget: (_, _, _) =>
                                    _buildFallbackGallery(),
                              );
                            },
                          )
                        else
                          _buildFallbackGallery(),
                        Positioned(
                          bottom: 38,
                          left: 16,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.black.withValues(alpha: 0.6),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              '${_currentImageIndex + 1} / ${images.isEmpty ? 1 : images.length}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              // 2. CourseInfoScreen Overlapping 32px Rounded Sheet
              Positioned(
                top: galleryHeight - 28.0,
                bottom: 0,
                left: 0,
                right: 0,
                child: Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFFF7FAF9),
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(32.0),
                      topRight: Radius.circular(32.0),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF17262A).withValues(alpha: 0.16),
                        offset: const Offset(0, -4),
                        blurRadius: 16.0,
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 10),
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.only(bottom: 100),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Title (from course_info_screen.dart)
                          Padding(
                            padding: const EdgeInsets.only(
                              top: 28.0,
                              left: 16,
                              right: 84,
                            ),
                            child: Text(
                              elan.bashliq,
                              textAlign: TextAlign.left,
                              style: const TextStyle(
                                fontWeight: FontWeight.w800,
                                fontSize: 21,
                                letterSpacing: 0.2,
                                height: 1.25,
                                color: Color(0xFF17262A),
                              ),
                            ),
                          ),

                          // Price & Star Rating Row (from course_info_screen.dart)
                          Padding(
                            padding: const EdgeInsets.only(
                              left: 16,
                              right: 16,
                              bottom: 8,
                              top: 14,
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                Text(
                                  elan.formattedPrice,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w900,
                                    fontSize: 22,
                                    letterSpacing: 0.2,
                                    color: Color(0xFF007B52),
                                  ),
                                ),
                                Row(
                                  children: [
                                    if (elan.isVip)
                                      Container(
                                        margin: const EdgeInsets.only(right: 8),
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 8,
                                          vertical: 3,
                                        ),
                                        decoration: BoxDecoration(
                                          gradient: const LinearGradient(
                                            colors: [
                                              Color(0xFFF59E0B),
                                              Color(0xFFD97706),
                                            ],
                                          ),
                                          borderRadius:
                                              BorderRadius.circular(8),
                                        ),
                                        child: const Text(
                                          'VİP',
                                          style: TextStyle(
                                            color: Colors.white,
                                            fontSize: 11,
                                            fontWeight: FontWeight.w900,
                                          ),
                                        ),
                                      ),
                                    Text(
                                      ratingScore,
                                      style: const TextStyle(
                                        fontWeight: FontWeight.w700,
                                        fontSize: 19,
                                        color: Color(0xFF475569),
                                      ),
                                    ),
                                    const SizedBox(width: 4),
                                    const Icon(
                                      Icons.star_rounded,
                                      color: Color(0xFF0FA968),
                                      size: 24,
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),

                          // 3. Animated Stats Row
                          AnimatedOpacity(
                            duration: const Duration(milliseconds: 150),
                            opacity: 1.0,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 6,
                              ),
                              child: isOwner
                                  ? Row(
                                      children: [
                                        Expanded(
                                          child: _getTimeBoxUI(
                                            '${elan.baxishSayi}',
                                            'Baxış',
                                          ),
                                        ),
                                        Expanded(
                                          child: _getTimeBoxUI(
                                            '${elan.zengSayi}',
                                            'Zəng',
                                          ),
                                        ),
                                        Expanded(
                                          child: _getTimeBoxUI(
                                            '${elan.wpSayi}',
                                            'WhatsApp',
                                          ),
                                        ),
                                      ],
                                    )
                                  : Row(
                                      children: [
                                        Expanded(
                                          child: _getTimeBoxUI(
                                            elan.sheher,
                                            'Şəhər',
                                          ),
                                        ),
                                        Expanded(
                                          child: _getTimeBoxUI(
                                            '${elan.baxishSayi}',
                                            'Baxış',
                                          ),
                                        ),
                                        Expanded(
                                          child: _getTimeBoxUI(
                                            '#${elan.nomre.isNotEmpty ? elan.nomre : elan.id}',
                                            'Elan kodu',
                                          ),
                                        ),
                                      ],
                                    ),
                            ),
                          ),

                          // 4. Animated Description & Seller Card
                          AnimatedOpacity(
                            duration: const Duration(milliseconds: 150),
                            opacity: 1.0,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                                vertical: 10,
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Tradesperson Profile Card
                                  Container(
                                    padding: const EdgeInsets.all(14),
                                    decoration: BoxDecoration(
                                      color: Colors.white,
                                      borderRadius: BorderRadius.circular(18),
                                      boxShadow: [
                                        BoxShadow(
                                          color: const Color(0xFF17262A)
                                              .withValues(alpha: 0.06),
                                          offset: const Offset(0, 4),
                                          blurRadius: 10,
                                        ),
                                      ],
                                    ),
                                    child: Row(
                                      children: [
                                        InkWell(
                                          onTap: sellerId > 0
                                              ? () {
                                                  Navigator.push(
                                                    context,
                                                    MaterialPageRoute(
                                                      builder: (_) =>
                                                          SellerElanlarScreen(
                                                        sellerId: sellerId,
                                                        sellerName: sellerName,
                                                        sellerAvatar:
                                                            sellerAvatar,
                                                      ),
                                                    ),
                                                  );
                                                }
                                              : null,
                                          borderRadius:
                                              BorderRadius.circular(26),
                                          child: CircleAvatar(
                                            radius: 26,
                                            backgroundColor:
                                                const Color(0xFFEAF6F1),
                                            backgroundImage: (sellerAvatar !=
                                                        null &&
                                                    sellerAvatar.isNotEmpty)
                                                ? CachedNetworkImageProvider(
                                                    sellerAvatar)
                                                : null,
                                            child: (sellerAvatar == null ||
                                                    sellerAvatar.isEmpty)
                                                ? Text(
                                                    sellerName.isNotEmpty
                                                        ? sellerName[0]
                                                            .toUpperCase()
                                                        : 'U',
                                                    style: const TextStyle(
                                                      fontSize: 20,
                                                      fontWeight: FontWeight.w800,
                                                      color: Color(0xFF007B52),
                                                    ),
                                                  )
                                                : null,
                                          ),
                                        ),
                                        const SizedBox(width: 12),
                                        Expanded(
                                          child: InkWell(
                                            onTap: sellerId > 0
                                                ? () {
                                                    Navigator.push(
                                                      context,
                                                      MaterialPageRoute(
                                                        builder: (_) =>
                                                            SellerElanlarScreen(
                                                          sellerId: sellerId,
                                                          sellerName:
                                                              sellerName,
                                                          sellerAvatar:
                                                              sellerAvatar,
                                                        ),
                                                      ),
                                                    );
                                                  }
                                                : null,
                                            borderRadius:
                                                BorderRadius.circular(8),
                                            child: Column(
                                              crossAxisAlignment:
                                                  CrossAxisAlignment.start,
                                              children: [
                                                Row(
                                                  children: [
                                                    Flexible(
                                                      child: Text(
                                                        sellerName,
                                                        maxLines: 1,
                                                        overflow:
                                                            TextOverflow.ellipsis,
                                                        style: const TextStyle(
                                                          fontSize: 16,
                                                          fontWeight:
                                                              FontWeight.w800,
                                                          color:
                                                              Color(0xFF17262A),
                                                        ),
                                                      ),
                                                    ),
                                                    const SizedBox(width: 5),
                                                    const Icon(
                                                      Icons.verified_rounded,
                                                      color: Color(0xFF0FA968),
                                                      size: 18,
                                                    ),
                                                    const SizedBox(width: 4),
                                                    const Icon(
                                                      Icons.arrow_forward_ios_rounded,
                                                      color: Color(0xFF94A3B8),
                                                      size: 13,
                                                    ),
                                                  ],
                                                ),
                                                const SizedBox(height: 3),
                                                Text(
                                                  'Ustanın bütün elanlarına bax →',
                                                  style: const TextStyle(
                                                    fontSize: 12,
                                                    color: Color(0xFF007B52),
                                                    fontWeight: FontWeight.w700,
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ),
                                        if (elan.telefon.isNotEmpty)
                                          TextButton.icon(
                                            onPressed: () =>
                                                _openWhatsApp(elan),
                                            icon: const Icon(
                                              Icons.chat_rounded,
                                              size: 16,
                                              color: Color(0xFF0FA968),
                                            ),
                                            label: const Text(
                                              'WhatsApp',
                                              style: TextStyle(
                                                fontWeight: FontWeight.w800,
                                                color: Color(0xFF007B52),
                                              ),
                                            ),
                                          ),
                                      ],
                                    ),
                                  ),

                                  const SizedBox(height: 16),
                                  const Text(
                                    'Xidmət haqqında ətraflı',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w800,
                                      color: Color(0xFF17262A),
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    (elan.acaqlama != null &&
                                            elan.acaqlama!.trim().isNotEmpty)
                                        ? elan.acaqlama!
                                        : 'Peşəkar usta tərəfindən zəmanətli və yüksək keyfiyyətli xidmət göstərilir. Ətraflı məlumat və sifariş üçün zəng edə və ya mesaj yaza bilərsiniz.',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w400,
                                      fontSize: 14.5,
                                      letterSpacing: 0.2,
                                      height: 1.55,
                                      color: Color(0xFF475569),
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
              ),

              // 5. ScaleTransition Floating Circular Favorite FAB (from course_info_screen.dart)
              Positioned(
                top: galleryHeight - 28.0 - 30.0,
                right: 28,
                child: ScaleTransition(
                  alignment: Alignment.center,
                  scale: CurvedAnimation(
                    parent: _animationController,
                    curve: Curves.fastOutSlowIn,
                  ),
                  child: Card(
                    color: const Color(0xFF0FA968),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(50.0),
                    ),
                    elevation: 10.0,
                    shadowColor:
                        const Color(0xFF007B52).withValues(alpha: 0.45),
                    child: InkWell(
                      customBorder: const CircleBorder(),
                      onTap: _handleFavoriteToggle,
                      child: SizedBox(
                        width: 58,
                        height: 58,
                        child: Center(
                          child: Icon(
                            elan.isFavorit
                                ? Icons.favorite_rounded
                                : Icons.favorite_border_rounded,
                            color: Colors.white,
                            size: 28,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),

              // 6. Top-left Back Button
              Padding(
                padding: EdgeInsets.only(
                  top: MediaQuery.of(context).padding.top + 8,
                  left: 12,
                ),
                child: SizedBox(
                  width: 44,
                  height: 44,
                  child: Material(
                    color: Colors.white.withValues(alpha: 0.9),
                    shape: const CircleBorder(),
                    child: InkWell(
                      customBorder: const CircleBorder(),
                      onTap: () => Navigator.pop(context),
                      child: const Icon(
                        Icons.arrow_back_ios_new_rounded,
                        color: Color(0xFF17262A),
                        size: 19,
                      ),
                    ),
                  ),
                ),
              ),

              // 7. Bottom Sticky Action Bar: Zəng et + WhatsApp (+ In-App Chat)
              Positioned(
                left: 0,
                right: 0,
                bottom: 0,
                child: AnimatedOpacity(
                  duration: const Duration(milliseconds: 150),
                  opacity: 1.0,
                  child: Container(
                    padding: EdgeInsets.only(
                      left: 16,
                      right: 16,
                      top: 12,
                      bottom: MediaQuery.of(context).padding.bottom + 14,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      border: const Border(
                        top: BorderSide(color: Color(0xFFE2E8F0)),
                      ),
                      boxShadow: [
                        BoxShadow(
                          color:
                              const Color(0xFF17262A).withValues(alpha: 0.08),
                          blurRadius: 14,
                          offset: const Offset(0, -3),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        // 1. Zəng et Button
                        Expanded(
                          child: Container(
                            height: 48,
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [
                                  Color(0xFF007B52),
                                  Color(0xFF0A4D34),
                                ],
                              ),
                              borderRadius: const BorderRadius.all(
                                Radius.circular(14.0),
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFF007B52)
                                      .withValues(alpha: 0.32),
                                  offset: const Offset(0, 4),
                                  blurRadius: 10.0,
                                ),
                              ],
                            ),
                            child: Material(
                              color: Colors.transparent,
                              child: InkWell(
                                borderRadius: const BorderRadius.all(
                                  Radius.circular(14.0),
                                ),
                                onTap: () => _makePhoneCall(elan),
                                child: const Center(
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(
                                        Icons.phone_in_talk_rounded,
                                        color: Colors.white,
                                        size: 19,
                                      ),
                                      SizedBox(width: 7),
                                      Text(
                                        'Zəng et',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w800,
                                          fontSize: 15,
                                          color: Colors.white,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        // 2. WhatsApp Button
                        Expanded(
                          child: Container(
                            height: 48,
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [
                                  Color(0xFF25D366),
                                  Color(0xFF128C7E),
                                ],
                              ),
                              borderRadius: const BorderRadius.all(
                                Radius.circular(14.0),
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFF25D366)
                                      .withValues(alpha: 0.35),
                                  offset: const Offset(0, 4),
                                  blurRadius: 10.0,
                                ),
                              ],
                            ),
                            child: Material(
                              color: Colors.transparent,
                              child: InkWell(
                                borderRadius: const BorderRadius.all(
                                  Radius.circular(14.0),
                                ),
                                onTap: () => _openWhatsApp(elan),
                                child: const Center(
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(
                                        Icons.chat_rounded,
                                        color: Colors.white,
                                        size: 19,
                                      ),
                                      SizedBox(width: 7),
                                      Text(
                                        'WhatsApp',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w800,
                                          fontSize: 15,
                                          color: Colors.white,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        // 3. In-App Message Button
                        SizedBox(
                          width: 48,
                          height: 48,
                          child: Material(
                            color: const Color(0xFFEAF6F1),
                            borderRadius:
                                const BorderRadius.all(Radius.circular(14.0)),
                            child: InkWell(
                              borderRadius:
                                  const BorderRadius.all(Radius.circular(14.0)),
                              onTap: () => _openMessage(elan),
                              child: Container(
                                decoration: BoxDecoration(
                                  borderRadius: const BorderRadius.all(
                                    Radius.circular(14.0),
                                  ),
                                  border: Border.all(
                                    color: const Color(0xFF0FA968)
                                        .withValues(alpha: 0.4),
                                  ),
                                ),
                                child: const Icon(
                                  Icons.forum_outlined,
                                  color: Color(0xFF007B52),
                                  size: 22,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Exact adaptation of getTimeBoxUI() from best_flutter_ui_templates/lib/design_course/course_info_screen.dart
  Widget _getTimeBoxUI(String valueText, String labelText) {
    return Padding(
      padding: const EdgeInsets.all(6.0),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: const BorderRadius.all(Radius.circular(16.0)),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF17262A).withValues(alpha: 0.08),
              offset: const Offset(1.1, 1.1),
              blurRadius: 8.0,
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 12.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Text(
                valueText,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontWeight: FontWeight.w800,
                  fontSize: 13.5,
                  letterSpacing: 0.2,
                  color: Color(0xFF007B52),
                ),
              ),
              const SizedBox(height: 3),
              Text(
                labelText,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontWeight: FontWeight.w500,
                  fontSize: 12,
                  color: Color(0xFF64748B),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFallbackGallery() {
    return Container(
      color: const Color(0xFFEAF6F1),
      child: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.handyman_outlined,
              size: 52,
              color: Color(0xFF007B52),
            ),
            SizedBox(height: 8),
            Text(
              'prousta.az',
              style: TextStyle(
                color: Color(0xFF007B52),
                fontWeight: FontWeight.w800,
                fontSize: 15,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
