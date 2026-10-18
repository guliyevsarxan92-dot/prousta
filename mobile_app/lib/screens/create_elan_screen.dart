import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/auth_provider.dart';
import '../providers/elan_provider.dart';
import '../services/api_service.dart';
import '../widgets/prousta_wordmark.dart';
import 'auth_screen.dart';

class CreateElanScreen extends StatefulWidget {
  final VoidCallback? onCreated;

  const CreateElanScreen({super.key, this.onCreated});

  @override
  State<CreateElanScreen> createState() => _CreateElanScreenState();
}

class _CreateElanScreenState extends State<CreateElanScreen> {
  static const Color _brandPrimary = Color(0xFF007B52);
  static const Color _brandLight = Color(0xFFEAF6F1);

  final _formKey = GlobalKey<FormState>();
  final _bashliqCtrl = TextEditingController();
  final _qiymetCtrl = TextEditingController();
  final _telefonCtrl = TextEditingController();
  final _acaqlamaCtrl = TextEditingController();

  final ImagePicker _picker = ImagePicker();
  final List<XFile> _images = [];
  final List<Uint8List> _imageBytes = [];

  CategoryModel? _selectedMainCategory;
  CategoryModel? _selectedSubCategory;
  String _selectedCity = 'Bakı';
  bool _isSubmitting = false;
  bool _phonePrefilled = false;

  static const List<String> _cities = [
    'Bakı',
    'Sumqayıt',
    'Gəncə',
    'Xırdalan',
    'Mingəçevir',
    'Lənkəran',
    'Şəki',
    'Quba',
    'Naxçıvan',
    'Şirvan',
    'Yevlax',
    'Şamaxı',
    'Qəbələ',
    'Zaqatala',
    'Bərdə',
    'Sabirabad',
    'Salyan',
    'Masallı',
    'Cəlilabad',
    'Göyçay',
    'Xaçmaz',
    'Qusar',
    'Tovuz',
    'Qazax',
    'Ağcabədi',
    'Şuşa',
    'Xankəndi',
    'Digər',
  ];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final auth = context.read<AuthProvider>();
    if (!_phonePrefilled && auth.user != null) {
      String raw = auth.user!.profil.telefon.replaceAll(RegExp(r'\D'), '');
      if (raw.startsWith('994')) {
        raw = raw.substring(3);
      } else if (raw.startsWith('0') && raw.length == 10) {
        raw = raw.substring(1);
      }
      if (raw.length > 9) {
        raw = raw.substring(raw.length - 9);
      }
      _telefonCtrl.text = raw;
      if (_cities.contains(auth.user!.profil.sheher)) {
        _selectedCity = auth.user!.profil.sheher;
      }
      _phonePrefilled = true;
    }
  }

  @override
  void dispose() {
    _bashliqCtrl.dispose();
    _qiymetCtrl.dispose();
    _telefonCtrl.dispose();
    _acaqlamaCtrl.dispose();
    super.dispose();
  }

  Future<void> _addXFiles(List<XFile> picked) async {
    for (final xfile in picked) {
      if (_images.length >= 5) break;
      final bytes = await xfile.readAsBytes();
      if (!mounted) return;
      setState(() {
        _images.add(xfile);
        _imageBytes.add(bytes);
      });
    }
  }

  Future<void> _pickFromGallery() async {
    if (_images.length >= 5) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Maksimum 5 şəkil əlavə edə bilərsiniz')),
      );
      return;
    }
    try {
      final picked = await _picker.pickMultiImage(
        imageQuality: 82,
        maxWidth: 1600,
      );
      if (picked.isNotEmpty) {
        await _addXFiles(picked);
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Şəkil seçilə bilmədi: $e')),
      );
    }
  }

  Future<void> _pickFromCamera() async {
    if (_images.length >= 5) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Maksimum 5 şəkil əlavə edə bilərsiniz')),
      );
      return;
    }
    try {
      final xfile = await _picker.pickImage(
        source: ImageSource.camera,
        imageQuality: 82,
        maxWidth: 1600,
      );
      if (xfile != null) {
        await _addXFiles([xfile]);
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Kamera açıla bilmədi: $e')),
      );
    }
  }

  void _showImageSourceSheet() {
    if (kIsWeb) {
      _pickFromGallery();
      return;
    }
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Wrap(
            children: [
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: _brandLight,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.photo_library_outlined,
                      color: _brandPrimary),
                ),
                title: const Text(
                  'Qalereyadan seç',
                  style: TextStyle(fontWeight: FontWeight.w700),
                ),
                subtitle: const Text('Cihazdakı şəkillərdən seçin'),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickFromGallery();
                },
              ),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: _brandLight,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.camera_alt_outlined,
                      color: _brandPrimary),
                ),
                title: const Text(
                  'Kamera ilə çək',
                  style: TextStyle(fontWeight: FontWeight.w700),
                ),
                subtitle: const Text('Yeni şəkil çəkərək əlavə edin'),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickFromCamera();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    if (_images.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Zəhmət olmasa ən azı 1 şəkil əlavə edin'),
          backgroundColor: Color(0xFFDC2626),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    final categoryId = _selectedSubCategory?.id ?? _selectedMainCategory?.id;
    if (categoryId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Zəhmət olmasa kateqoriya seçin'),
          backgroundColor: Color(0xFFDC2626),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    setState(() => _isSubmitting = true);
    try {
      await ApiService.createElan(
        bashliq: _bashliqCtrl.text.trim(),
        acaqlama: _acaqlamaCtrl.text.trim(),
        qiymet:
            _qiymetCtrl.text.trim().isEmpty ? null : _qiymetCtrl.text.trim(),
        kategoriId: categoryId,
        sheher: _selectedCity,
        telefon: _telefonCtrl.text.trim(),
        images: _images,
      );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Elanınız uğurla dərc edildi!'),
          backgroundColor: _brandPrimary,
          behavior: SnackBarBehavior.floating,
        ),
      );

      _bashliqCtrl.clear();
      _qiymetCtrl.clear();
      _acaqlamaCtrl.clear();
      setState(() {
        _images.clear();
        _imageBytes.clear();
        _selectedMainCategory = null;
        _selectedSubCategory = null;
      });

      await context.read<ElanProvider>().fetchElanlar(reset: true);
      widget.onCreated?.call();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString().replaceFirst('Exception: ', '')),
          backgroundColor: const Color(0xFFDC2626),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  InputDecoration _inputDecoration({
    required String hint,
    IconData? icon,
    Widget? prefix,
    String? suffixText,
  }) {
    return InputDecoration(
      hintText: hint,
      suffixText: suffixText,
      hintStyle: const TextStyle(
        color: Color(0xFF94A3B8),
        fontSize: 13.5,
      ),
      prefixIcon:
          icon != null ? Icon(icon, color: _brandPrimary, size: 19) : prefix,
      filled: true,
      fillColor: const Color(0xFFF8FAFC),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: _brandPrimary, width: 1.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: Colors.red.shade400),
      ),
    );
  }

  Widget _buildLabel(String text, {bool required = true}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          Text(
            text,
            style: const TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 13.5,
              color: Color(0xFF1E293B),
            ),
          ),
          if (required)
            const Text(
              ' *',
              style: TextStyle(
                color: Color(0xFFDC2626),
                fontWeight: FontWeight.w800,
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isAuthenticated = context.watch<AuthProvider>().isAuthenticated;
    final elanProvider = context.watch<ElanProvider>();
    final categories = elanProvider.categories;

    return Scaffold(
      backgroundColor: const Color(0xFFF6F9F8),
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
                'Yeni Elan',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: _brandPrimary,
                ),
              ),
            ),
          ],
        ),
      ),
      body: !isAuthenticated
          ? _buildLoggedOutState(context)
          : Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 660),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(14),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Card 1: Photos
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  const Row(
                                    children: [
                                      Icon(Icons.photo_camera_back_outlined,
                                          size: 19, color: _brandPrimary),
                                      SizedBox(width: 7),
                                      Text(
                                        'Elan şəkilləri',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w800,
                                          fontSize: 15,
                                          color: Color(0xFF0F172A),
                                        ),
                                      ),
                                    ],
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 3,
                                    ),
                                    decoration: BoxDecoration(
                                      color: _brandLight,
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: Text(
                                      '${_images.length} / 5 şəkil',
                                      style: const TextStyle(
                                        fontSize: 11.5,
                                        fontWeight: FontWeight.w700,
                                        color: _brandPrimary,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              const Text(
                                'İlk seçilən şəkil elanın əsas üz qabığı olacaq (filiqransız orijinal şəkil yükləyin).',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Color(0xFF64748B),
                                ),
                              ),
                              const SizedBox(height: 12),
                              SizedBox(
                                height: 96,
                                child: ListView(
                                  scrollDirection: Axis.horizontal,
                                  children: [
                                    if (_images.length < 5)
                                      Padding(
                                        padding:
                                            const EdgeInsets.only(right: 10),
                                        child: InkWell(
                                          onTap: _showImageSourceSheet,
                                          borderRadius:
                                              BorderRadius.circular(12),
                                          child: Container(
                                            width: 96,
                                            decoration: BoxDecoration(
                                              color: _brandLight
                                                  .withValues(alpha: 0.65),
                                              borderRadius:
                                                  BorderRadius.circular(12),
                                              border: Border.all(
                                                color: _brandPrimary.withValues(
                                                    alpha: 0.35),
                                                width: 1.4,
                                              ),
                                            ),
                                            child: const Column(
                                              mainAxisAlignment:
                                                  MainAxisAlignment.center,
                                              children: [
                                                Icon(
                                                  Icons.add_a_photo_outlined,
                                                  color: _brandPrimary,
                                                  size: 24,
                                                ),
                                                SizedBox(height: 4),
                                                Text(
                                                  'Şəkil seç',
                                                  style: TextStyle(
                                                    fontSize: 11.5,
                                                    color: _brandPrimary,
                                                    fontWeight: FontWeight.w700,
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ),
                                      ),
                                    ..._imageBytes.asMap().entries.map((entry) {
                                      final idx = entry.key;
                                      final bytes = entry.value;
                                      return Padding(
                                        padding:
                                            const EdgeInsets.only(right: 10),
                                        child: Stack(
                                          children: [
                                            ClipRRect(
                                              borderRadius:
                                                  BorderRadius.circular(12),
                                              child: Image.memory(
                                                bytes,
                                                width: 96,
                                                height: 96,
                                                fit: BoxFit.cover,
                                              ),
                                            ),
                                            if (idx == 0)
                                              Positioned(
                                                bottom: 5,
                                                left: 5,
                                                child: Container(
                                                  padding: const EdgeInsets
                                                      .symmetric(
                                                    horizontal: 6,
                                                    vertical: 2,
                                                  ),
                                                  decoration: BoxDecoration(
                                                    color: _brandPrimary,
                                                    borderRadius:
                                                        BorderRadius.circular(
                                                            5),
                                                  ),
                                                  child: const Text(
                                                    'ƏSAS',
                                                    style: TextStyle(
                                                      color: Colors.white,
                                                      fontSize: 9,
                                                      fontWeight:
                                                          FontWeight.w800,
                                                    ),
                                                  ),
                                                ),
                                              ),
                                            Positioned(
                                              top: 4,
                                              right: 4,
                                              child: GestureDetector(
                                                onTap: () {
                                                  setState(() {
                                                    _images.removeAt(idx);
                                                    _imageBytes.removeAt(idx);
                                                  });
                                                },
                                                child: Container(
                                                  padding:
                                                      const EdgeInsets.all(3.5),
                                                  decoration: BoxDecoration(
                                                    color: Colors.black
                                                        .withValues(alpha: 0.6),
                                                    shape: BoxShape.circle,
                                                  ),
                                                  child: const Icon(
                                                    Icons.close_rounded,
                                                    size: 14,
                                                    color: Colors.white,
                                                  ),
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),
                                      );
                                    }),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 12),

                        // Card 2: Category & Title & Price & City
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              _buildLabel('Xidmət kateqoriyası'),
                              DropdownButtonFormField<CategoryModel>(
                                key: ValueKey(
                                    'main_${_selectedMainCategory?.id}'),
                                initialValue: _selectedMainCategory,
                                isExpanded: true,
                                style: const TextStyle(
                                  fontSize: 14,
                                  color: Color(0xFF0F172A),
                                ),
                                decoration: _inputDecoration(
                                  hint: 'Kateqoriya seçin',
                                  icon: Icons.grid_view_rounded,
                                ),
                                items: categories
                                    .map(
                                      (cat) => DropdownMenuItem<CategoryModel>(
                                        value: cat,
                                        child: Text(cat.ad),
                                      ),
                                    )
                                    .toList(),
                                onChanged: (val) {
                                  setState(() {
                                    _selectedMainCategory = val;
                                    _selectedSubCategory = null;
                                  });
                                },
                                validator: (val) => val == null
                                    ? 'Zəhmət olmasa kateqoriya seçin'
                                    : null,
                              ),
                              if (_selectedMainCategory != null &&
                                  _selectedMainCategory!
                                      .altKateqoriyalar.isNotEmpty) ...[
                                const SizedBox(height: 12),
                                _buildLabel('Alt kateqoriya'),
                                DropdownButtonFormField<CategoryModel>(
                                  key: ValueKey(
                                      'sub_${_selectedMainCategory?.id}_${_selectedSubCategory?.id}'),
                                  initialValue: _selectedSubCategory,
                                  isExpanded: true,
                                  style: const TextStyle(
                                    fontSize: 14,
                                    color: Color(0xFF0F172A),
                                  ),
                                  decoration: _inputDecoration(
                                    hint: 'Alt kateqoriya seçin',
                                    icon: Icons.subdirectory_arrow_right_rounded,
                                  ),
                                  items: _selectedMainCategory!.altKateqoriyalar
                                      .map(
                                        (sub) =>
                                            DropdownMenuItem<CategoryModel>(
                                          value: sub,
                                          child: Text(sub.ad),
                                        ),
                                      )
                                      .toList(),
                                  onChanged: (val) {
                                    setState(() {
                                      _selectedSubCategory = val;
                                    });
                                  },
                                  validator: (val) => val == null
                                      ? 'Zəhmət olmasa alt kateqoriya seçin'
                                      : null,
                                ),
                              ],
                              const SizedBox(height: 12),
                              _buildLabel('Elanın başlığı'),
                              TextFormField(
                                controller: _bashliqCtrl,
                                style: const TextStyle(fontSize: 14),
                                decoration: _inputDecoration(
                                  hint: 'Məs: Peşəkar santexnik və kombi ustası',
                                  icon: Icons.title_rounded,
                                ),
                                validator: (val) {
                                  if (val == null || val.trim().length < 5) {
                                    return 'Başlıq ən azı 5 simvol olmalıdır';
                                  }
                                  return null;
                                },
                              ),
                              const SizedBox(height: 12),
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        _buildLabel('Qiymət (AZN)',
                                            required: false),
                                        TextFormField(
                                          controller: _qiymetCtrl,
                                          style: const TextStyle(fontSize: 14),
                                          keyboardType: const TextInputType
                                              .numberWithOptions(decimal: true),
                                          decoration: _inputDecoration(
                                            hint: 'Razılaşma',
                                            icon: Icons.payments_outlined,
                                            suffixText: '₼',
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        _buildLabel('Şəhər'),
                                        DropdownButtonFormField<String>(
                                          initialValue: _selectedCity,
                                          isExpanded: true,
                                          style: const TextStyle(
                                            fontSize: 14,
                                            color: Color(0xFF0F172A),
                                          ),
                                          decoration: _inputDecoration(
                                            hint: 'Şəhər',
                                            icon: Icons.location_on_outlined,
                                          ),
                                          items: _cities
                                              .map(
                                                (c) => DropdownMenuItem(
                                                  value: c,
                                                  child: Text(
                                                    c,
                                                    overflow:
                                                        TextOverflow.ellipsis,
                                                  ),
                                                ),
                                              )
                                              .toList(),
                                          onChanged: (val) {
                                            if (val != null) {
                                              setState(
                                                  () => _selectedCity = val);
                                            }
                                          },
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              _buildLabel('Əlaqə nömrəsi (Zəng və WhatsApp)'),
                              TextFormField(
                                controller: _telefonCtrl,
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                ),
                                keyboardType: TextInputType.phone,
                                inputFormatters: [
                                  FilteringTextInputFormatter.digitsOnly,
                                  LengthLimitingTextInputFormatter(9),
                                ],
                                decoration: _inputDecoration(
                                  hint: '50 123 45 67',
                                  prefix: Container(
                                    width: 64,
                                    alignment: Alignment.center,
                                    margin: const EdgeInsets.only(right: 6),
                                    decoration: const BoxDecoration(
                                      border: Border(
                                        right: BorderSide(
                                            color: Color(0xFFE2E8F0)),
                                      ),
                                    ),
                                    child: const Text(
                                      '+994',
                                      style: TextStyle(
                                        fontWeight: FontWeight.w800,
                                        fontSize: 13.5,
                                        color: _brandPrimary,
                                      ),
                                    ),
                                  ),
                                ),
                                validator: (val) {
                                  final digits =
                                      (val ?? '').replaceAll(RegExp(r'\D'), '');
                                  if (digits.length != 9) {
                                    return '9 rəqəmli mobil nömrə daxil edin (məs: 501234567)';
                                  }
                                  return null;
                                },
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 12),

                        // Card 3: Description & Submit
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              _buildLabel('Xidmət haqqında ətraflı məlumat'),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 11,
                                  vertical: 8,
                                ),
                                margin: const EdgeInsets.only(bottom: 10),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFFFFBEB),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(
                                      color: const Color(0xFFFDE68A)),
                                ),
                                child: const Row(
                                  children: [
                                    Icon(
                                      Icons.info_outline_rounded,
                                      color: Color(0xFFD97706),
                                      size: 17,
                                    ),
                                    SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        'Açıqlama mətnində telefon nömrəsi və ya sayt linki yazmaq qadağandır.',
                                        style: TextStyle(
                                          fontSize: 12,
                                          color: Color(0xFF92400E),
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              TextFormField(
                                controller: _acaqlamaCtrl,
                                maxLines: 4,
                                style: const TextStyle(fontSize: 14),
                                decoration: _inputDecoration(
                                  hint:
                                      'Gördüyünüz işlər, təcrübəniz və zəmanət barədə ətraflı məlumat yazın...',
                                ),
                                validator: (val) {
                                  if (val == null || val.trim().length < 15) {
                                    return 'Açıqlama ən azı 15 simvol olmalıdır';
                                  }
                                  return null;
                                },
                              ),
                              const SizedBox(height: 16),
                              SizedBox(
                                width: double.infinity,
                                height: 50,
                                child: ElevatedButton.icon(
                                  onPressed: _isSubmitting ? null : _submit,
                                  icon: _isSubmitting
                                      ? const SizedBox.shrink()
                                      : const Icon(
                                          Icons.check_circle_outline_rounded,
                                          size: 20,
                                        ),
                                  label: _isSubmitting
                                      ? const SizedBox(
                                          width: 20,
                                          height: 20,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2.2,
                                            color: Colors.white,
                                          ),
                                        )
                                      : const Text(
                                          'Elanı Dərc Et',
                                          style: TextStyle(
                                            fontSize: 15.5,
                                            fontWeight: FontWeight.w800,
                                          ),
                                        ),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: _brandPrimary,
                                    foregroundColor: Colors.white,
                                    elevation: 2,
                                    shadowColor:
                                        _brandPrimary.withValues(alpha: 0.35),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        SizedBox(
                          height: 120 + MediaQuery.of(context).padding.bottom,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
    );
  }

  Widget _buildLoggedOutState(BuildContext context) {
    return Center(
      child: SingleChildScrollView(
        padding: EdgeInsets.fromLTRB(
          20,
          20,
          20,
          120 + MediaQuery.of(context).padding.bottom,
        ),
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
                    Icons.add_business_outlined,
                    size: 30,
                    color: _brandPrimary,
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Pulsuz Elan Yerləşdirin',
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
                  'Xidmətlərinizi minlərlə müştəriyə təqdim etmək və birbaşa sifariş zəngləri qəbul etmək üçün hesabınıza daxil olun.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 13.5,
                    color: Color(0xFF64748B),
                    height: 1.45,
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: const Column(
                    children: [
                      _BenefitRow(text: '4 kateqoriyada pulsuz elan imkanı'),
                      SizedBox(height: 6),
                      _BenefitRow(text: 'Birbaşa Zəng və WhatsApp müraciətləri'),
                      SizedBox(height: 6),
                      _BenefitRow(text: 'Veb sayt və mobil tətbiqdə eyni anda dərc'),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  height: 45,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const AuthScreen()),
                      );
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
}

class _BenefitRow extends StatelessWidget {
  final String text;
  const _BenefitRow({required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const Icon(
          Icons.check_circle_rounded,
          size: 16,
          color: Color(0xFF007B52),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              fontSize: 12.5,
              fontWeight: FontWeight.w600,
              color: Color(0xFF334155),
            ),
          ),
        ),
      ],
    );
  }
}
