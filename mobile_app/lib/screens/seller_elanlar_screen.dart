import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/models.dart';
import '../services/api_service.dart';
import '../widgets/elan_card.dart';
import 'elan_detail_screen.dart';

class SellerElanlarScreen extends StatefulWidget {
  final int sellerId;
  final String sellerName;
  final String? sellerAvatar;

  const SellerElanlarScreen({
    super.key,
    required this.sellerId,
    required this.sellerName,
    this.sellerAvatar,
  });

  @override
  State<SellerElanlarScreen> createState() => _SellerElanlarScreenState();
}

class _SellerElanlarScreenState extends State<SellerElanlarScreen> {
  static const Color _brandPrimary = Color(0xFF007B52);
  static const Color _brandLight = Color(0xFFEAF6F1);

  final List<ElanModel> _elanlar = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchSellerElanlar();
  }

  Future<void> _fetchSellerElanlar() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final res = await ApiService.getElanlar(userId: widget.sellerId);
      final list = (res['results'] as List<dynamic>?)?.cast<ElanModel>() ?? [];
      if (mounted) {
        setState(() {
          _elanlar.clear();
          _elanlar.addAll(list);
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7FAF9),
      appBar: AppBar(
        titleSpacing: 0,
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        title: Row(
          children: [
            CircleAvatar(
              radius: 17,
              backgroundColor: _brandLight,
              backgroundImage: (widget.sellerAvatar != null &&
                      widget.sellerAvatar!.isNotEmpty)
                  ? CachedNetworkImageProvider(widget.sellerAvatar!)
                  : null,
              child: (widget.sellerAvatar == null ||
                      widget.sellerAvatar!.isEmpty)
                  ? Text(
                      widget.sellerName.isNotEmpty
                          ? widget.sellerName[0].toUpperCase()
                          : 'U',
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                        color: _brandPrimary,
                      ),
                    )
                  : null,
            ),
            const SizedBox(width: 9),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.sellerName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 15.5,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  if (_isLoading)
                    const Text(
                      'Elanlar yüklənir...',
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
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: _brandPrimary),
            )
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          _error!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: Color(0xFF64748B),
                            fontSize: 14,
                          ),
                        ),
                        const SizedBox(height: 14),
                        ElevatedButton(
                          onPressed: _fetchSellerElanlar,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _brandPrimary,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: const Text('Yenidən cəhd et'),
                        ),
                      ],
                    ),
                  ),
                )
              : _elanlar.isEmpty
                  ? const Center(
                      child: Text(
                        'Ustanın başqa aktiv elanı yoxdur',
                        style: TextStyle(
                          color: Color(0xFF64748B),
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    )
                  : RefreshIndicator(
                      color: _brandPrimary,
                      onRefresh: _fetchSellerElanlar,
                      child: GridView.builder(
                        padding: const EdgeInsets.all(14),
                        gridDelegate:
                            const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          mainAxisSpacing: 12,
                          crossAxisSpacing: 12,
                          mainAxisExtent: 226,
                        ),
                        itemCount: _elanlar.length,
                        itemBuilder: (context, index) {
                          final elan = _elanlar[index];
                          return ElanCard(
                            elan: elan,
                            onTap: () {
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
                          );
                        },
                      ),
                    ),
    );
  }
}
