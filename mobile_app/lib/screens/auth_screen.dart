import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/prousta_wordmark.dart';

class AuthScreen extends StatefulWidget {
  final bool isEmbedded;
  final VoidCallback? onSuccess;

  const AuthScreen({super.key, this.isEmbedded = false, this.onSuccess});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  static const Color _brandPrimary = Color(0xFF007B52);
  static const Color _brandAccent = Color(0xFF0FA968);

  static const List<String> _cities = [
    'Bakı',
    'Sumqayıt',
    'Gəncə',
    'Xırdalan',
    'Mingəçevir',
    'Lənkəran',
    'Şəki',
    'Naxçıvan',
    'Digər',
  ];

  final _formKey = GlobalKey<FormState>();
  bool _isLoginMode = true;
  bool _obscurePassword = true;
  String? _errorMessage;

  // Login controllers
  final _usernameOrEmailController = TextEditingController();
  final _passwordController = TextEditingController();

  // Register controllers
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _adController = TextEditingController();
  final _soyadController = TextEditingController();
  final _telefonController = TextEditingController();
  String _selectedCity = 'Bakı';

  @override
  void dispose() {
    _usernameOrEmailController.dispose();
    _passwordController.dispose();
    _usernameController.dispose();
    _emailController.dispose();
    _adController.dispose();
    _soyadController.dispose();
    _telefonController.dispose();
    super.dispose();
  }

  void _toggleMode(bool isLogin) {
    if (_isLoginMode == isLogin) return;
    setState(() {
      _isLoginMode = isLogin;
      _errorMessage = null;
    });
  }

  void _handleSuccess() {
    if (!mounted) return;
    widget.onSuccess?.call();
    if (!widget.isEmbedded && Navigator.canPop(context)) {
      Navigator.pop(context, true);
    }
  }

  Future<void> _submitForm() async {
    setState(() {
      _errorMessage = null;
    });

    if (!_formKey.currentState!.validate()) {
      return;
    }

    final authProvider = context.read<AuthProvider>();

    try {
      if (_isLoginMode) {
        await authProvider.login(
          _usernameOrEmailController.text.trim(),
          _passwordController.text,
        );
      } else {
        await authProvider.register(
          username: _usernameController.text.trim(),
          email: _emailController.text.trim(),
          password: _passwordController.text,
          ad: _adController.text.trim(),
          soyad: _soyadController.text.trim(),
          telefon: _telefonController.text.trim(),
          sheher: _selectedCity,
        );
      }
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            _isLoginMode
                ? 'Uğurla daxil oldunuz!'
                : 'Qeydiyyat uğurla tamamlandı!',
          ),
          backgroundColor: _brandPrimary,
          behavior: SnackBarBehavior.floating,
        ),
      );
      _handleSuccess();
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      setState(() {
        _errorMessage = message;
      });
    }
  }

  Future<void> _handleGoogleSignIn() async {
    setState(() {
      _errorMessage = null;
    });

    final authProvider = context.read<AuthProvider>();
    try {
      await authProvider.signInWithGoogle();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Google ilə uğurla daxil oldunuz!'),
          backgroundColor: _brandPrimary,
          behavior: SnackBarBehavior.floating,
        ),
      );
      _handleSuccess();
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      setState(() {
        _errorMessage = message;
      });
    }
  }

  InputDecoration _inputDecoration({
    required String label,
    required IconData icon,
    String? hint,
    Widget? suffixIcon,
  }) {
    return InputDecoration(
      labelText: label,
      hintText: hint,
      labelStyle: const TextStyle(
        color: Color(0xFF475569),
        fontSize: 13.5,
        fontWeight: FontWeight.w500,
      ),
      hintStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
      prefixIcon: Icon(icon, color: _brandPrimary, size: 19),
      suffixIcon: suffixIcon,
      filled: true,
      fillColor: const Color(0xFFF8FAFC),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(color: _brandPrimary, width: 1.6),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: BorderSide(color: Colors.red.shade400),
      ),
    );
  }

  // Adapted from flutter_ui_challenges/lib/src/pages/login/auth3.dart
  Widget _buildAuthThreeLayout(BuildContext context) {
    final isLoading = context.watch<AuthProvider>().isLoading;

    return SingleChildScrollView(
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 460),
          child: Column(
            children: [
              // 1. Auth3-style Curved Top Hero Header + Overlapping Form Card
              Stack(
                children: [
                  Container(
                    height: 225,
                    width: double.infinity,
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Color(0xFF0A4D34),
                          Color(0xFF007B52),
                          Color(0xFF0FA968),
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.only(
                        bottomLeft: Radius.circular(36),
                        bottomRight: Radius.circular(36),
                      ),
                    ),
                    child: Stack(
                      children: [
                        Positioned(
                          top: -40,
                          right: -25,
                          child: Container(
                            width: 150,
                            height: 150,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.white.withValues(alpha: 0.08),
                            ),
                          ),
                        ),
                        Positioned(
                          bottom: 30,
                          left: -30,
                          child: Container(
                            width: 110,
                            height: 110,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.white.withValues(alpha: 0.06),
                            ),
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.fromLTRB(22, 24, 22, 0),
                          child: Column(
                            children: [
                              const ProustaWordmark(
                                fontSize: 32,
                                centered: true,
                                lightMode: true,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                _isLoginMode
                                    ? 'Xoş gəlmisiniz! Hesabınıza daxil olun'
                                    : 'Peşəkar usta və müştəri platformasına qoşulun',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: Colors.white.withValues(alpha: 0.9),
                                  fontSize: 13.5,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              const SizedBox(height: 18),
                              // Auth3 Pill Mode Toggle Buttons (Daxil ol / Qeydiyyat)
                              Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: _isLoginMode
                                          ? Colors.white
                                          : Colors.white.withValues(
                                              alpha: 0.16,
                                            ),
                                      foregroundColor: _isLoginMode
                                          ? _brandPrimary
                                          : Colors.white,
                                      elevation: _isLoginMode ? 2 : 0,
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 24,
                                        vertical: 10,
                                      ),
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(
                                          22.0,
                                        ),
                                      ),
                                    ),
                                    onPressed: isLoading
                                        ? null
                                        : () => _toggleMode(true),
                                    child: const Text(
                                      'Daxil ol',
                                      style: TextStyle(
                                        fontWeight: FontWeight.w800,
                                        fontSize: 13.5,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: !_isLoginMode
                                          ? Colors.white
                                          : Colors.white.withValues(
                                              alpha: 0.16,
                                            ),
                                      foregroundColor: !_isLoginMode
                                          ? _brandPrimary
                                          : Colors.white,
                                      elevation: !_isLoginMode ? 2 : 0,
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 24,
                                        vertical: 10,
                                      ),
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(
                                          22.0,
                                        ),
                                      ),
                                    ),
                                    onPressed: isLoading
                                        ? null
                                        : () => _toggleMode(false),
                                    child: const Text(
                                      'Qeydiyyat',
                                      style: TextStyle(
                                        fontWeight: FontWeight.w800,
                                        fontSize: 13.5,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                  // 2. Floating Elevated Form Card overlapping the curved header
                  Container(
                    margin: const EdgeInsets.fromLTRB(16, 165, 16, 16),
                    padding: const EdgeInsets.fromLTRB(20, 22, 20, 22),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(22),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(
                            0xFF0F172A,
                          ).withValues(alpha: 0.08),
                          blurRadius: 24,
                          offset: const Offset(0, 10),
                        ),
                      ],
                    ),
                    child: Form(
                      key: _formKey,
                      child: AnimatedSwitcher(
                        duration: const Duration(milliseconds: 240),
                        child: Column(
                          key: ValueKey<bool>(_isLoginMode),
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // Error Banner
                            if (_errorMessage != null) ...[
                              Container(
                                padding: const EdgeInsets.all(11),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFFEF2F2),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: const Color(0xFFFECACA),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(
                                      Icons.error_outline_rounded,
                                      color: Color(0xFFDC2626),
                                      size: 18,
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        _errorMessage!,
                                        style: const TextStyle(
                                          color: Color(0xFF991B1B),
                                          fontSize: 12.5,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(height: 14),
                            ],

                            // Form Fields
                            if (_isLoginMode) ...[
                              TextFormField(
                                controller: _usernameOrEmailController,
                                textInputAction: TextInputAction.next,
                                style: const TextStyle(fontSize: 14),
                                decoration: _inputDecoration(
                                  label: 'İstifadəçi adı və ya E-poçt',
                                  icon: Icons.person_outline_rounded,
                                ),
                                validator: (value) {
                                  if (value == null || value.trim().isEmpty) {
                                    return 'İstifadəçi adı və ya e-poçt daxil edin';
                                  }
                                  return null;
                                },
                              ),
                              const SizedBox(height: 12),
                            ] else ...[
                              Row(
                                children: [
                                  Expanded(
                                    child: TextFormField(
                                      controller: _adController,
                                      textInputAction: TextInputAction.next,
                                      style: const TextStyle(fontSize: 14),
                                      decoration: _inputDecoration(
                                        label: 'Ad',
                                        icon: Icons.badge_outlined,
                                      ),
                                      validator: (value) {
                                        if (value == null ||
                                            value.trim().isEmpty) {
                                          return 'Ad daxil edin';
                                        }
                                        return null;
                                      },
                                    ),
                                  ),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: TextFormField(
                                      controller: _soyadController,
                                      textInputAction: TextInputAction.next,
                                      style: const TextStyle(fontSize: 14),
                                      decoration: _inputDecoration(
                                        label: 'Soyad',
                                        icon: Icons.badge_outlined,
                                      ),
                                      validator: (value) {
                                        if (value == null ||
                                            value.trim().isEmpty) {
                                          return 'Soyad daxil edin';
                                        }
                                        return null;
                                      },
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              TextFormField(
                                controller: _usernameController,
                                textInputAction: TextInputAction.next,
                                style: const TextStyle(fontSize: 14),
                                decoration: _inputDecoration(
                                  label: 'İstifadəçi adı',
                                  icon: Icons.alternate_email_rounded,
                                ),
                                validator: (value) {
                                  if (value == null || value.trim().isEmpty) {
                                    return 'İstifadəçi adı daxil edin';
                                  }
                                  return null;
                                },
                              ),
                              const SizedBox(height: 12),
                              TextFormField(
                                controller: _emailController,
                                keyboardType: TextInputType.emailAddress,
                                textInputAction: TextInputAction.next,
                                style: const TextStyle(fontSize: 14),
                                decoration: _inputDecoration(
                                  label: 'E-poçt',
                                  icon: Icons.email_outlined,
                                ),
                                validator: (value) {
                                  if (value == null || value.trim().isEmpty) {
                                    return 'E-poçt ünvanı daxil edin';
                                  }
                                  if (!value.contains('@')) {
                                    return 'Düzgün e-poçt ünvanı daxil edin';
                                  }
                                  return null;
                                },
                              ),
                              const SizedBox(height: 12),
                              TextFormField(
                                controller: _telefonController,
                                keyboardType: TextInputType.phone,
                                textInputAction: TextInputAction.next,
                                style: const TextStyle(fontSize: 14),
                                decoration: _inputDecoration(
                                  label: 'Telefon',
                                  hint: '050 123 45 67',
                                  icon: Icons.phone_outlined,
                                ),
                                validator: (value) {
                                  if (value == null || value.trim().isEmpty) {
                                    return 'Telefon nömrəsi daxil edin';
                                  }
                                  return null;
                                },
                              ),
                              const SizedBox(height: 12),
                              DropdownButtonFormField<String>(
                                initialValue: _selectedCity,
                                style: const TextStyle(
                                  fontSize: 14,
                                  color: Color(0xFF0F172A),
                                ),
                                decoration: _inputDecoration(
                                  label: 'Şəhər',
                                  icon: Icons.location_on_outlined,
                                ),
                                items: _cities
                                    .map(
                                      (city) => DropdownMenuItem(
                                        value: city,
                                        child: Text(city),
                                      ),
                                    )
                                    .toList(),
                                onChanged: (val) {
                                  if (val != null) {
                                    setState(() {
                                      _selectedCity = val;
                                    });
                                  }
                                },
                              ),
                              const SizedBox(height: 12),
                            ],

                            // Password field
                            TextFormField(
                              controller: _passwordController,
                              obscureText: _obscurePassword,
                              textInputAction: TextInputAction.done,
                              style: const TextStyle(fontSize: 14),
                              onFieldSubmitted: (_) => _submitForm(),
                              decoration: _inputDecoration(
                                label: 'Şifrə',
                                icon: Icons.lock_outline_rounded,
                                suffixIcon: IconButton(
                                  icon: Icon(
                                    _obscurePassword
                                        ? Icons.visibility_off_outlined
                                        : Icons.visibility_outlined,
                                    color: const Color(0xFF64748B),
                                    size: 19,
                                  ),
                                  onPressed: () {
                                    setState(() {
                                      _obscurePassword = !_obscurePassword;
                                    });
                                  },
                                ),
                              ),
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Şifrə daxil edin';
                                }
                                if (!_isLoginMode && value.length < 6) {
                                  return 'Şifrə ən azı 6 simvol olmalıdır';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 18),

                            // Primary Pill Submit Button (Auth3 style)
                            SizedBox(
                              height: 48,
                              child: ElevatedButton(
                                onPressed: isLoading ? null : _submitForm,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: _brandAccent,
                                  foregroundColor: Colors.white,
                                  elevation: 2,
                                  shadowColor: _brandAccent.withValues(
                                    alpha: 0.4,
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(24),
                                  ),
                                ),
                                child: isLoading
                                    ? const SizedBox(
                                        width: 20,
                                        height: 20,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2.2,
                                          color: Colors.white,
                                        ),
                                      )
                                    : Text(
                                        _isLoginMode
                                            ? 'Daxil ol'
                                            : 'Qeydiyyatdan keç',
                                        style: const TextStyle(
                                          fontSize: 15,
                                          fontWeight: FontWeight.w800,
                                        ),
                                      ),
                              ),
                            ),

                            if (_isLoginMode) ...[
                              const SizedBox(height: 16),
                              Row(
                                children: [
                                  const Expanded(
                                    child: Divider(color: Color(0xFFE2E8F0)),
                                  ),
                                  Padding(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 12,
                                    ),
                                    child: Text(
                                      'və ya',
                                      style: TextStyle(
                                        color: Colors.grey.shade500,
                                        fontSize: 12.5,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ),
                                  const Expanded(
                                    child: Divider(color: Color(0xFFE2E8F0)),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 14),

                              // Auth3-style Pill Google Sign-In Button
                              SizedBox(
                                height: 48,
                                child: OutlinedButton(
                                  onPressed: isLoading
                                      ? null
                                      : _handleGoogleSignIn,
                                  style: OutlinedButton.styleFrom(
                                    foregroundColor: const Color(0xFF1E293B),
                                    backgroundColor: Colors.white,
                                    side: const BorderSide(
                                      color: Color(0xFFCBD5E1),
                                      width: 1.3,
                                    ),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(24),
                                    ),
                                  ),
                                  child: const Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      _GoogleColorIcon(size: 24),
                                      SizedBox(width: 11),
                                      Text(
                                        'Google ilə davam et',
                                        style: TextStyle(
                                          fontSize: 14.5,
                                          fontWeight: FontWeight.w800,
                                          color: Color(0xFF0F172A),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),

              // Compact Trust Badges below card
              Padding(
                padding: const EdgeInsets.only(bottom: 24),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _buildBadge(
                      Icons.verified_user_outlined,
                      'Təhlükəsiz giriş',
                    ),
                    const SizedBox(width: 14),
                    _buildBadge(Icons.sync_rounded, 'Veb ilə eyni hesab'),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBadge(IconData icon, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: _brandPrimary),
        const SizedBox(width: 4),
        Text(
          text,
          style: const TextStyle(
            fontSize: 12,
            color: Color(0xFF64748B),
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    if (widget.isEmbedded) {
      return Container(
        color: const Color(0xFFF6F9F8),
        alignment: Alignment.topCenter,
        child: _buildAuthThreeLayout(context),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFFF6F9F8),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0A4D34),
        foregroundColor: Colors.white,
        elevation: 0,
        title: const ProustaWordmark(fontSize: 22, lightMode: true),
      ),
      body: SafeArea(child: _buildAuthThreeLayout(context)),
    );
  }
}

/// Official 4-color Google "G" icon (Blue, Red, Yellow, Green)
class _GoogleColorIcon extends StatelessWidget {
  final double size;

  const _GoogleColorIcon({this.size = 24});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(painter: _GoogleLogoPainter()),
    );
  }
}

class _GoogleLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final double stroke = size.width * 0.21;
    final Rect arcRect = Rect.fromCircle(
      center: Offset(size.width / 2, size.height / 2),
      radius: (size.width - stroke) / 2,
    );

    final Paint paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = stroke
      ..strokeCap = StrokeCap.butt;

    // Red top arc (-45° to -145°)
    paint.color = const Color(0xFFEA4335);
    canvas.drawArc(arcRect, -0.785, -1.75, false, paint);

    // Yellow left arc (145° to 215°)
    paint.color = const Color(0xFFFBBC05);
    canvas.drawArc(arcRect, 2.53, 1.22, false, paint);

    // Green bottom arc (45° to 145°)
    paint.color = const Color(0xFF34A853);
    canvas.drawArc(arcRect, 0.785, 1.75, false, paint);

    // Blue right arc (-8° to 45°)
    paint.color = const Color(0xFF4285F4);
    canvas.drawArc(arcRect, -0.14, 0.93, false, paint);

    // Blue horizontal crossbar of the "G"
    final Paint barPaint = Paint()
      ..color = const Color(0xFF4285F4)
      ..style = PaintingStyle.fill;
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(
          size.width * 0.50,
          (size.height - stroke * 0.92) / 2,
          size.width * 0.46,
          stroke * 0.92,
        ),
        const Radius.circular(1.5),
      ),
      barPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
