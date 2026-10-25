import 'dart:typed_data';
import '../widgets/picked_image.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/models.dart';
import '../providers/auth_provider.dart';
import '../providers/elan_provider.dart';
import '../services/api_service.dart';
import '../widgets/elan_card.dart';
import 'auth_screen.dart';
import 'elan_detail_screen.dart';
import 'vip_payment_screen.dart';

class ProfileScreen extends StatefulWidget {
  final VoidCallback? onNavigateToMessages;

  const ProfileScreen({super.key, this.onNavigateToMessages});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  List<ElanModel> _myElanlar = [];
  bool _wasAuthenticated = false;
  int _unreadMessagesCount = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (ApiService.isAuthenticated) {
        _wasAuthenticated = true;
        _loadProfileData();
      }
    });
  }

  Future<void> _loadProfileData() async {
    if (!ApiService.isAuthenticated) return;
    await Future.wait([
      context.read<AuthProvider>().refreshProfile(),
      context.read<ElanProvider>().loadFavorites(),
      _fetchMyElanlar(),
      _fetchUnreadCount(),
    ]);
  }

  Future<void> _fetchMyElanlar() async {
    try {
      final list = await ApiService.getMyElanlar();
      if (mounted) {
        setState(() {
          _myElanlar = list;
        });
      }
    } catch (_) {}
  }

  Future<void> _fetchUnreadCount() async {
    try {
      final convs = await ApiService.getConversations();
      final totalUnread = convs.fold<int>(
        0,
        (sum, item) => sum + item.unreadCount,
      );
      if (mounted) {
        setState(() {
          _unreadMessagesCount = totalUnread;
        });
      }
    } catch (_) {}
  }

  Future<void> _showEditElanSheet(ElanModel elan) async {
    ElanModel fullElan = elan;
    if (elan.acaqlama == null || elan.acaqlama!.trim().isEmpty) {
      try {
        fullElan = await ApiService.getElanDetail(elan.id);
      } catch (_) {}
    }
    if (!mounted) return;

    final bashliqCtrl = TextEditingController(text: fullElan.bashliq);
    final qiymetCtrl = TextEditingController(
      text: fullElan.qiymet != null && fullElan.qiymet! > 0
          ? fullElan.qiymet!.toStringAsFixed(
              fullElan.qiymet! == fullElan.qiymet!.roundToDouble() ? 0 : 2,
            )
          : '',
    );
    final sheherCtrl = TextEditingController(text: fullElan.sheher);
    final telefonCtrl = TextEditingController(text: fullElan.telefon);
    final acaqlamaCtrl = TextEditingController(text: fullElan.acaqlama ?? '');
    // Existing photos and new photos
    final existingImages = List<ElanShekilModel>.from(fullElan.shekillar);
    final deleteImageIds = <int>[];
    final newImageFiles = <XFile>[];
    bool isSaving = false;

    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFFF7FAF9),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(22)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setModalState) {
            return DraggableScrollableSheet(
              initialChildSize: 0.9,
              minChildSize: 0.5,
              maxChildSize: 0.96,
              expand: false,
              builder: (ctx, scrollCtrl) {
                return Container(
                  decoration: const BoxDecoration(
                    color: Color(0xFFF7FAF9),
                    borderRadius: BorderRadius.vertical(
                      top: Radius.circular(22),
                    ),
                  ),
                  child: Column(
                    children: [
                      // Header
                      Padding(
                        padding: const EdgeInsets.fromLTRB(20, 14, 14, 10),
                        child: Row(
                          children: [
                            Container(
                              width: 36,
                              height: 36,
                              decoration: BoxDecoration(
                                color: const Color(0xFFEAF6F1),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Icon(
                                Icons.edit_note_rounded,
                                color: Color(0xFF007B52),
                                size: 22,
                              ),
                            ),
                            const SizedBox(width: 12),
                            const Expanded(
                              child: Text(
                                'Elana düzəliş et',
                                style: TextStyle(
                                  fontSize: 17,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                            ),
                            IconButton(
                              onPressed: () => Navigator.pop(ctx),
                              icon: const Icon(Icons.close_rounded),
                            ),
                          ],
                        ),
                      ),
                      const Divider(height: 1, color: Color(0xFFE2E8F0)),

                      // Form Content
                      Expanded(
                        child: ListView(
                          controller: scrollCtrl,
                          padding: const EdgeInsets.fromLTRB(18, 16, 18, 24),
                          children: [
                            // 1. Photos Section
                            const Text(
                              'Xidmət Şəkilləri',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                            const SizedBox(height: 4),
                            const Text(
                              'Köhnə şəkilləri silə və ya yenilərini əlavə edə bilərsiniz',
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
                                  // Add photo button
                                  InkWell(
                                    onTap: () async {
                                      final picker = ImagePicker();
                                      final picked = await picker
                                          .pickMultiImage();
                                      if (picked.isNotEmpty) {
                                        setModalState(() {
                                          newImageFiles.addAll(picked);
                                        });
                                      }
                                    },
                                    borderRadius: BorderRadius.circular(14),
                                    child: Container(
                                      width: 96,
                                      height: 96,
                                      margin: const EdgeInsets.only(right: 10),
                                      decoration: BoxDecoration(
                                        color: Colors.white,
                                        borderRadius: BorderRadius.circular(14),
                                        border: Border.all(
                                          color: const Color(0xFF0FA968),
                                          style: BorderStyle.solid,
                                          width: 1.5,
                                        ),
                                      ),
                                      child: const Column(
                                        mainAxisAlignment:
                                            MainAxisAlignment.center,
                                        children: [
                                          Icon(
                                            Icons.add_a_photo_outlined,
                                            color: Color(0xFF007B52),
                                            size: 26,
                                          ),
                                          SizedBox(height: 4),
                                          Text(
                                            'Foto əlavə et',
                                            style: TextStyle(
                                              fontSize: 10.5,
                                              fontWeight: FontWeight.w600,
                                              color: Color(0xFF007B52),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),

                                  // Existing Photos
                                  ...existingImages.map((shk) {
                                    return Container(
                                      width: 96,
                                      height: 96,
                                      margin: const EdgeInsets.only(right: 10),
                                      child: Stack(
                                        children: [
                                          ClipRRect(
                                            borderRadius: BorderRadius.circular(
                                              14,
                                            ),
                                            child: CachedNetworkImage(
                                              imageUrl: shk.shekilUrl ?? '',
                                              width: 96,
                                              height: 96,
                                              fit: BoxFit.cover,
                                              placeholder: (context, url) =>
                                                  Container(
                                                    color: const Color(
                                                      0xFFE2E8F0,
                                                    ),
                                                  ),
                                              errorWidget:
                                                  (
                                                    context,
                                                    url,
                                                    error,
                                                  ) => Container(
                                                    color: const Color(
                                                      0xFFE2E8F0,
                                                    ),
                                                    child: const Icon(
                                                      Icons
                                                          .image_not_supported_outlined,
                                                    ),
                                                  ),
                                            ),
                                          ),
                                          Positioned(
                                            top: 4,
                                            right: 4,
                                            child: GestureDetector(
                                              onTap: () {
                                                setModalState(() {
                                                  existingImages.remove(shk);
                                                  deleteImageIds.add(shk.id);
                                                });
                                              },
                                              child: Container(
                                                padding: const EdgeInsets.all(
                                                  4,
                                                ),
                                                decoration: const BoxDecoration(
                                                  color: Colors.black54,
                                                  shape: BoxShape.circle,
                                                ),
                                                child: const Icon(
                                                  Icons.close_rounded,
                                                  color: Colors.white,
                                                  size: 14,
                                                ),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    );
                                  }),

                                  // Newly picked photos
                                  ...newImageFiles.map((file) {
                                    return Container(
                                      width: 96,
                                      height: 96,
                                      margin: const EdgeInsets.only(right: 10),
                                      child: Stack(
                                        children: [
                                          ClipRRect(
                                            borderRadius: BorderRadius.circular(
                                              14,
                                            ),
                                            child: PickedImage(
                                              file,
                                              width: 96,
                                              height: 96,
                                              fit: BoxFit.cover,
                                            ),
                                          ),
                                          Positioned(
                                            top: 4,
                                            right: 4,
                                            child: GestureDetector(
                                              onTap: () {
                                                setModalState(() {
                                                  newImageFiles.remove(file);
                                                });
                                              },
                                              child: Container(
                                                padding: const EdgeInsets.all(
                                                  4,
                                                ),
                                                decoration: const BoxDecoration(
                                                  color: Colors.black54,
                                                  shape: BoxShape.circle,
                                                ),
                                                child: const Icon(
                                                  Icons.close_rounded,
                                                  color: Colors.white,
                                                  size: 14,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            bottom: 4,
                                            left: 4,
                                            child: Container(
                                              padding:
                                                  const EdgeInsets.symmetric(
                                                    horizontal: 5,
                                                    vertical: 2,
                                                  ),
                                              decoration: BoxDecoration(
                                                color: const Color(0xFF007B52),
                                                borderRadius:
                                                    BorderRadius.circular(6),
                                              ),
                                              child: const Text(
                                                'Yeni',
                                                style: TextStyle(
                                                  fontSize: 9,
                                                  fontWeight: FontWeight.w700,
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
                            const SizedBox(height: 20),

                            // 2. Title
                            TextField(
                              controller: bashliqCtrl,
                              decoration: InputDecoration(
                                labelText: 'Xidmətin adı (Başlıq)',
                                filled: true,
                                fillColor: Colors.white,
                                isDense: true,
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(14),
                                  borderSide: const BorderSide(
                                    color: Color(0xFFE2E8F0),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(height: 14),

                            // 3. Price & City
                            Row(
                              children: [
                                Expanded(
                                  child: TextField(
                                    controller: qiymetCtrl,
                                    keyboardType: TextInputType.number,
                                    decoration: InputDecoration(
                                      labelText: 'Qiymət (AZN)',
                                      filled: true,
                                      fillColor: Colors.white,
                                      isDense: true,
                                      border: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(14),
                                        borderSide: const BorderSide(
                                          color: Color(0xFFE2E8F0),
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: TextField(
                                    controller: sheherCtrl,
                                    decoration: InputDecoration(
                                      labelText: 'Şəhər',
                                      filled: true,
                                      fillColor: Colors.white,
                                      isDense: true,
                                      border: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(14),
                                        borderSide: const BorderSide(
                                          color: Color(0xFFE2E8F0),
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 14),

                            // 4. Phone
                            TextField(
                              controller: telefonCtrl,
                              keyboardType: TextInputType.phone,
                              decoration: InputDecoration(
                                labelText: 'Telefon nömrəsi',
                                filled: true,
                                fillColor: Colors.white,
                                isDense: true,
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(14),
                                  borderSide: const BorderSide(
                                    color: Color(0xFFE2E8F0),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(height: 14),

                            // 5. Description
                            TextField(
                              controller: acaqlamaCtrl,
                              maxLines: 4,
                              decoration: InputDecoration(
                                labelText: 'Xidmət haqqında ətraflı məlumat',
                                filled: true,
                                fillColor: Colors.white,
                                isDense: true,
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(14),
                                  borderSide: const BorderSide(
                                    color: Color(0xFFE2E8F0),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(height: 22),

                            // Submit Button
                            SizedBox(
                              width: double.infinity,
                              height: 50,
                              child: ElevatedButton(
                                onPressed: isSaving
                                    ? null
                                    : () async {
                                        setModalState(() => isSaving = true);
                                        try {
                                          final updated =
                                              await ApiService.updateElan(
                                                id: elan.id,
                                                bashliq: bashliqCtrl.text
                                                    .trim(),
                                                acaqlama: acaqlamaCtrl.text
                                                    .trim(),
                                                qiymet: qiymetCtrl.text.trim(),
                                                sheher: sheherCtrl.text.trim(),
                                                telefon: telefonCtrl.text
                                                    .trim(),
                                                newImages:
                                                    newImageFiles.isNotEmpty
                                                    ? newImageFiles
                                                    : null,
                                                deleteImageIds:
                                                    deleteImageIds.isNotEmpty
                                                    ? deleteImageIds
                                                    : null,
                                              );
                                          if (mounted) {
                                            setState(() {
                                              final idx = _myElanlar.indexWhere(
                                                (e) => e.id == elan.id,
                                              );
                                              if (idx != -1) {
                                                _myElanlar[idx] = updated;
                                              }
                                            });
                                            context
                                                .read<ElanProvider>()
                                                .fetchElanlar(reset: true);
                                          }
                                          if (!ctx.mounted) return;
                                          Navigator.pop(ctx);
                                          if (!mounted) return;
                                          ScaffoldMessenger.of(
                                            context,
                                          ).showSnackBar(
                                            const SnackBar(
                                              content: Text(
                                                'Elan və şəkillər uğurla yeniləndi!',
                                              ),
                                              backgroundColor: Color(
                                                0xFF007B52,
                                              ),
                                            ),
                                          );
                                        } catch (e) {
                                          if (ctx.mounted) {
                                            setModalState(
                                              () => isSaving = false,
                                            );
                                          }
                                          if (!mounted) return;
                                          ScaffoldMessenger.of(
                                            context,
                                          ).showSnackBar(
                                            SnackBar(
                                              content: Text(
                                                e.toString().replaceFirst(
                                                  'Exception: ',
                                                  '',
                                                ),
                                              ),
                                              backgroundColor: Colors.redAccent,
                                            ),
                                          );
                                        }
                                      },
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF007B52),
                                  foregroundColor: Colors.white,
                                  elevation: 2,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(14),
                                  ),
                                ),
                                child: isSaving
                                    ? const SizedBox(
                                        width: 22,
                                        height: 22,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2.2,
                                          color: Colors.white,
                                        ),
                                      )
                                    : const Text(
                                        'Yadda saxla',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w700,
                                          fontSize: 15.5,
                                        ),
                                      ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            );
          },
        );
      },
    );
  }

  Future<void> _confirmDeleteElan(ElanModel elan) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Elanı sil'),
        content: Text(
          '"${elan.bashliq}" elanını silmək istədiyinizə əminsiniz?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Ləğv et'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.redAccent,
              foregroundColor: Colors.white,
            ),
            child: const Text('Sil'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    try {
      await ApiService.deleteElan(elan.id);
      if (!mounted) return;
      setState(() {
        _myElanlar.removeWhere((e) => e.id == elan.id);
      });
      await context.read<ElanProvider>().fetchElanlar(reset: true);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Elan silindi'),
          backgroundColor: Color(0xFF007B52),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString().replaceFirst('Exception: ', '')),
          backgroundColor: Colors.redAccent,
        ),
      );
    }
  }

  void _showEditProfileSheet(AppUser user) {
    final adCtrl = TextEditingController(text: user.profil.ad);
    final soyadCtrl = TextEditingController(text: user.profil.soyad);
    final telefonCtrl = TextEditingController(text: user.profil.telefon);
    final sheherCtrl = TextEditingController(text: user.profil.sheher);
    XFile? pickedAvatar;
    Uint8List? pickedAvatarBytes;
    bool isSaving = false;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setModalState) {
            Future<void> pickImage() async {
              final xfile = await ImagePicker().pickImage(
                source: ImageSource.gallery,
                imageQuality: 82,
              );
              if (xfile != null) {
                final bytes = await xfile.readAsBytes();
                if (!ctx.mounted) return;
                setModalState(() {
                  pickedAvatar = xfile;
                  pickedAvatarBytes = bytes;
                });
              }
            }

            return Padding(
              padding: EdgeInsets.only(
                left: 20,
                right: 20,
                top: 20,
                bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Profil Tənzimləmələri',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        IconButton(
                          onPressed: () => Navigator.pop(ctx),
                          icon: const Icon(Icons.close_rounded),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Center(
                      child: GestureDetector(
                        onTap: pickImage,
                        child: Stack(
                          children: [
                            CircleAvatar(
                              radius: 42,
                              backgroundColor: const Color(0xFFEAF6F1),
                              backgroundImage: pickedAvatar != null
                                  ? MemoryImage(pickedAvatarBytes!)
                                        as ImageProvider
                                  : (user.profil.avatar != null &&
                                        user.profil.avatar!.isNotEmpty)
                                  ? CachedNetworkImageProvider(
                                      user.profil.avatar!,
                                    )
                                  : null,
                              child:
                                  (pickedAvatar == null &&
                                      (user.profil.avatar == null ||
                                          user.profil.avatar!.isEmpty))
                                  ? Text(
                                      user.fullName.isNotEmpty
                                          ? user.fullName[0].toUpperCase()
                                          : 'U',
                                      style: const TextStyle(
                                        fontSize: 28,
                                        fontWeight: FontWeight.w800,
                                        color: Color(0xFF007B52),
                                      ),
                                    )
                                  : null,
                            ),
                            Positioned(
                              bottom: 0,
                              right: 0,
                              child: Container(
                                padding: const EdgeInsets.all(6),
                                decoration: const BoxDecoration(
                                  color: Color(0xFF007B52),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(
                                  Icons.camera_alt_rounded,
                                  color: Colors.white,
                                  size: 16,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: adCtrl,
                            decoration: InputDecoration(
                              labelText: 'Ad',
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: TextField(
                            controller: soyadCtrl,
                            decoration: InputDecoration(
                              labelText: 'Soyad',
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: telefonCtrl,
                      keyboardType: TextInputType.phone,
                      decoration: InputDecoration(
                        labelText: 'Telefon',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: sheherCtrl,
                      decoration: InputDecoration(
                        labelText: 'Şəhər',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton(
                        onPressed: isSaving
                            ? null
                            : () async {
                                setModalState(() => isSaving = true);
                                try {
                                  await context
                                      .read<AuthProvider>()
                                      .updateProfile(
                                        ad: adCtrl.text.trim(),
                                        soyad: soyadCtrl.text.trim(),
                                        telefon: telefonCtrl.text.trim(),
                                        sheher: sheherCtrl.text.trim(),
                                        avatarFile: pickedAvatar,
                                      );
                                  if (!ctx.mounted) return;
                                  Navigator.pop(ctx);
                                  if (!mounted) return;
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Profil yeniləndi!'),
                                      backgroundColor: Color(0xFF007B52),
                                    ),
                                  );
                                } catch (e) {
                                  if (ctx.mounted) {
                                    setModalState(() => isSaving = false);
                                  }
                                  if (!mounted) return;
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(
                                        e.toString().replaceFirst(
                                          'Exception: ',
                                          '',
                                        ),
                                      ),
                                      backgroundColor: Colors.redAccent,
                                    ),
                                  );
                                }
                              },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF007B52),
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: isSaving
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Text(
                                'Yadda saxla',
                                style: TextStyle(
                                  fontWeight: FontWeight.w800,
                                  fontSize: 15,
                                ),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  void _showMyElanlarSheet(AppUser user, String cityDisplay) {
    final totalViews = _myElanlar.fold<int>(
      0,
      (sum, item) => sum + item.baxishSayi,
    );
    final totalZeng = _myElanlar.fold<int>(
      0,
      (sum, item) => sum + item.zengSayi,
    );
    final totalWp = _myElanlar.fold<int>(0, (sum, item) => sum + item.wpSayi);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFFF4F8F6),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(22)),
      ),
      builder: (ctx) {
        return DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.85,
          maxChildSize: 0.94,
          minChildSize: 0.50,
          builder: (_, scrollCtrl) {
            return Column(
              children: [
                // Header
                Container(
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.vertical(
                      top: Radius.circular(22),
                    ),
                  ),
                  padding: const EdgeInsets.fromLTRB(18, 12, 10, 10),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 34,
                            height: 34,
                            decoration: BoxDecoration(
                              color: const Color(0xFFEAF6F1),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Icon(
                              Icons.assignment_outlined,
                              color: Color(0xFF007B52),
                              size: 19,
                            ),
                          ),
                          const SizedBox(width: 10),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Elanlarım (${_myElanlar.length})',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                              Text(
                                '${user.fullName} • $cityDisplay',
                                style: const TextStyle(
                                  fontSize: 11.5,
                                  fontWeight: FontWeight.w600,
                                  color: Color(0xFF64748B),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      IconButton(
                        onPressed: () => Navigator.pop(ctx),
                        icon: const Icon(Icons.close_rounded),
                      ),
                    ],
                  ),
                ),
                const Divider(height: 1, color: Color(0xFFE2E8F0)),

                // Overall Usta Info: Baxış, Zəng, WhatsApp
                Container(
                  margin: const EdgeInsets.fromLTRB(14, 10, 14, 4),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [
                        Color(0xFF0A4D34),
                        Color(0xFF007B52),
                        Color(0xFF0FA968),
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(14),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF007B52).withValues(alpha: 0.22),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: _buildUstaStatBox(
                          icon: Icons.visibility_rounded,
                          value: '$totalViews',
                          label: 'Baxış',
                        ),
                      ),
                      Container(
                        width: 1,
                        height: 30,
                        color: Colors.white.withValues(alpha: 0.22),
                      ),
                      Expanded(
                        child: _buildUstaStatBox(
                          icon: Icons.phone_callback_rounded,
                          value: '$totalZeng',
                          label: 'Zəng',
                        ),
                      ),
                      Container(
                        width: 1,
                        height: 30,
                        color: Colors.white.withValues(alpha: 0.22),
                      ),
                      Expanded(
                        child: _buildUstaStatBox(
                          icon: Icons.chat_rounded,
                          value: '$totalWp',
                          label: 'WhatsApp',
                        ),
                      ),
                    ],
                  ),
                ),

                // Compact 2-Column Vertical Listings Grid (yığcam, 2 elan aşağı doğru)
                Expanded(
                  child: _myElanlar.isEmpty
                      ? const Center(
                          child: Text(
                            'Hələ elanınız yoxdur',
                            style: TextStyle(
                              color: Color(0xFF64748B),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        )
                      : GridView.builder(
                          controller: scrollCtrl,
                          padding: const EdgeInsets.fromLTRB(12, 8, 12, 24),
                          gridDelegate:
                              const SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: 2,
                                mainAxisSpacing: 10,
                                crossAxisSpacing: 10,
                                mainAxisExtent: 206,
                              ),
                          itemCount: _myElanlar.length,
                          itemBuilder: (context, index) {
                            final elan = _myElanlar[index];
                            return Container(
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(14),
                                boxShadow: [
                                  BoxShadow(
                                    color: const Color(
                                      0xFF0F172A,
                                    ).withValues(alpha: 0.12),
                                    blurRadius: 12,
                                    offset: const Offset(0, 4),
                                  ),
                                ],
                              ),
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(14),
                                child: Column(
                                  crossAxisAlignment:
                                      CrossAxisAlignment.stretch,
                                  children: [
                                    // Compact ElanCard (Photo + Title + Price)
                                    Expanded(
                                      child: ElanCard(
                                        elan: elan,
                                        onTap: () {
                                          Navigator.pop(ctx);
                                          Navigator.push(
                                            context,
                                            MaterialPageRoute(
                                              builder: (_) => ElanDetailScreen(
                                                elanId: elan.id,
                                                initialElan: elan,
                                              ),
                                            ),
                                          );
                                        },
                                      ),
                                    ),
                                    // Per-listing Compact Stats: Baxış, Telefon, WhatsApp
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 8,
                                        vertical: 4,
                                      ),
                                      decoration: const BoxDecoration(
                                        color: Color(0xFFF4FAF7),
                                        border: Border(
                                          top: BorderSide(
                                            color: Color(0xFFE2E8F0),
                                          ),
                                        ),
                                      ),
                                      child: Row(
                                        mainAxisAlignment:
                                            MainAxisAlignment.spaceEvenly,
                                        children: [
                                          _buildMiniStat(
                                            Icons.visibility_outlined,
                                            '${elan.baxishSayi}',
                                            const Color(0xFF007B52),
                                          ),
                                          _buildMiniStat(
                                            Icons.phone_in_talk_outlined,
                                            '${elan.zengSayi}',
                                            const Color(0xFF0FA968),
                                          ),
                                          _buildMiniStat(
                                            Icons.chat_bubble_outline_rounded,
                                            '${elan.wpSayi}',
                                            const Color(0xFF16A34A),
                                          ),
                                        ],
                                      ),
                                    ),
                                    // Compact Actions Row: Düzəliş | VİP | Sil
                                    Padding(
                                      padding: const EdgeInsets.fromLTRB(
                                        5,
                                        4,
                                        5,
                                        5,
                                      ),
                                      child: Row(
                                        children: [
                                          // 1. Düzəliş (Edit)
                                          Expanded(
                                            child: InkWell(
                                              borderRadius:
                                                  BorderRadius.circular(7),
                                              onTap: () {
                                                Navigator.pop(ctx);
                                                _showEditElanSheet(elan);
                                              },
                                              child: Container(
                                                padding:
                                                    const EdgeInsets.symmetric(
                                                      vertical: 5,
                                                    ),
                                                decoration: BoxDecoration(
                                                  color: const Color(
                                                    0xFFEAF6F1,
                                                  ),
                                                  borderRadius:
                                                      BorderRadius.circular(7),
                                                ),
                                                child: const Row(
                                                  mainAxisAlignment:
                                                      MainAxisAlignment.center,
                                                  children: [
                                                    Icon(
                                                      Icons.edit_outlined,
                                                      size: 12,
                                                      color: Color(0xFF007B52),
                                                    ),
                                                    SizedBox(width: 2),
                                                    Text(
                                                      'Düzəliş',
                                                      style: TextStyle(
                                                        fontSize: 10.5,
                                                        fontWeight:
                                                            FontWeight.w800,
                                                        color: Color(
                                                          0xFF007B52,
                                                        ),
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ),
                                            ),
                                          ),
                                          if (!elan.isVip) ...[
                                            const SizedBox(width: 4),
                                            // 2. VİP (yalnız VİP olmayan elanlarda)
                                            Expanded(
                                              child: InkWell(
                                                borderRadius:
                                                    BorderRadius.circular(7),
                                                onTap: () async {
                                                  Navigator.pop(ctx);
                                                  final updated =
                                                      await Navigator.push<
                                                        bool
                                                      >(
                                                        context,
                                                        MaterialPageRoute(
                                                          builder: (_) =>
                                                              VipPaymentScreen(
                                                                elanId: elan.id,
                                                                elanTitle: elan
                                                                    .bashliq,
                                                                initialType:
                                                                    'vip',
                                                              ),
                                                        ),
                                                      );
                                                  if (updated == true &&
                                                      mounted) {
                                                    _fetchMyElanlar();
                                                  }
                                                },
                                                child: Container(
                                                  padding:
                                                      const EdgeInsets.symmetric(
                                                        vertical: 5,
                                                      ),
                                                  decoration: BoxDecoration(
                                                    color: const Color(
                                                      0xFFFEF3C7,
                                                    ),
                                                    borderRadius:
                                                        BorderRadius.circular(
                                                          7,
                                                        ),
                                                  ),
                                                  child: const Row(
                                                    mainAxisAlignment:
                                                        MainAxisAlignment
                                                            .center,
                                                    children: [
                                                      Icon(
                                                        Icons
                                                            .workspace_premium_rounded,
                                                        size: 12,
                                                        color: Color(
                                                          0xFFD97706,
                                                        ),
                                                      ),
                                                      SizedBox(width: 2),
                                                      Text(
                                                        'VİP',
                                                        style: TextStyle(
                                                          fontSize: 10.5,
                                                          fontWeight:
                                                              FontWeight.w800,
                                                          color: Color(
                                                            0xFFB45309,
                                                          ),
                                                        ),
                                                      ),
                                                    ],
                                                  ),
                                                ),
                                              ),
                                            ),
                                          ],
                                          const SizedBox(width: 4),
                                          // 3. Sil
                                          InkWell(
                                            borderRadius: BorderRadius.circular(
                                              7,
                                            ),
                                            onTap: () {
                                              Navigator.pop(ctx);
                                              _confirmDeleteElan(elan);
                                            },
                                            child: Container(
                                              padding:
                                                  const EdgeInsets.symmetric(
                                                    horizontal: 8,
                                                    vertical: 5,
                                                  ),
                                              decoration: BoxDecoration(
                                                color: const Color(0xFFFEE2E2),
                                                borderRadius:
                                                    BorderRadius.circular(7),
                                              ),
                                              child: const Icon(
                                                Icons.delete_outline_rounded,
                                                size: 13.5,
                                                color: Color(0xFFDC2626),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Widget _buildMiniStat(IconData icon, String text, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 12, color: color),
        const SizedBox(width: 2),
        Text(
          text,
          style: const TextStyle(
            fontSize: 10.5,
            fontWeight: FontWeight.w800,
            color: Color(0xFF0F172A),
          ),
        ),
      ],
    );
  }

  Widget _buildUstaStatBox({
    required IconData icon,
    required String value,
    required String label,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white, size: 14),
            const SizedBox(width: 4),
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.w900,
              ),
            ),
          ],
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.88),
            fontSize: 11,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  void _showFavoritesSheet(List<ElanModel> favorites) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFFF4F8F6),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.75,
          maxChildSize: 0.92,
          minChildSize: 0.45,
          builder: (_, scrollCtrl) {
            return Column(
              children: [
                Container(
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.vertical(
                      top: Radius.circular(20),
                    ),
                  ),
                  padding: const EdgeInsets.fromLTRB(18, 16, 12, 10),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Favorilər (${favorites.length})',
                        style: const TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                      IconButton(
                        onPressed: () => Navigator.pop(ctx),
                        icon: const Icon(Icons.close_rounded),
                      ),
                    ],
                  ),
                ),
                const Divider(height: 1),
                Expanded(
                  child: favorites.isEmpty
                      ? const Center(
                          child: Text(
                            'Seçilmiş usta və ya elan yoxdur',
                            style: TextStyle(color: Color(0xFF64748B)),
                          ),
                        )
                      : GridView.builder(
                          controller: scrollCtrl,
                          padding: const EdgeInsets.all(14),
                          gridDelegate:
                              const SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: 2,
                                mainAxisSpacing: 12,
                                crossAxisSpacing: 12,
                                mainAxisExtent: 196,
                              ),
                          itemCount: favorites.length,
                          itemBuilder: (context, index) {
                            final elan = favorites[index];
                            return ElanCard(
                              elan: elan,
                              onTap: () {
                                Navigator.pop(ctx);
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) => ElanDetailScreen(
                                      elanId: elan.id,
                                      initialElan: elan,
                                    ),
                                  ),
                                );
                              },
                              onFavoriteToggle: () async {
                                await context
                                    .read<ElanProvider>()
                                    .toggleFavorite(elan.id);
                              },
                            );
                          },
                        ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  void _showHelpSupportDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
        title: const Text(
          'Kömək və dəstək',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'prousta.az platforması ilə bağlı sual və ya təklifləriniz üçün dəstək xidmətimizlə əlaqə saxlaya bilərsiniz:\n\n• E-poçt: info@prousta.az\n• Veb sayt: https://prousta.az',
              style: TextStyle(height: 1.45),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                TextButton.icon(
                  onPressed: () {
                    Navigator.pop(ctx);
                    _launchUrl('https://prousta.az/gizlilik/');
                  },
                  icon: const Icon(Icons.privacy_tip_outlined, size: 18),
                  label: const Text('Məxfilik siyasəti'),
                ),
              ],
            ),
            Row(
              children: [
                TextButton.icon(
                  onPressed: () {
                    Navigator.pop(ctx);
                    _launchUrl('https://prousta.az/istifade-sertleri/');
                  },
                  icon: const Icon(Icons.description_outlined, size: 18),
                  label: const Text('İstifadə şərtləri'),
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text(
              'Bağla',
              style: TextStyle(
                color: Color(0xFF007B52),
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _confirmDeleteAccount(AppUser user) {
    final passwordCtrl = TextEditingController();
    final confirmCtrl = TextEditingController();
    bool isSubmitting = false;
    String? errorText;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) {
          return AlertDialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(18),
            ),
            title: Row(
              children: const [
                Icon(Icons.warning_amber_rounded, color: Color(0xFFEF4444)),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Hesabı birdəfəlik sil',
                    style: TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
                  ),
                ),
              ],
            ),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Hesabınızı sildikdə bütün elanlarınız, mesajlarınız, favoritləriniz və profil məlumatlarınız sistemdən birdəfəlik silinəcək və bu əməliyyat geri qaytarıla bilməz.',
                    style: TextStyle(
                      color: Color(0xFF64748B),
                      height: 1.45,
                      fontSize: 13.5,
                    ),
                  ),
                  const SizedBox(height: 16),
                  if (user.hasPassword) ...[
                    const Text(
                      'Təsdiq üçün cari şifrənizi daxil edin:',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: passwordCtrl,
                      obscureText: true,
                      decoration: const InputDecoration(
                        hintText: 'Şifrəniz',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                  ] else ...[
                    const Text(
                      'Təsdiq üçün aşağıdakı xanaya "SIL" yazın:',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: confirmCtrl,
                      decoration: const InputDecoration(
                        hintText: 'SIL',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                  ],
                  if (errorText != null) ...[
                    const SizedBox(height: 10),
                    Text(
                      errorText!,
                      style: const TextStyle(
                        color: Color(0xFFEF4444),
                        fontSize: 12.5,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: isSubmitting ? null : () => Navigator.pop(ctx),
                child: const Text('İmtina'),
              ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFEF4444),
                  foregroundColor: Colors.white,
                  elevation: 0,
                ),
                onPressed: isSubmitting
                    ? null
                    : () async {
                        setDialogState(() {
                          isSubmitting = true;
                          errorText = null;
                        });
                        final messenger = ScaffoldMessenger.of(context);
                        try {
                          await context.read<AuthProvider>().deleteAccount(
                            password: user.hasPassword
                                ? passwordCtrl.text.trim()
                                : null,
                            confirm: !user.hasPassword
                                ? confirmCtrl.text.trim()
                                : null,
                          );
                          if (ctx.mounted) Navigator.pop(ctx);
                          messenger.showSnackBar(
                            const SnackBar(
                              content: Text('Hesabınız uğurla silindi'),
                            ),
                          );
                        } catch (e) {
                          setDialogState(() {
                            isSubmitting = false;
                            errorText = e.toString().replaceFirst(
                              'Exception: ',
                              '',
                            );
                          });
                        }
                      },
                child: isSubmitting
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text(
                        'Hesabı sil',
                        style: TextStyle(fontWeight: FontWeight.w800),
                      ),
              ),
            ],
          );
        },
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
        _loadProfileData();
      });
    } else if (!auth.isAuthenticated && _wasAuthenticated) {
      _wasAuthenticated = false;
    }

    if (!auth.isAuthenticated || auth.user == null) {
      return Scaffold(
        backgroundColor: const Color(0xFFF6F9F8),
        body: SafeArea(
          child: AuthScreen(isEmbedded: true, onSuccess: _loadProfileData),
        ),
      );
    }

    final user = auth.user!;
    final favorites = elanProvider.favorites;
    final phoneDisplay = user.profil.telefon.trim().isNotEmpty
        ? (user.profil.telefon.startsWith('+')
              ? user.profil.telefon
              : '+994 ${user.profil.telefon}')
        : 'Qeyd edilməyib';
    final cityDisplay = user.profil.sheher.trim().isNotEmpty
        ? user.profil.sheher
        : 'Bakı, Azərbaycan';
    final emailDisplay = user.email.trim().isNotEmpty
        ? user.email
        : '@${user.username}';
    final totalViews = _myElanlar.fold<int>(
      0,
      (sum, item) => sum + item.baxishSayi,
    );
    final totalZeng = _myElanlar.fold<int>(
      0,
      (sum, item) => sum + item.zengSayi,
    );
    final totalWp = _myElanlar.fold<int>(0, (sum, item) => sum + item.wpSayi);

    // Combined flutter_ui_challenges profile8.dart + settings1.dart UI
    return Scaffold(
      backgroundColor: const Color(0xFFF4F8F6),
      body: RefreshIndicator(
        color: const Color(0xFF007B52),
        onRefresh: _loadProfileData,
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              child: Column(
                children: <Widget>[
                  // 1. Profile8-style Header with Cover Backdrop & Triple-Ring Avatar
                  _ProustaProfileHeader(
                    user: user,
                    subtitle: '@${user.username} • $cityDisplay',
                    onEditPressed: () => _showEditProfileSheet(user),
                  ),

                  const SizedBox(height: 12.0),

                  // 2. Usta Overall Statistics Card (Baxış, Zəng, WhatsApp, Yazışma)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: InkWell(
                      borderRadius: BorderRadius.circular(14),
                      onTap: () => _showMyElanlarSheet(user, cityDisplay),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 11,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: const Color(0xFFDCECE5)),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(
                                0xFF0F172A,
                              ).withValues(alpha: 0.05),
                              blurRadius: 10,
                              offset: const Offset(0, 3),
                            ),
                          ],
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      const Icon(
                                        Icons.visibility_outlined,
                                        size: 14,
                                        color: Color(0xFF007B52),
                                      ),
                                      const SizedBox(width: 3),
                                      Text(
                                        '$totalViews',
                                        style: const TextStyle(
                                          fontSize: 15.5,
                                          fontWeight: FontWeight.w700,
                                          color: Color(0xFF0F172A),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 2),
                                  const Text(
                                    'Baxış',
                                    style: TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.w600,
                                      color: Color(0xFF64748B),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Container(
                              width: 1,
                              height: 30,
                              color: const Color(0xFFE2E8F0),
                            ),
                            Expanded(
                              child: Column(
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      const Icon(
                                        Icons.phone_callback_rounded,
                                        size: 14,
                                        color: Color(0xFF0FA968),
                                      ),
                                      const SizedBox(width: 3),
                                      Text(
                                        '$totalZeng',
                                        style: const TextStyle(
                                          fontSize: 15.5,
                                          fontWeight: FontWeight.w700,
                                          color: Color(0xFF0F172A),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 2),
                                  const Text(
                                    'Zəng',
                                    style: TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.w600,
                                      color: Color(0xFF64748B),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Container(
                              width: 1,
                              height: 30,
                              color: const Color(0xFFE2E8F0),
                            ),
                            Expanded(
                              child: Column(
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      const Icon(
                                        Icons.chat_rounded,
                                        size: 14,
                                        color: Color(0xFF16A34A),
                                      ),
                                      const SizedBox(width: 3),
                                      Text(
                                        '$totalWp',
                                        style: const TextStyle(
                                          fontSize: 15.5,
                                          fontWeight: FontWeight.w700,
                                          color: Color(0xFF0F172A),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 2),
                                  const Text(
                                    'WhatsApp',
                                    style: TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.w600,
                                      color: Color(0xFF64748B),
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

                  const SizedBox(height: 12.0),

                  // 3. Modern Clean Balance Card (Səliqəli balans kartı)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [Color(0xFF007B52), Color(0xFF06573C)],
                        ),
                        borderRadius: BorderRadius.circular(18.0),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(
                              0xFF007B52,
                            ).withValues(alpha: 0.28),
                            offset: const Offset(0, 8),
                            blurRadius: 18.0,
                            spreadRadius: 1.0,
                          ),
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(18.0),
                        child: Stack(
                          children: [
                            // Subtle background decoration circles
                            Positioned(
                              top: -24,
                              right: -24,
                              child: Container(
                                width: 110,
                                height: 110,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: Colors.white.withValues(alpha: 0.07),
                                ),
                              ),
                            ),
                            Positioned(
                              bottom: -35,
                              right: 60,
                              child: Container(
                                width: 90,
                                height: 90,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: Colors.white.withValues(alpha: 0.05),
                                ),
                              ),
                            ),

                            // Main Content
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 18.0,
                                vertical: 16.0,
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Top Row: Wallet Icon + Label
                                  Row(
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.all(7),
                                        decoration: BoxDecoration(
                                          color: Colors.white.withValues(
                                            alpha: 0.16,
                                          ),
                                          borderRadius: BorderRadius.circular(
                                            10,
                                          ),
                                        ),
                                        child: const Icon(
                                          Icons.account_balance_wallet_rounded,
                                          color: Colors.white,
                                          size: 18,
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Text(
                                        'Cari balans',
                                        style: TextStyle(
                                          color: Colors.white.withValues(
                                            alpha: 0.9,
                                          ),
                                          fontSize: 13,
                                          fontWeight: FontWeight.w600,
                                          letterSpacing: 0.2,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),

                                  // Balance Value + Artır Action Button
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    children: [
                                      Row(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.baseline,
                                        textBaseline: TextBaseline.alphabetic,
                                        children: [
                                          Text(
                                            user.profil.balans.toStringAsFixed(
                                              2,
                                            ),
                                            style: const TextStyle(
                                              color: Colors.white,
                                              fontSize: 27,
                                              fontWeight: FontWeight.w700,
                                              letterSpacing: -0.5,
                                            ),
                                          ),
                                          const SizedBox(width: 6),
                                          Text(
                                            'AZN',
                                            style: TextStyle(
                                              color: Colors.white.withValues(
                                                alpha: 0.85,
                                              ),
                                              fontSize: 14,
                                              fontWeight: FontWeight.w600,
                                            ),
                                          ),
                                        ],
                                      ),

                                      // Sleek Top-up Button
                                      Material(
                                        color: Colors.transparent,
                                        child: InkWell(
                                          borderRadius: BorderRadius.circular(
                                            22,
                                          ),
                                          onTap: () async {
                                            await Navigator.push(
                                              context,
                                              MaterialPageRoute(
                                                builder: (_) =>
                                                    const VipPaymentScreen(
                                                      initialType: 'balans',
                                                    ),
                                              ),
                                            );
                                            _loadProfileData();
                                          },
                                          child: Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 14,
                                              vertical: 8,
                                            ),
                                            decoration: BoxDecoration(
                                              color: Colors.white,
                                              borderRadius:
                                                  BorderRadius.circular(22),
                                              boxShadow: [
                                                BoxShadow(
                                                  color: Colors.black
                                                      .withValues(alpha: 0.12),
                                                  blurRadius: 6,
                                                  offset: const Offset(0, 2),
                                                ),
                                              ],
                                            ),
                                            child: const Row(
                                              mainAxisSize: MainAxisSize.min,
                                              children: [
                                                Icon(
                                                  Icons.add_rounded,
                                                  size: 16,
                                                  color: Color(0xFF007B52),
                                                ),
                                                SizedBox(width: 3),
                                                Text(
                                                  'Balans artır',
                                                  style: TextStyle(
                                                    color: Color(0xFF007B52),
                                                    fontWeight: FontWeight.w700,
                                                    fontSize: 12.5,
                                                  ),
                                                ),
                                              ],
                                            ),
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
                    ),
                  ),

                  const SizedBox(height: 14.0),

                  // 4. Settings1-style Grouped Menu Card (Elanlarım, Favorilər, Mesajlar, Tənzimləmələr)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Card(
                      elevation: 3.5,
                      margin: EdgeInsets.zero,
                      color: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14.0),
                      ),
                      child: Column(
                        children: <Widget>[
                          _buildSettingsTile(
                            icon: Icons.assignment_outlined,
                            title: 'Elanlarım',
                            badgeText: '${_myElanlar.length} elan',
                            onTap: () => _showMyElanlarSheet(user, cityDisplay),
                          ),
                          _buildDivider(),
                          _buildSettingsTile(
                            icon: Icons.favorite_border_rounded,
                            title: 'Favorilər',
                            badgeText: '${favorites.length} elan',
                            onTap: () => _showFavoritesSheet(favorites),
                          ),
                          _buildDivider(),
                          _buildSettingsTile(
                            icon: Icons.chat_bubble_outline_rounded,
                            title: 'Mesajlar',
                            badgeText: _unreadMessagesCount > 0
                                ? '$_unreadMessagesCount yeni'
                                : 'Bax',
                            highlightBadge: _unreadMessagesCount > 0,
                            onTap: () => widget.onNavigateToMessages?.call(),
                          ),
                          _buildDivider(),
                          _buildSettingsTile(
                            icon: Icons.edit_note_rounded,
                            title: 'Tənzimləmələr',
                            onTap: () => _showEditProfileSheet(user),
                          ),
                          _buildDivider(),
                          _buildSettingsTile(
                            icon: Icons.privacy_tip_outlined,
                            title: 'Məxfilik siyasəti',
                            onTap: () =>
                                _launchUrl('https://prousta.az/gizlilik/'),
                          ),
                          _buildDivider(),
                          _buildSettingsTile(
                            icon: Icons.help_outline_rounded,
                            title: 'Kömək və dəstək',
                            onTap: _showHelpSupportDialog,
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 16.0),

                  // 4. Profile8-style User Information Card (ListTile.divideTiles)
                  _ProustaUserInfoCard(
                    city: cityDisplay,
                    email: emailDisplay,
                    phone: phoneDisplay,
                    username: '@${user.username}',
                    onLogout: () async {
                      await context.read<AuthProvider>().logout();
                    },
                    onDeleteAccount: () => _confirmDeleteAccount(user),
                  ),

                  const SizedBox(height: 105.0),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Container _buildDivider() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12.0),
      width: double.infinity,
      height: 1.0,
      color: const Color(0xFFF1F5F9),
    );
  }

  Widget _buildSettingsTile({
    required IconData icon,
    required String title,
    String? badgeText,
    bool highlightBadge = false,
    required VoidCallback onTap,
  }) {
    return ListTile(
      onTap: onTap,
      leading: Container(
        width: 38,
        height: 38,
        decoration: BoxDecoration(
          color: const Color(0xFFEAF6F1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: const Color(0xFF007B52), size: 20),
      ),
      title: Text(
        title,
        style: const TextStyle(
          fontSize: 15,
          fontWeight: FontWeight.w700,
          color: Color(0xFF0F172A),
        ),
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (badgeText != null) ...[
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
              decoration: BoxDecoration(
                color: highlightBadge
                    ? const Color(0xFF0FA968)
                    : const Color(0xFFEAF6F1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                badgeText,
                style: TextStyle(
                  fontSize: 11.5,
                  fontWeight: FontWeight.w600,
                  color: highlightBadge
                      ? Colors.white
                      : const Color(0xFF007B52),
                ),
              ),
            ),
            const SizedBox(width: 6),
          ],
          const Icon(
            Icons.keyboard_arrow_right_rounded,
            color: Color(0xFF94A3B8),
          ),
        ],
      ),
    );
  }
}

/// Adapted directly from `flutter_ui_challenges/lib/src/pages/profile/profile8.dart` (`ProfileHeader` & `Avatar`)
class _ProustaProfileHeader extends StatelessWidget {
  final AppUser user;
  final String subtitle;
  final VoidCallback onEditPressed;

  const _ProustaProfileHeader({
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
        // Narrower Green Cover Backdrop lifted up
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
        // Triple-Ring Avatar + User Name & Subtitle lifted up
        Container(
          width: double.infinity,
          margin: EdgeInsets.only(top: bannerHeight - 44),
          child: Column(
            children: <Widget>[
              GestureDetector(
                onTap: onEditPressed,
                child: _ProustaAvatar(
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

/// Adapted from `profile8.dart` (`UserInfo`)
class _ProustaUserInfoCard extends StatelessWidget {
  final String city;
  final String email;
  final String phone;
  final String username;
  final VoidCallback onLogout;
  final VoidCallback onDeleteAccount;

  const _ProustaUserInfoCard({
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

/// Triple-ring Avatar from `profile8.dart`
class _ProustaAvatar extends StatelessWidget {
  final String? imageUrl;
  final String fallbackInitial;
  final Color borderColor;
  final Color? backgroundColor;
  final double radius;
  final double borderWidth;

  const _ProustaAvatar({
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
