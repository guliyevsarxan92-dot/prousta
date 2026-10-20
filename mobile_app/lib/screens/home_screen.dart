import 'dart:async';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/auth_provider.dart';
import '../providers/elan_provider.dart';
import '../widgets/elan_card.dart';
import '../widgets/prousta_wordmark.dart';
import 'auth_screen.dart';
import 'elan_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  final VoidCallback? onNavigateToCategories;
  final VoidCallback? onNavigateToCreate;
  final VoidCallback? onNavigateToProfile;

  const HomeScreen({
    super.key,
    this.onNavigateToCategories,
    this.onNavigateToCreate,
    this.onNavigateToProfile,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const List<String> _cities = [
    'Bütün Azərbaycan',
    'Bakı',
    'Sumqayıt',
    'Xırdalan',
    'Gəncə',
    'Mingəçevir',
    'Lənkəran',
    'Şəki',
    'Quba',
  ];

  final TextEditingController _searchController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  Timer? _searchDebounce;

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      final provider = context.read<ElanProvider>();
      _searchController.text = provider.searchQuery;
      if (provider.elanlar.isEmpty && !provider.isLoading) {
        provider.loadInitialData();
      }
    });
  }

  @override
  void dispose() {
    _searchDebounce?.cancel();
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 280) {
      context.read<ElanProvider>().fetchElanlar(reset: false);
    }
  }

  void _onSearchChanged(String value) {
    setState(() {});
    _searchDebounce?.cancel();
    _searchDebounce = Timer(const Duration(milliseconds: 350), () {
      if (mounted) {
        context.read<ElanProvider>().setFilters(query: value.trim());
      }
    });
  }

  void _submitSearch(String value) {
    _searchDebounce?.cancel();
    context.read<ElanProvider>().setFilters(query: value.trim());
  }

  Future<void> _handleFavorite(ElanModel elan) async {
    final auth = context.read<AuthProvider>();
    if (!auth.isAuthenticated) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const AuthScreen()),
      );
      return;
    }
    try {
      await context.read<ElanProvider>().toggleFavorite(elan.id);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Xəta: $e')),
        );
      }
    }
  }

  void _openElanDetail(ElanModel elan) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ElanDetailScreen(
          elanId: elan.id,
          initialElan: elan,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final elanProvider = context.watch<ElanProvider>();
    final authProvider = context.watch<AuthProvider>();
    final displayedElanlar = elanProvider.elanlar;

    return Scaffold(
      backgroundColor: const Color(0xFFF7FAF9),
      body: RefreshIndicator(
        color: const Color(0xFF007B52),
        onRefresh: () => elanProvider.loadInitialData(),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1080),
            child: CustomScrollView(
              controller: _scrollController,
              physics: const AlwaysScrollableScrollPhysics(),
              slivers: [
                // 1. Ecommerce5 (flutter_ui_challenges) + DesignCourse Curved Header & Floating Search Bar
                SliverToBoxAdapter(
                  child: Stack(
                    children: [
                      // Curved bottom-radius backdrop (from ecommerce5.dart)
                      Container(
                        height: 136,
                        decoration: const BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Color(0xFFEAF6F1), Color(0xFFD9F0E6)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.only(
                            bottomLeft: Radius.circular(30.0),
                            bottomRight: Radius.circular(30.0),
                          ),
                        ),
                      ),
                      // Decorative organic green blob (from ecommerce5.dart)
                      Positioned(
                        top: -55,
                        right: -35,
                        child: Container(
                          width: 190,
                          height: 190,
                          decoration: BoxDecoration(
                            color:
                                const Color(0xFF0FA968).withValues(alpha: 0.14),
                            borderRadius: const BorderRadius.only(
                              bottomLeft: Radius.circular(130.0),
                              bottomRight: Radius.circular(80.0),
                            ),
                          ),
                        ),
                      ),
                      SafeArea(
                        bottom: false,
                        child: Column(
                          children: [
                            Padding(
                              padding:
                                  const EdgeInsets.fromLTRB(18, 12, 18, 10),
                              child: Row(
                                children: [
                                  Expanded(
                                    child: GestureDetector(
                                      onTap: () {
                                        _searchController.clear();
                                        elanProvider.resetFilters();
                                      },
                                      child: const ProustaWordmark(
                                        fontSize: 21,
                                      ),
                                    ),
                                  ),
                                  // City Selector Pill
                                  Container(
                                    height: 38,
                                    margin: const EdgeInsets.only(right: 10),
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 10),
                                    decoration: BoxDecoration(
                                      color: Colors.white,
                                      borderRadius: BorderRadius.circular(20),
                                      boxShadow: [
                                        BoxShadow(
                                          color: const Color(0xFF17262A)
                                              .withValues(alpha: 0.07),
                                          blurRadius: 10,
                                          offset: const Offset(0, 2),
                                        ),
                                      ],
                                    ),
                                    child: DropdownButtonHideUnderline(
                                      child: DropdownButton<String>(
                                        value: _cities.contains(
                                                elanProvider.selectedCity)
                                            ? elanProvider.selectedCity
                                            : 'Bütün Azərbaycan',
                                        isDense: true,
                                        icon: const Icon(
                                          Icons.keyboard_arrow_down_rounded,
                                          size: 17,
                                          color: Color(0xFF007B52),
                                        ),
                                        style: const TextStyle(
                                          fontSize: 12,
                                          fontWeight: FontWeight.w700,
                                          color: Color(0xFF17262A),
                                        ),
                                        items: _cities
                                            .map(
                                              (city) =>
                                                  DropdownMenuItem<String>(
                                                value: city,
                                                child: Text(
                                                  city == 'Bütün Azərbaycan'
                                                      ? 'Azərbaycan'
                                                      : city,
                                                ),
                                              ),
                                            )
                                            .toList(),
                                        onChanged: (value) {
                                          if (value != null) {
                                            elanProvider.setFilters(
                                                city: value);
                                          }
                                        },
                                      ),
                                    ),
                                  ),
                                  // Profile Avatar Button
                                  GestureDetector(
                                    onTap: widget.onNavigateToProfile,
                                    child: Container(
                                      width: 44,
                                      height: 44,
                                      decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: Colors.white,
                                        border: Border.all(
                                          color: const Color(0xFF0FA968)
                                              .withValues(alpha: 0.4),
                                          width: 1.5,
                                        ),
                                        boxShadow: [
                                          BoxShadow(
                                            color: const Color(0xFF007B52)
                                                .withValues(alpha: 0.12),
                                            blurRadius: 10,
                                            offset: const Offset(0, 3),
                                          ),
                                        ],
                                      ),
                                      child: ClipOval(
                                        child: authProvider
                                                        .user?.profil.avatar !=
                                                    null &&
                                                authProvider.user!.profil
                                                    .avatar!.isNotEmpty
                                            ? CachedNetworkImage(
                                                imageUrl: authProvider
                                                    .user!.profil.avatar!,
                                                fit: BoxFit.cover,
                                              )
                                            : const Icon(
                                                Icons.person_rounded,
                                                color: Color(0xFF007B52),
                                                size: 24,
                                              ),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),

                            // 2. Floating Elevated Search Bar overlapping the curved header (ecommerce5.dart + hotel_booking)
                            Padding(
                              padding: const EdgeInsets.fromLTRB(18, 2, 18, 8),
                              child: Row(
                                children: [
                                  Expanded(
                                    child: Container(
                                      height: 50,
                                      decoration: BoxDecoration(
                                        color: Colors.white,
                                        borderRadius: const BorderRadius.all(
                                            Radius.circular(28.0)),
                                        boxShadow: [
                                          BoxShadow(
                                            color: const Color(0xFF17262A)
                                                .withValues(alpha: 0.09),
                                            offset: const Offset(0, 6),
                                            blurRadius: 16.0,
                                          ),
                                        ],
                                      ),
                                      child: Padding(
                                        padding: const EdgeInsets.symmetric(
                                            horizontal: 18),
                                        child: Row(
                                          children: [
                                            Expanded(
                                              child: TextField(
                                                controller: _searchController,
                                                textInputAction:
                                                    TextInputAction.search,
                                                onSubmitted: _submitSearch,
                                                style: const TextStyle(
                                                  fontWeight: FontWeight.w600,
                                                  fontSize: 14.5,
                                                  color: Color(0xFF17262A),
                                                ),
                                                decoration:
                                                    const InputDecoration(
                                                  hintText:
                                                      'Usta və ya xidmət axtar (elektrik, santexnik)...',
                                                  border: InputBorder.none,
                                                  hintStyle: TextStyle(
                                                    fontWeight: FontWeight.w500,
                                                    fontSize: 13.5,
                                                    color: Color(0xFF94A3B8),
                                                  ),
                                                ),
                                                onChanged: _onSearchChanged,
                                              ),
                                            ),
                                            if (_searchController
                                                    .text.isNotEmpty ||
                                                elanProvider
                                                    .searchQuery.isNotEmpty)
                                              GestureDetector(
                                                onTap: () {
                                                  _searchController.clear();
                                                  _submitSearch('');
                                                  setState(() {});
                                                },
                                                child: const Icon(
                                                  Icons.close_rounded,
                                                  size: 19,
                                                  color: Color(0xFF94A3B8),
                                                ),
                                              ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  // Circular Green Search Button
                                  Container(
                                    width: 50,
                                    height: 50,
                                    decoration: BoxDecoration(
                                      gradient: const LinearGradient(
                                        colors: [
                                          Color(0xFF0FA968),
                                          Color(0xFF007B52)
                                        ],
                                        begin: Alignment.topLeft,
                                        end: Alignment.bottomRight,
                                      ),
                                      borderRadius: const BorderRadius.all(
                                          Radius.circular(28.0)),
                                      boxShadow: [
                                        BoxShadow(
                                          color: const Color(0xFF007B52)
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
                                            Radius.circular(28.0)),
                                        onTap: () => _submitSearch(
                                            _searchController.text),
                                        child: const Icon(
                                          Icons.search_rounded,
                                          size: 22,
                                          color: Colors.white,
                                        ),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                // 3. Category Icons Section (Kateqoriyaların İkonları)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(16, 10, 16, 4),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Kateqoriyalar',
                              style: TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 18.5,
                                letterSpacing: 0.2,
                                color: Color(0xFF17262A),
                              ),
                            ),
                            if (widget.onNavigateToCategories != null)
                              InkWell(
                                onTap: widget.onNavigateToCategories,
                                borderRadius: BorderRadius.circular(12),
                                child: const Padding(
                                  padding: EdgeInsets.symmetric(
                                    horizontal: 6,
                                    vertical: 3,
                                  ),
                                  child: Row(
                                    children: [
                                      Text(
                                        'Hamısı',
                                        style: TextStyle(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w600,
                                          color: Color(0xFF007B52),
                                        ),
                                      ),
                                      SizedBox(width: 2),
                                      Icon(
                                        Icons.arrow_forward_rounded,
                                        size: 15,
                                        color: Color(0xFF007B52),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        _buildCategoryIconsGrid(elanProvider),
                      ],
                    ),
                  ),
                ),

                // 4. Standard Listing Grid Section Header
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(18, 12, 18, 8),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            elanProvider.selectedCategoryName ??
                                'Usta Elanları',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontWeight: FontWeight.w700,
                              fontSize: 19,
                              letterSpacing: 0.2,
                              color: Color(0xFF17262A),
                            ),
                          ),
                        ),
                        if (elanProvider.selectedCategorySlug != null ||
                            elanProvider.searchQuery.isNotEmpty ||
                            elanProvider.selectedCity != 'Bütün Azərbaycan')
                          TextButton(
                            onPressed: () {
                              _searchController.clear();
                              elanProvider.resetFilters();
                            },
                            child: const Text(
                              'Sıfırla',
                              style: TextStyle(
                                color: Color(0xFF007B52),
                                fontWeight: FontWeight.w600,
                                fontSize: 13,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),

                // 5. Standard 2-Column Grid (Photo -> Service Name -> Price)
                if (elanProvider.isLoading && displayedElanlar.isEmpty)
                  const SliverFillRemaining(
                    hasScrollBody: false,
                    child: Center(
                      child: CircularProgressIndicator(
                        color: Color(0xFF007B52),
                      ),
                    ),
                  )
                else if (displayedElanlar.isEmpty)
                  SliverFillRemaining(
                    hasScrollBody: false,
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.all(24.0),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(14),
                              decoration: BoxDecoration(
                                color: const Color(0xFFEAF6F1),
                                borderRadius: BorderRadius.circular(16),
                              ),
                              child: const Icon(
                                Icons.search_off_rounded,
                                size: 36,
                                color: Color(0xFF007B52),
                              ),
                            ),
                            const SizedBox(height: 10),
                            const Text(
                              'Uyğun elan tapılmadı',
                              style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF17262A),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  )
                else
                  SliverPadding(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                    sliver: SliverGrid(
                      gridDelegate:
                          const SliverGridDelegateWithMaxCrossAxisExtent(
                        maxCrossAxisExtent: 215,
                        mainAxisSpacing: 14,
                        crossAxisSpacing: 12,
                        mainAxisExtent: 204,
                      ),
                      delegate: SliverChildBuilderDelegate(
                        (context, index) {
                          final elan = displayedElanlar[index];
                          return ElanCard(
                            elan: elan,
                            onTap: () => _openElanDetail(elan),
                            onFavoriteToggle: () => _handleFavorite(elan),
                          );
                        },
                        childCount: displayedElanlar.length,
                      ),
                    ),
                  ),

                if (elanProvider.isLoadingMore)
                  const SliverToBoxAdapter(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 20),
                      child: Center(
                        child: SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: Color(0xFF007B52),
                          ),
                        ),
                      ),
                    ),
                  ),

                const SliverToBoxAdapter(child: SizedBox(height: 100)),
              ],
            ),
          ),
        ),
      ),
    );
  }

  static const List<Map<String, String>> _fallbackCategories = [
    {'ad': 'Elektrik', 'slug': 'elektrik'},
    {'ad': 'Santexnik', 'slug': 'santexnik'},
    {'ad': 'Təmir və tikinti', 'slug': 'temir-ve-tikinti'},
    {'ad': 'Mebel ustası', 'slug': 'mebel'},
    {'ad': 'Məişət texnikası', 'slug': 'meiset-texnikasi'},
    {'ad': 'Rəngsaz', 'slug': 'rengsaz'},
    {'ad': 'Təmizlik', 'slug': 'temizlik'},
    {'ad': 'Digər xidmətlər', 'slug': 'diger'},
  ];

  IconData _getCategoryIcon(String text) {
    final lower = text.toLowerCase();
    if (lower.contains('elektrik') || lower.contains('işıq')) {
      return Icons.electrical_services_rounded;
    }
    if (lower.contains('santexnik') ||
        lower.contains('su ') ||
        lower.contains('kanalizasiya') ||
        lower.contains('kombi')) {
      return Icons.plumbing_rounded;
    }
    if (lower.contains('təmir') ||
        lower.contains('temir') ||
        lower.contains('tikinti') ||
        lower.contains('usta')) {
      return Icons.handyman_rounded;
    }
    if (lower.contains('mebel') || lower.contains('qapı')) {
      return Icons.chair_rounded;
    }
    if (lower.contains('kondisioner') ||
        lower.contains('məişət') ||
        lower.contains('meiset') ||
        lower.contains('texnika') ||
        lower.contains('soyuducu')) {
      return Icons.ac_unit_rounded;
    }
    if (lower.contains('rəng') ||
        lower.contains('reng') ||
        lower.contains('boya') ||
        lower.contains('divar') ||
        lower.contains('oboy')) {
      return Icons.format_paint_rounded;
    }
    if (lower.contains('təmizlik') || lower.contains('temizlik')) {
      return Icons.cleaning_services_rounded;
    }
    if (lower.contains('avto') ||
        lower.contains('maşın') ||
        lower.contains('qaraj')) {
      return Icons.car_repair_rounded;
    }
    if (lower.contains('yük') ||
        lower.contains('yuk') ||
        lower.contains('köçürmə')) {
      return Icons.local_shipping_rounded;
    }
    if (lower.contains('bağ') || lower.contains('bag')) {
      return Icons.yard_rounded;
    }
    return Icons.home_repair_service_rounded;
  }

  Widget _buildCategoryIconsGrid(ElanProvider elanProvider) {
    final cats = elanProvider.categories;
    final items = cats.isNotEmpty
        ? cats
            .take(8)
            .map((c) => {'ad': c.ad, 'slug': c.slug})
            .toList()
        : _fallbackCategories;

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: EdgeInsets.zero,
      itemCount: items.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 4,
        mainAxisSpacing: 10,
        crossAxisSpacing: 10,
        mainAxisExtent: 86,
      ),
      itemBuilder: (context, index) {
        final item = items[index];
        final ad = item['ad']!;
        final slug = item['slug']!;
        final isSelected = elanProvider.selectedCategorySlug == slug;
        final icon = _getCategoryIcon('$ad $slug');

        return Material(
          color: Colors.transparent,
          child: InkWell(
            borderRadius: BorderRadius.circular(16),
            onTap: () {
              if (isSelected) {
                elanProvider.setFilters(clearCategory: true);
              } else {
                elanProvider.setFilters(
                  categorySlug: slug,
                  categoryName: ad,
                );
              }
            },
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 180),
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                    color: isSelected
                        ? const Color(0xFF007B52)
                        : const Color(0xFFEAF6F1),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isSelected
                          ? const Color(0xFF007B52)
                          : const Color(0xFF0FA968).withValues(alpha: 0.25),
                    ),
                    boxShadow: isSelected
                        ? [
                            BoxShadow(
                              color: const Color(0xFF007B52)
                                  .withValues(alpha: 0.28),
                              blurRadius: 8,
                              offset: const Offset(0, 3),
                            ),
                          ]
                        : null,
                  ),
                  child: Icon(
                    icon,
                    size: 25,
                    color: isSelected ? Colors.white : const Color(0xFF007B52),
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  ad,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 11.5,
                    fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                    color: isSelected
                        ? const Color(0xFF007B52)
                        : const Color(0xFF17262A),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
