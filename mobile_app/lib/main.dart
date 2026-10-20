import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/elan_provider.dart';
import 'screens/home_screen.dart';
import 'screens/categories_screen.dart';
import 'screens/favorites_screen.dart';
import 'screens/create_elan_screen.dart';
import 'screens/messages_screen.dart';
import 'screens/profile_screen.dart';
import 'services/api_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ApiService.init();
  runApp(const ProustaApp());
}

class ProustaApp extends StatelessWidget {
  const ProustaApp({super.key});

  static const Color brandPrimary = Color(0xFF007B52);
  static const Color brandAccent = Color(0xFF0FA968);
  static const Color nearlyWhite = Color(0xFFF7FAF9);
  static const Color darkerText = Color(0xFF17262A);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()..initialize()),
        ChangeNotifierProvider(create: (_) => ElanProvider()..loadInitialData()),
      ],
      child: MaterialApp(
        title: 'prousta.az',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: brandPrimary,
            primary: brandPrimary,
            secondary: brandAccent,
            surface: Colors.white,
          ),
          scaffoldBackgroundColor: nearlyWhite,
          appBarTheme: const AppBarTheme(
            backgroundColor: Colors.white,
            foregroundColor: darkerText,
            elevation: 0,
            scrolledUnderElevation: 0.5,
            surfaceTintColor: Colors.transparent,
          ),
          cardTheme: CardThemeData(
            color: Colors.white,
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
          ),
          pageTransitionsTheme: const PageTransitionsTheme(
            builders: {
              TargetPlatform.android: PredictiveBackPageTransitionsBuilder(),
              TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
              TargetPlatform.linux: FadeUpwardsPageTransitionsBuilder(),
              TargetPlatform.macOS: CupertinoPageTransitionsBuilder(),
              TargetPlatform.windows: FadeUpwardsPageTransitionsBuilder(),
            },
          ),
        ),
        home: const MainNavigationShell(),
      ),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell>
    with TickerProviderStateMixin {
  int _currentIndex = 0;
  late final AnimationController _barAnimController;
  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    _barAnimController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 350),
      value: 1.0,
    );
    _screens = [
      HomeScreen(
        onNavigateToCategories: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => const CategoriesScreen(),
            ),
          );
        },
        onNavigateToCreate: () => _setTab(2),
        onNavigateToProfile: () => _setTab(4),
      ),
      FavoritesScreen(onNavigateToHome: () => _setTab(0)),
      CreateElanScreen(onCreated: () => _setTab(0)),
      const MessagesScreen(),
      ProfileScreen(
        onNavigateToMessages: () => _setTab(3),
      ),
    ];
  }

  @override
  void dispose() {
    _barAnimController.dispose();
    super.dispose();
  }

  void _setTab(int index) {
    if (_currentIndex == index) return;
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true,
      body: _AnimatedIndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: _buildCurvedBottomBar(context),
    );
  }

  // Floating rounded oval bottom navigation bar with soft multi-layer shadow
  Widget _buildCurvedBottomBar(BuildContext context) {
    final bottomPadding = MediaQuery.of(context).padding.bottom;
    final bottomMargin = bottomPadding > 0 ? bottomPadding : 12.0;

    return Container(
      padding: EdgeInsets.only(
        left: 16.0,
        right: 16.0,
        bottom: bottomMargin,
      ),
      child: SizedBox(
        height: 70,
        child: Stack(
          alignment: Alignment.center,
          clipBehavior: Clip.none,
          children: [
            // 1. Oval background card with multi-layer ambient & drop shadow
            Container(
              height: 64,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(32.0),
                boxShadow: [
                  // Wide ambient soft drop shadow (alti kolgeli)
                  BoxShadow(
                    color: const Color(0xFF0F172A).withValues(alpha: 0.12),
                    offset: const Offset(0, 10),
                    blurRadius: 24.0,
                    spreadRadius: 2.0,
                  ),
                  // Dark green tinted directional shadow
                  BoxShadow(
                    color: const Color(0xFF0A4D34).withValues(alpha: 0.10),
                    offset: const Offset(0, 4),
                    blurRadius: 10.0,
                  ),
                ],
                border: Border.all(
                  color: const Color(0xFFE2E8F0).withValues(alpha: 0.8),
                  width: 1.0,
                ),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(32.0),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8.0),
                  child: Row(
                    children: [
                      _buildNavItem(
                        index: 0,
                        icon: Icons.home_outlined,
                        activeIcon: Icons.home_rounded,
                        label: 'Ana səhifə',
                      ),
                      _buildNavItem(
                        index: 1,
                        icon: Icons.favorite_border_rounded,
                        activeIcon: Icons.favorite_rounded,
                        label: 'Favorilər',
                      ),
                      const SizedBox(width: 58.0), // Gap for center floating action button
                      _buildNavItem(
                        index: 3,
                        icon: Icons.chat_bubble_outline_rounded,
                        activeIcon: Icons.chat_bubble_rounded,
                        label: 'Mesajlar',
                      ),
                      _buildNavItem(
                        index: 4,
                        icon: Icons.person_outline_rounded,
                        activeIcon: Icons.person_rounded,
                        label: 'Profil',
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // 2. Center Floating '+' Action Button
            Positioned(
              top: -12,
              child: SizedBox(
                width: 58,
                height: 58,
                child: Container(
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [
                        Color(0xFF0A4D34),
                        Color(0xFF0FA968),
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF007B52).withValues(alpha: 0.42),
                        offset: const Offset(0, 8),
                        blurRadius: 16.0,
                        spreadRadius: 1.0,
                      ),
                      BoxShadow(
                        color: const Color(0xFF0F172A).withValues(alpha: 0.15),
                        offset: const Offset(0, 4),
                        blurRadius: 6.0,
                      ),
                    ],
                    border: Border.all(
                      color: Colors.white,
                      width: 3.5,
                    ),
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      customBorder: const CircleBorder(),
                      splashColor: Colors.white.withValues(alpha: 0.25),
                      onTap: () => _setTab(2),
                      child: const Icon(
                        Icons.add_rounded,
                        color: Colors.white,
                        size: 30,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNavItem({
    required int index,
    required IconData icon,
    required IconData activeIcon,
    required String label,
  }) {
    final isSelected = _currentIndex == index;
    const primary = Color(0xFF007B52);

    return Expanded(
      child: InkWell(
        onTap: () => _setTab(index),
        borderRadius: BorderRadius.circular(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Stack(
              alignment: Alignment.center,
              children: [
                AnimatedScale(
                  scale: isSelected ? 1.08 : 0.96,
                  duration: const Duration(milliseconds: 220),
                  curve: Curves.fastOutSlowIn,
                  child: Icon(
                    isSelected ? activeIcon : icon,
                    size: 24,
                    color: isSelected ? primary : const Color(0xFF78858F),
                  ),
                ),
                if (isSelected)
                  Positioned(
                    top: 0,
                    right: 0,
                    child: Container(
                      width: 6,
                      height: 6,
                      decoration: const BoxDecoration(
                        color: Color(0xFF0FA968),
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 3),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                color: isSelected ? primary : const Color(0xFF78858F),
                letterSpacing: 0.1,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Smooth 60/120 FPS high-performance animated tab switcher
class _AnimatedIndexedStack extends StatefulWidget {
  final int index;
  final List<Widget> children;

  const _AnimatedIndexedStack({
    required this.index,
    required this.children,
  });

  @override
  State<_AnimatedIndexedStack> createState() => _AnimatedIndexedStackState();
}

class _AnimatedIndexedStackState extends State<_AnimatedIndexedStack>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _fadeAnimation;
  late final Animation<Offset> _slideAnimation;
  late int _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.index;
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 240),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    );
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.025),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));
    _controller.forward();
  }

  @override
  void didUpdateWidget(covariant _AnimatedIndexedStack oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.index != oldWidget.index) {
      _currentIndex = widget.index;
      _controller.forward(from: 0.0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: SlideTransition(
        position: _slideAnimation,
        child: IndexedStack(
          index: _currentIndex,
          children: widget.children,
        ),
      ),
    );
  }
}
