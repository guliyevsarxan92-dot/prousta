import '../widgets/picked_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/auth_provider.dart';
import '../providers/elan_provider.dart';
import '../services/api_service.dart';
import '../widgets/prousta_wordmark.dart';

class VipPaymentScreen extends StatefulWidget {
  final int? elanId;
  final String? elanTitle;
  final String initialType;

  const VipPaymentScreen({
    super.key,
    this.elanId,
    this.elanTitle,
    this.initialType = 'balans',
  });

  @override
  State<VipPaymentScreen> createState() => _VipPaymentScreenState();
}

class _VipPaymentScreenState extends State<VipPaymentScreen> {
  static const Color _brandPrimary = Color(0xFF007B52);
  static const Color _brandDark = Color(0xFF0A4D34);
  static const Color _brandAccent = Color(0xFF0FA968);
  static const Color _brandLight = Color(0xFFEAF6F1);

  static const List<int> _quickAmounts = [5, 10, 20, 50, 100];

  final _meblegCtrl = TextEditingController(text: '10');
  final _qeydCtrl = TextEditingController();
  final ImagePicker _picker = ImagePicker();

  List<VipPaketModel> _packages = [];
  List<BankMelumatModel> _banks = [];
  late String _selectedType;
  XFile? _receiptFile;
  bool _isLoading = true;
  bool _isSubmitting = false;
  bool _isActivatingFromBalance = false;

  /// True when opened from the Profile "Balans" section (strictly balance top-up, no VIP options)
  bool get _isBalanceOnly =>
      widget.initialType == 'balans' && widget.elanId == null;

  @override
  void initState() {
    super.initState();
    _selectedType = _isBalanceOnly
        ? 'balans'
        : (widget.initialType == 'super_vip' ? 'super_vip' : 'vip');
    _loadData();
  }

  @override
  void dispose() {
    _meblegCtrl.dispose();
    _qeydCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final bankList = await ApiService.getBankInfo();
      List<VipPaketModel> pkgList = [];
      if (!_isBalanceOnly) {
        pkgList = await ApiService.getVipPackages();
      }
      if (mounted) {
        setState(() {
          _banks = bankList;
          _packages = pkgList;
          if (!_isBalanceOnly) {
            _updateAmountForType(_selectedType);
          }
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  double _priceForType(String type) {
    final match = _packages.where((p) => p.nov == type).firstOrNull;
    if (match != null && match.qiymet > 0) {
      return match.qiymet;
    }
    return type == 'super_vip' ? 8.0 : 3.0;
  }

  int _daysForType(String type) {
    final match = _packages.where((p) => p.nov == type).firstOrNull;
    if (match != null && match.muddetGun > 0) {
      return match.muddetGun;
    }
    return type == 'super_vip' ? 30 : 10;
  }

  void _updateAmountForType(String type) {
    if (type == 'vip' || type == 'super_vip') {
      final price = _priceForType(type);
      _meblegCtrl.text = price == price.roundToDouble()
          ? price.toInt().toString()
          : price.toStringAsFixed(2);
    }
  }

  Future<void> _activateFromBalance() async {
    if (widget.elanId == null) return;
    setState(() => _isActivatingFromBalance = true);
    try {
      final msg = await ApiService.activateVipFromBalance(
        elanId: widget.elanId!,
        nov: _selectedType,
      );
      if (!mounted) return;
      await context.read<AuthProvider>().refreshProfile();
      if (!mounted) return;
      await context.read<ElanProvider>().fetchElanlar(reset: true);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg), backgroundColor: _brandPrimary),
      );
      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString().replaceFirst('Exception: ', '')),
          backgroundColor: Colors.redAccent,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isActivatingFromBalance = false);
      }
    }
  }

  Future<void> _pickReceipt() async {
    try {
      final xfile = await _picker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
      );
      if (xfile != null) {
        setState(() {
          _receiptFile = xfile;
        });
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Qəbz seçilə bilmədi: $e')));
    }
  }

  Future<void> _submitPayment() async {
    final amount = _meblegCtrl.text.trim();
    if (amount.isEmpty || (double.tryParse(amount) ?? 0) <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Zəhmət olmasa düzgün məbləğ daxil edin'),
          backgroundColor: Colors.redAccent,
        ),
      );
      return;
    }

    if (_receiptFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Zəhmət olmasa ödəniş qəbzinin şəklini əlavə edin'),
          backgroundColor: Colors.redAccent,
        ),
      );
      return;
    }

    setState(() => _isSubmitting = true);
    try {
      final msg = await ApiService.submitPayment(
        nov: _isBalanceOnly ? 'balans' : _selectedType,
        mebleg: amount,
        elanId: widget.elanId,
        qebzFile: _receiptFile!,
        qeyd: _qeydCtrl.text.trim(),
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg), backgroundColor: _brandPrimary),
      );
      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString().replaceFirst('Exception: ', '')),
          backgroundColor: Colors.redAccent,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = context.watch<AuthProvider>().user;
    final currentBalance = user?.profil.balans ?? 0.0;
    final selectedPrice = _priceForType(_selectedType);
    final hasEnoughBalance = currentBalance >= selectedPrice;

    return Scaffold(
      backgroundColor: const Color(0xFFF4F8F6),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        titleSpacing: 0,
        title: Row(
          children: [
            const ProustaWordmark(fontSize: 21),
            const SizedBox(width: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 3),
              decoration: BoxDecoration(
                color: _brandLight,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                _isBalanceOnly ? 'Balans artır' : 'Elanı VİP et',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  color: _brandPrimary,
                ),
              ),
            ),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: _brandPrimary))
          : Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 640),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 36),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 1. Current Balance Hero Card
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: const Color(0xFFE2E8F0)),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(
                                0xFF0F172A,
                              ).withValues(alpha: 0.05),
                              blurRadius: 16,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 48,
                              height: 48,
                              decoration: BoxDecoration(
                                color: _brandLight,
                                borderRadius: BorderRadius.circular(14),
                              ),
                              child: const Icon(
                                Icons.account_balance_wallet_rounded,
                                color: _brandPrimary,
                                size: 25,
                              ),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'Cari balansınız',
                                    style: TextStyle(
                                      fontSize: 12.5,
                                      color: Color(0xFF64748B),
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    '${currentBalance.toStringAsFixed(2)} AZN',
                                    style: const TextStyle(
                                      fontSize: 21,
                                      fontWeight: FontWeight.w900,
                                      color: _brandPrimary,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            if (!_isBalanceOnly)
                              TextButton.icon(
                                onPressed: () async {
                                  await Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (_) => const VipPaymentScreen(
                                        initialType: 'balans',
                                      ),
                                    ),
                                  );
                                  if (!context.mounted) return;
                                  await context
                                      .read<AuthProvider>()
                                      .refreshProfile();
                                },
                                icon: const Icon(
                                  Icons.add_circle_outline_rounded,
                                  size: 16,
                                  color: _brandPrimary,
                                ),
                                label: const Text(
                                  'Balans artır',
                                  style: TextStyle(
                                    fontSize: 12.5,
                                    fontWeight: FontWeight.w800,
                                    color: _brandPrimary,
                                  ),
                                ),
                                style: TextButton.styleFrom(
                                  backgroundColor: _brandLight,
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 12,
                                    vertical: 8,
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Selected Elan & 2 VIP Options (3 AZN - 8 AZN) when opened for an Elan
                      if (!_isBalanceOnly) ...[
                        if (widget.elanTitle != null &&
                            widget.elanTitle!.isNotEmpty) ...[
                          Container(
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: _brandLight,
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(
                                color: _brandAccent.withValues(alpha: 0.35),
                              ),
                            ),
                            child: Row(
                              children: [
                                const Icon(
                                  Icons.workspace_premium_rounded,
                                  color: Color(0xFFD97706),
                                  size: 24,
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        'Seçilmiş elan:',
                                        style: TextStyle(
                                          fontSize: 12,
                                          color: Color(0xFF475569),
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                      Text(
                                        widget.elanTitle!,
                                        style: const TextStyle(
                                          fontWeight: FontWeight.w800,
                                          fontSize: 14.5,
                                          color: Color(0xFF0F172A),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 16),
                        ],

                        const Text(
                          'VİP Paket Seçin (2 seçim)',
                          style: TextStyle(
                            fontSize: 15.5,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        const SizedBox(height: 10),

                        Row(
                          children: [
                            Expanded(
                              child: _buildVipOptionCard(
                                nov: 'vip',
                                title: 'VİP Elan',
                                priceText:
                                    '${_priceForType('vip').toInt()} AZN',
                                durationText:
                                    '${_daysForType('vip')} gün aktiv',
                                subtitle: 'Axtarışda və siyahıda öndə',
                                icon: Icons.star_rounded,
                                accentColor: const Color(0xFF007B52),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _buildVipOptionCard(
                                nov: 'super_vip',
                                title: 'Super VİP',
                                priceText:
                                    '${_priceForType('super_vip').toInt()} AZN',
                                durationText:
                                    '${_daysForType('super_vip')} gün aktiv',
                                subtitle: 'Ana səhifədə ən öndə + Qızılı nişan',
                                icon: Icons.workspace_premium_rounded,
                                accentColor: const Color(0xFFD97706),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),

                        // Activate directly from Balance card
                        if (widget.elanId != null) ...[
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: hasEnoughBalance
                                    ? _brandPrimary.withValues(alpha: 0.4)
                                    : const Color(0xFFFCA5A5),
                              ),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Icon(
                                      hasEnoughBalance
                                          ? Icons.verified_rounded
                                          : Icons.info_outline_rounded,
                                      color: hasEnoughBalance
                                          ? _brandPrimary
                                          : const Color(0xFFDC2626),
                                      size: 20,
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        hasEnoughBalance
                                            ? 'Balansınız kifayətdir! Dərhal aktiv edə bilərsiniz.'
                                            : 'Balansınızda kifayət qədər vəsait yoxdur (Lazım olan: ${selectedPrice.toInt()} AZN).',
                                        style: TextStyle(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w700,
                                          color: hasEnoughBalance
                                              ? const Color(0xFF0F172A)
                                              : const Color(0xFFB91C1C),
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 12),
                                SizedBox(
                                  width: double.infinity,
                                  height: 48,
                                  child: ElevatedButton.icon(
                                    onPressed: _isActivatingFromBalance
                                        ? null
                                        : (hasEnoughBalance
                                              ? _activateFromBalance
                                              : () async {
                                                  await Navigator.push(
                                                    context,
                                                    MaterialPageRoute(
                                                      builder: (_) =>
                                                          const VipPaymentScreen(
                                                            initialType:
                                                                'balans',
                                                          ),
                                                    ),
                                                  );
                                                  if (!context.mounted) return;
                                                  await context
                                                      .read<AuthProvider>()
                                                      .refreshProfile();
                                                }),
                                    icon: _isActivatingFromBalance
                                        ? const SizedBox(
                                            width: 18,
                                            height: 18,
                                            child: CircularProgressIndicator(
                                              strokeWidth: 2,
                                              color: Colors.white,
                                            ),
                                          )
                                        : Icon(
                                            hasEnoughBalance
                                                ? Icons.bolt_rounded
                                                : Icons
                                                      .account_balance_wallet_rounded,
                                            size: 20,
                                          ),
                                    label: Text(
                                      hasEnoughBalance
                                          ? 'Balansdan Aktiv Et (${selectedPrice.toInt()} AZN)'
                                          : 'Balansı Artır (${selectedPrice.toInt()} AZN üçün)',
                                      style: const TextStyle(
                                        fontSize: 14.5,
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: hasEnoughBalance
                                          ? (_selectedType == 'super_vip'
                                                ? const Color(0xFFD97706)
                                                : _brandPrimary)
                                          : const Color(0xFF0F172A),
                                      foregroundColor: Colors.white,
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 20),
                        ],
                      ],

                      // 2. Bank Card Details (Prousta Forest Green Card) - shown for Balance top-up
                      if (_isBalanceOnly) ...[
                        const Text(
                          'Ödəniş üçün Bank Kartı',
                          style: TextStyle(
                            fontSize: 15.5,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        const SizedBox(height: 8),
                        if (_banks.isEmpty)
                          _buildBankCard(
                            BankMelumatModel(
                              id: 0,
                              bankAdi: 'Kapital Bank / ABB',
                              kartNomresi: '4169 7388 0000 0000',
                              kartSahibi: 'Prousta.az',
                            ),
                          )
                        else
                          ..._banks.map(_buildBankCard),

                        const SizedBox(height: 16),

                        // 3. Amount & Receipt Card
                        Container(
                          padding: const EdgeInsets.all(18),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                            boxShadow: [
                              BoxShadow(
                                color: const Color(
                                  0xFF0F172A,
                                ).withValues(alpha: 0.04),
                                blurRadius: 14,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Artırılacaq məbləğ (AZN) *',
                                style: TextStyle(
                                  fontWeight: FontWeight.w800,
                                  fontSize: 14.5,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                              const SizedBox(height: 10),

                              // Quick Amount Chips for Balance Top-Up
                              Wrap(
                                spacing: 8,
                                runSpacing: 8,
                                children: _quickAmounts.map((amt) {
                                  final isSelected =
                                      _meblegCtrl.text.trim() == amt.toString();
                                  return GestureDetector(
                                    onTap: () {
                                      setState(() {
                                        _meblegCtrl.text = amt.toString();
                                      });
                                    },
                                    child: AnimatedContainer(
                                      duration: const Duration(
                                        milliseconds: 160,
                                      ),
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 14,
                                        vertical: 8,
                                      ),
                                      decoration: BoxDecoration(
                                        color: isSelected
                                            ? _brandPrimary
                                            : _brandLight,
                                        borderRadius: BorderRadius.circular(20),
                                        border: Border.all(
                                          color: isSelected
                                              ? _brandPrimary
                                              : _brandAccent.withValues(
                                                  alpha: 0.3,
                                                ),
                                        ),
                                      ),
                                      child: Text(
                                        '$amt ₼',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w800,
                                          fontSize: 13.5,
                                          color: isSelected
                                              ? Colors.white
                                              : _brandPrimary,
                                        ),
                                      ),
                                    ),
                                  );
                                }).toList(),
                              ),
                              const SizedBox(height: 12),

                              TextField(
                                controller: _meblegCtrl,
                                onChanged: (_) => setState(() {}),
                                keyboardType:
                                    const TextInputType.numberWithOptions(
                                      decimal: true,
                                    ),
                                style: const TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF0F172A),
                                ),
                                decoration: InputDecoration(
                                  prefixIcon: const Icon(
                                    Icons.payments_outlined,
                                    color: _brandPrimary,
                                    size: 20,
                                  ),
                                  suffixText: 'AZN',
                                  suffixStyle: const TextStyle(
                                    fontWeight: FontWeight.w800,
                                    color: _brandPrimary,
                                  ),
                                  filled: true,
                                  fillColor: const Color(0xFFF8FAFC),
                                  contentPadding: const EdgeInsets.symmetric(
                                    horizontal: 14,
                                    vertical: 13,
                                  ),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: const BorderSide(
                                      color: Color(0xFFE2E8F0),
                                    ),
                                  ),
                                  enabledBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: const BorderSide(
                                      color: Color(0xFFE2E8F0),
                                    ),
                                  ),
                                  focusedBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: const BorderSide(
                                      color: _brandPrimary,
                                      width: 1.5,
                                    ),
                                  ),
                                ),
                              ),

                              const SizedBox(height: 18),

                              // Receipt Image Picker
                              const Text(
                                'Ödəniş qəbzi (ekran görüntüsü və ya foto) *',
                                style: TextStyle(
                                  fontWeight: FontWeight.w800,
                                  fontSize: 14.5,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                              const SizedBox(height: 8),
                              GestureDetector(
                                onTap: _pickReceipt,
                                child: Container(
                                  width: double.infinity,
                                  height: _receiptFile != null ? 190 : 115,
                                  decoration: BoxDecoration(
                                    color: _brandLight.withValues(alpha: 0.55),
                                    borderRadius: BorderRadius.circular(14),
                                    border: Border.all(
                                      color: _brandPrimary.withValues(
                                        alpha: 0.35,
                                      ),
                                      width: 1.4,
                                    ),
                                  ),
                                  child: _receiptFile != null
                                      ? Stack(
                                          fit: StackFit.expand,
                                          children: [
                                            ClipRRect(
                                              borderRadius:
                                                  BorderRadius.circular(13),
                                              child: PickedImage(
                                                _receiptFile!,
                                                fit: BoxFit.cover,
                                              ),
                                            ),
                                            Positioned(
                                              top: 8,
                                              right: 8,
                                              child: CircleAvatar(
                                                radius: 16,
                                                backgroundColor: Colors.black54,
                                                child: IconButton(
                                                  padding: EdgeInsets.zero,
                                                  icon: const Icon(
                                                    Icons.close_rounded,
                                                    color: Colors.white,
                                                    size: 18,
                                                  ),
                                                  onPressed: () {
                                                    setState(
                                                      () => _receiptFile = null,
                                                    );
                                                  },
                                                ),
                                              ),
                                            ),
                                          ],
                                        )
                                      : const Column(
                                          mainAxisAlignment:
                                              MainAxisAlignment.center,
                                          children: [
                                            Icon(
                                              Icons.receipt_long_rounded,
                                              size: 36,
                                              color: _brandPrimary,
                                            ),
                                            SizedBox(height: 6),
                                            Text(
                                              'Qəbz şəklini seçmək üçün toxunun',
                                              style: TextStyle(
                                                color: _brandPrimary,
                                                fontWeight: FontWeight.w700,
                                                fontSize: 13.5,
                                              ),
                                            ),
                                          ],
                                        ),
                                ),
                              ),

                              const SizedBox(height: 16),

                              // Optional Note
                              const Text(
                                'Əlavə qeyd (istəyə bağlı)',
                                style: TextStyle(
                                  fontWeight: FontWeight.w700,
                                  fontSize: 13.5,
                                  color: Color(0xFF475569),
                                ),
                              ),
                              const SizedBox(height: 6),
                              TextField(
                                controller: _qeydCtrl,
                                maxLines: 2,
                                style: const TextStyle(fontSize: 14),
                                decoration: InputDecoration(
                                  hintText:
                                      'Ödənişlə bağlı qeydiniz varsa yazın...',
                                  hintStyle: const TextStyle(
                                    color: Color(0xFF94A3B8),
                                    fontSize: 13.5,
                                  ),
                                  filled: true,
                                  fillColor: const Color(0xFFF8FAFC),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: const BorderSide(
                                      color: Color(0xFFE2E8F0),
                                    ),
                                  ),
                                  enabledBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: const BorderSide(
                                      color: Color(0xFFE2E8F0),
                                    ),
                                  ),
                                  focusedBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: const BorderSide(
                                      color: _brandPrimary,
                                      width: 1.5,
                                    ),
                                  ),
                                ),
                              ),

                              const SizedBox(height: 20),

                              SizedBox(
                                width: double.infinity,
                                height: 50,
                                child: ElevatedButton.icon(
                                  onPressed: _isSubmitting
                                      ? null
                                      : _submitPayment,
                                  icon: _isSubmitting
                                      ? const SizedBox(
                                          width: 20,
                                          height: 20,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                            color: Colors.white,
                                          ),
                                        )
                                      : const Icon(
                                          Icons.check_circle_outline_rounded,
                                          size: 20,
                                        ),
                                  label: const Text(
                                    'Balansı Artır (Qəbzi Göndər)',
                                    style: TextStyle(
                                      fontSize: 15,
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: _brandPrimary,
                                    foregroundColor: Colors.white,
                                    elevation: 2,
                                    shadowColor: _brandPrimary.withValues(
                                      alpha: 0.35,
                                    ),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ),
    );
  }

  Widget _buildVipOptionCard({
    required String nov,
    required String title,
    required String priceText,
    required String durationText,
    required String subtitle,
    required IconData icon,
    required Color accentColor,
  }) {
    final isSelected = _selectedType == nov;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedType = nov;
          _updateAmountForType(nov);
        });
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isSelected
              ? accentColor.withValues(alpha: 0.08)
              : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? accentColor : const Color(0xFFE2E8F0),
            width: isSelected ? 2 : 1,
          ),
          boxShadow: [
            BoxShadow(
              color: isSelected
                  ? accentColor.withValues(alpha: 0.16)
                  : const Color(0xFF0F172A).withValues(alpha: 0.04),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.all(7),
                  decoration: BoxDecoration(
                    color: accentColor.withValues(alpha: 0.14),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(icon, color: accentColor, size: 20),
                ),
                Icon(
                  isSelected
                      ? Icons.radio_button_checked_rounded
                      : Icons.radio_button_off_rounded,
                  color: isSelected ? accentColor : const Color(0xFF94A3B8),
                  size: 20,
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              title,
              style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              priceText,
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.w900,
                color: accentColor,
              ),
            ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                durationText,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF475569),
                ),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              subtitle,
              style: const TextStyle(
                fontSize: 11.5,
                color: Color(0xFF64748B),
                height: 1.3,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBankCard(BankMelumatModel bank) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_brandDark, _brandPrimary, _brandAccent],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: _brandPrimary.withValues(alpha: 0.28),
            blurRadius: 14,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                bank.bankAdi,
                style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.88),
                  fontSize: 13.5,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const Icon(
                Icons.contactless_rounded,
                color: Colors.white70,
                size: 22,
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Text(
                  bank.kartNomresi,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 19,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.4,
                  ),
                ),
              ),
              Material(
                color: Colors.white.withValues(alpha: 0.18),
                borderRadius: BorderRadius.circular(10),
                child: InkWell(
                  borderRadius: BorderRadius.circular(10),
                  onTap: () {
                    Clipboard.setData(ClipboardData(text: bank.kartNomresi));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Kart nömrəsi kopyalandı!'),
                        backgroundColor: _brandPrimary,
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                  child: const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.copy_rounded, color: Colors.white, size: 16),
                        SizedBox(width: 4),
                        Text(
                          'Kopyala',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            bank.kartSahibi,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.92),
              fontSize: 13.5,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
