import 'dart:math' as math;
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
              TargetPlatform.android: CupertinoPageTransitionsBuilder(),
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
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: _buildCurvedBottomBar(context),
    );
  }

  // Inspired by best_flutter_ui_templates/lib/fitness_app/bottom_navigation_view/bottom_bar_view.dart
  Widget _buildCurvedBottomBar(BuildContext context) {
    final bottomPadding = MediaQuery.of(context).padding.bottom;

    return SizedBox(
      height: 88 + bottomPadding,
      child: Stack(
        alignment: AlignmentDirectional.bottomCenter,
        children: [
          AnimatedBuilder(
            animation: _barAnimController,
            builder: (context, _) {
              final radius = CurvedAnimation(
                    parent: _barAnimController,
                    curve: Curves.fastOutSlowIn,
                  ).value *
                  36.0;

              return CustomPaint(
                painter: _ProustaBarShadowPainter(radius: radius),
                child: PhysicalShape(
                  color: Colors.white,
                  elevation: 20.0,
                  shadowColor:
                      const Color(0xFF0A4D34).withValues(alpha: 0.35),
                  clipper: _ProustaTabClipper(radius: radius),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      SizedBox(
                        height: 64,
                        child: Padding(
                          padding:
                              const EdgeInsets.only(left: 8, right: 8, top: 4),
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
                              SizedBox(
                                width: CurvedAnimation(
                                      parent: _barAnimController,
                                      curve: Curves.fastOutSlowIn,
                                    ).value *
                                    68.0,
                              ),
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
                      SizedBox(height: bottomPadding),
                    ],
                  ),
                ),
              );
            },
          ),
          Padding(
            padding: EdgeInsets.only(bottom: bottomPadding + 14),
            child: SizedBox(
              width: 68,
              height: 68,
              child: Padding(
                padding: const EdgeInsets.all(6.0),
                child: ScaleTransition(
                  alignment: Alignment.center,
                  scale: CurvedAnimation(
                    parent: _barAnimController,
                    curve: Curves.fastOutSlowIn,
                  ),
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
                          color:
                              const Color(0xFF007B52).withValues(alpha: 0.48),
                          offset: const Offset(0, 8),
                          blurRadius: 18.0,
                          spreadRadius: 1.0,
                        ),
                      ],
                    ),
                    child: Material(
                      color: Colors.transparent,
                      child: InkWell(
                        customBorder: const CircleBorder(),
                        splashColor: Colors.white.withValues(alpha: 0.2),
                        onTap: () => _setTab(2),
                        child: const Icon(
                          Icons.add_rounded,
                          color: Colors.white,
                          size: 32,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
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
                fontWeight: isSelected ? FontWeight.w800 : FontWeight.w500,
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

/// Paints an upward ambient + direct drop shadow along the curved bottom bar path
class _ProustaBarShadowPainter extends CustomPainter {
  _ProustaBarShadowPainter({this.radius = 36.0});

  final double radius;

  @override
  void paint(Canvas canvas, Size size) {
    final path = _ProustaTabClipper(radius: radius).getClip(size);

    // Soft wide upward ambient shadow
    final ambientShadowPaint = Paint()
      ..color = const Color(0xFF0F172A).withValues(alpha: 0.14)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 14);
    canvas.save();
    canvas.translate(0, -4);
    canvas.drawPath(path, ambientShadowPaint);
    canvas.restore();

    // Closer crisp shadow right under the top edge
    final directShadowPaint = Paint()
      ..color = const Color(0xFF0A4D34).withValues(alpha: 0.12)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6);
    canvas.save();
    canvas.translate(0, -1.5);
    canvas.drawPath(path, directShadowPaint);
    canvas.restore();

    // Subtle crisp top border line so the curve edge is always defined
    final borderPaint = Paint()
      ..color = const Color(0xFFCBD5E1).withValues(alpha: 0.65)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;
    canvas.drawPath(path, borderPaint);
  }

  @override
  bool shouldRepaint(_ProustaBarShadowPainter oldDelegate) =>
      oldDelegate.radius != radius;
}

// Custom notched wave clipper from best_flutter_ui_templates/lib/fitness_app/bottom_navigation_view/bottom_bar_view.dart
class _ProustaTabClipper extends CustomClipper<Path> {
  _ProustaTabClipper({this.radius = 36.0});

  final double radius;

  @override
  Path getClip(Size size) {
    final Path path = Path();
    final double v = radius * 2;

    path.lineTo(0, 0);
    path.arcTo(
      Rect.fromLTWH(0, 0, radius, radius),
      _degreeToRadians(180),
      _degreeToRadians(90),
      false,
    );
    path.arcTo(
      Rect.fromLTWH(
        ((size.width / 2) - v / 2) - radius + v * 0.04,
        0,
        radius,
        radius,
      ),
      _degreeToRadians(270),
      _degreeToRadians(70),
      false,
    );

    path.arcTo(
      Rect.fromLTWH((size.width / 2) - v / 2, -v / 2, v, v),
      _degreeToRadians(160),
      _degreeToRadians(-140),
      false,
    );

    path.arcTo(
      Rect.fromLTWH(
        (size.width - ((size.width / 2) - v / 2)) - v * 0.04,
        0,
        radius,
        radius,
      ),
      _degreeToRadians(200),
      _degreeToRadians(70),
      false,
    );
    path.arcTo(
      Rect.fromLTWH(size.width - radius, 0, radius, radius),
      _degreeToRadians(270),
      _degreeToRadians(90),
      false,
    );
    path.lineTo(size.width, 0);
    path.lineTo(size.width, size.height);
    path.lineTo(0, size.height);

    path.close();
    return path;
  }

  @override
  bool shouldReclip(_ProustaTabClipper oldClipper) =>
      oldClipper.radius != radius;

  double _degreeToRadians(double degree) {
    return (math.pi / 180) * degree;
  }
}
