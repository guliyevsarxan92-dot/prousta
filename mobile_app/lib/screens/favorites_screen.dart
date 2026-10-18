import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/auth_provider.dart';
import '../providers/elan_provider.dart';
import '../widgets/elan_card.dart';
import '../widgets/prousta_wordmark.dart';
import 'auth_screen.dart';
import 'elan_detail_screen.dart';

class FavoritesScreen extends StatefulWidget {
  final VoidCallback? onNavigateToHome;

  const FavoritesScreen({
    super.key,
    this.onNavigateToHome,
  });

  @override
  State<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  static const Color _brandPrimary = Color(0xFF007B52);
  static const Color _brandLight = Color(0xFFEAF6F1);

  bool _wasAuthenticated = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      final auth = context.read<AuthProvider>();
      if (auth.isAuthenticated) {
        _wasAuthenticated = true;
        context.read<ElanProvider>().loadFavorites();
      }
    });
  }

  Future<void> _refreshFavorites() async {
    if (!context.read<AuthProvider>().isAuthenticated) return;
    await context.read<ElanProvider>().loadFavorites();
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
    final auth = context.watch<AuthProvider>();
    final elanProvider = context.watch<ElanProvider>();

    if (auth.isAuthenticated && !_wasAuthenticated) {
      _wasAuthenticated = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          context.read<ElanProvider>().loadFavorites();
        }
      });
    } else if (!auth.isAuthenticated && _wasAuthenticated) {
      _wasAuthenticated = false;
    }

    final favorites = elanProvider.favorites;

    return Scaffold(
      backgroundColor: const Color(0xFFF7FAF9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        titleSpacing: 18,
        title: Row(
          children: [
            const ProustaWordmark(fontSize: 22),
            const SizedBox(width: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 3),
              decoration: BoxDecoration(
                color: _brandLight,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                'Favorilər',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: _brandPrimary,
                ),
              ),
            ),
          ],
        ),
        actions: [
          if (auth.isAuthenticated)
            IconButton(
              onPressed: _refreshFavorites,
              icon: const Icon(
                Icons.refresh_rounded,
                color: Color(0xFF475569),
                size: 21,
              ),
              tooltip: 'Yenilə',
            ),
        ],
      ),
      body: !auth.isAuthenticated
          ? _buildLoggedOutState(context)
          : RefreshIndicator(
              color: _brandPrimary,
              onRefresh: _refreshFavorites,
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 1080),
                  child: favorites.isEmpty
                      ? _buildEmptyState()
                      : GridView.builder(
                          physics: const AlwaysScrollableScrollPhysics(),
                          padding: const EdgeInsets.fromLTRB(14, 14, 14, 115),
                          gridDelegate:
                              const SliverGridDelegateWithMaxCrossAxisExtent(
                            maxCrossAxisExtent: 215,
                            mainAxisSpacing: 14,
                            crossAxisSpacing: 12,
                            mainAxisExtent: 204,
                          ),
                          itemCount: favorites.length,
                          itemBuilder: (context, index) {
                            final elan = favorites[index];
                            return ElanCard(
                              elan: elan,
                              onTap: () => _openElanDetail(elan),
                              onFavoriteToggle: () async {
                                await context
                                    .read<ElanProvider>()
                                    .toggleFavorite(elan.id);
                              },
                            );
                          },
                        ),
                ),
              ),
            ),
    );
  }

  Widget _buildLoggedOutState(BuildContext context) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 400),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 28),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(22),
              border: Border.all(color: const Color(0xFFE2E8F0)),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF0F172A).withValues(alpha: 0.04),
                  blurRadius: 20,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    color: _brandLight,
                    borderRadius: BorderRadius.circular(18),
                  ),
                  child: const Icon(
                    Icons.favorite_border_rounded,
                    size: 30,
                    color: _brandPrimary,
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Seçilmiş Elanlar',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 19,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                    letterSpacing: -0.3,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Bəyəndiyiniz usta elanlarını favorilərə əlavə etmək və istənilən vaxt baxmaq üçün hesabınıza daxil olun.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 13.5,
                    color: Color(0xFF64748B),
                    height: 1.45,
                  ),
                ),
                const SizedBox(height: 22),
                SizedBox(
                  width: double.infinity,
                  height: 45,
                  child: ElevatedButton.icon(
                    onPressed: () async {
                      await Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const AuthScreen()),
                      );
                      if (mounted) {
                        _refreshFavorites();
                      }
                    },
                    icon: const Icon(Icons.login_rounded, size: 19),
                    label: const Text(
                      'Hesaba daxil ol',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 14,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _brandPrimary,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
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

  Widget _buildEmptyState() {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(24),
      children: [
        const SizedBox(height: 60),
        Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 360),
            child: Container(
              padding: const EdgeInsets.all(26),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const CircleAvatar(
                    radius: 28,
                    backgroundColor: _brandLight,
                    child: Icon(
                      Icons.favorite_border_rounded,
                      size: 26,
                      color: _brandPrimary,
                    ),
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    'Favori elanınız yoxdur',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Elanların üzərindəki ürək işarəsinə toxunaraq onları favorilər siyahısına əlavə edə bilərsiniz.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 13,
                      color: Color(0xFF64748B),
                      height: 1.4,
                    ),
                  ),
                  if (widget.onNavigateToHome != null) ...[
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: widget.onNavigateToHome,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _brandPrimary,
                        foregroundColor: Colors.white,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text(
                        'Elanlara bax',
                        style: TextStyle(fontWeight: FontWeight.w700),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
