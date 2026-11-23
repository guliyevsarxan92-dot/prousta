import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import '../widgets/prousta_wordmark.dart';
import 'auth_screen.dart';
import 'chat_detail_screen.dart';

export 'chat_detail_screen.dart';

class MessagesScreen extends StatefulWidget {
  const MessagesScreen({super.key});

  @override
  State<MessagesScreen> createState() => _MessagesScreenState();
}

class _MessagesScreenState extends State<MessagesScreen> {
  static const Color _brandPrimary = Color(0xFF007B52);
  static const Color _brandLight = Color(0xFFEAF6F1);

  List<ConversationModel> _conversations = [];
  bool _isLoading = false;
  String? _error;
  bool _hasMore = false;

  @override
  void initState() {
    super.initState();
    _loadConversations();
  }

  Future<void> _loadConversations({bool more = false}) async {
    if (!ApiService.isAuthenticated || _isLoading) return;
    final sessionToken = ApiService.token;
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final list = await ApiService.getConversations(
        beforeId: more && _conversations.isNotEmpty
            ? _conversations.last.lastMessageId
            : null,
      );
      if (mounted && ApiService.token == sessionToken) {
        setState(() {
          if (more) {
            final ids = _conversations.map((item) => item.userId).toSet();
            _conversations.addAll(
              list.where((item) => !ids.contains(item.userId)),
            );
          } else {
            _conversations = list;
          }
          _hasMore = list.length == 100;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString().replaceFirst('Exception: ', '');
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  String _formatTime(String raw) {
    if (raw.isEmpty) return '';
    final dt = DateTime.tryParse(raw)?.toLocal();
    if (dt == null) return raw;
    final now = DateTime.now();
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    if (dt.year == now.year && dt.month == now.month && dt.day == now.day) {
      return '${twoDigits(dt.hour)}:${twoDigits(dt.minute)}';
    }
    return '${twoDigits(dt.day)}.${twoDigits(dt.month)}.${dt.year}';
  }

  @override
  Widget build(BuildContext context) {
    final isAuthenticated = context.watch<AuthProvider>().isAuthenticated;

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
                'Mesajlar',
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
          if (isAuthenticated)
            IconButton(
              onPressed: _loadConversations,
              icon: const Icon(
                Icons.refresh_rounded,
                color: Color(0xFF475569),
                size: 21,
              ),
              tooltip: 'Yenilə',
            ),
        ],
      ),
      body: !isAuthenticated
          ? _buildLoggedOutState(context)
          : RefreshIndicator(
              color: _brandPrimary,
              onRefresh: _loadConversations,
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 720),
                  child: _isLoading && _conversations.isEmpty
                      ? const Center(
                          child: CircularProgressIndicator(
                            color: _brandPrimary,
                          ),
                        )
                      : _error != null && _conversations.isEmpty
                      ? Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  _error!,
                                  style: const TextStyle(
                                    color: Color(0xFFDC2626),
                                  ),
                                ),
                                const SizedBox(height: 12),
                                ElevatedButton(
                                  onPressed: _loadConversations,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: _brandPrimary,
                                    foregroundColor: Colors.white,
                                  ),
                                  child: const Text('Yenidən cəhd et'),
                                ),
                              ],
                            ),
                          ),
                        )
                      : _conversations.isEmpty
                      ? _buildEmptyConversationsState()
                      : ListView.separated(
                          padding: const EdgeInsets.all(12),
                          itemCount: _conversations.length + (_hasMore ? 1 : 0),
                          separatorBuilder: (_, _) => const SizedBox(height: 8),
                          itemBuilder: (context, index) {
                            if (index == _conversations.length) {
                              return TextButton(
                                onPressed: _isLoading
                                    ? null
                                    : () => _loadConversations(more: true),
                                child: const Text('Daha çox söhbət'),
                              );
                            }
                            final conv = _conversations[index];
                            final displayName = conv.adSoyad.trim().isNotEmpty
                                ? conv.adSoyad
                                : conv.username;
                            final hasUnread = conv.unreadCount > 0;

                            return Material(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(14),
                              child: InkWell(
                                borderRadius: BorderRadius.circular(14),
                                onTap: () async {
                                  await Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (_) => ChatDetailScreen(
                                        otherUserId: conv.userId,
                                        otherUserName: displayName,
                                        elanId: conv.elanId,
                                      ),
                                    ),
                                  );
                                  _loadConversations();
                                },
                                child: Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 14,
                                    vertical: 12,
                                  ),
                                  decoration: BoxDecoration(
                                    borderRadius: BorderRadius.circular(14),
                                    border: Border.all(
                                      color: hasUnread
                                          ? _brandPrimary.withValues(alpha: 0.4)
                                          : const Color(0xFFE2E8F0),
                                    ),
                                  ),
                                  child: Row(
                                    children: [
                                      CircleAvatar(
                                        radius: 23,
                                        backgroundColor: _brandLight,
                                        backgroundImage:
                                            conv.avatar != null &&
                                                conv.avatar!.isNotEmpty
                                            ? CachedNetworkImageProvider(
                                                conv.avatar!,
                                              )
                                            : null,
                                        child:
                                            conv.avatar == null ||
                                                conv.avatar!.isEmpty
                                            ? Text(
                                                displayName.isNotEmpty
                                                    ? displayName[0]
                                                          .toUpperCase()
                                                    : 'U',
                                                style: const TextStyle(
                                                  fontWeight: FontWeight.w800,
                                                  color: _brandPrimary,
                                                  fontSize: 16,
                                                ),
                                              )
                                            : null,
                                      ),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Row(
                                              children: [
                                                Expanded(
                                                  child: Text(
                                                    displayName,
                                                    maxLines: 1,
                                                    overflow:
                                                        TextOverflow.ellipsis,
                                                    style: TextStyle(
                                                      fontSize: 14.5,
                                                      fontWeight: hasUnread
                                                          ? FontWeight.w800
                                                          : FontWeight.w700,
                                                      color: const Color(
                                                        0xFF0F172A,
                                                      ),
                                                    ),
                                                  ),
                                                ),
                                                const SizedBox(width: 6),
                                                Text(
                                                  _formatTime(
                                                    conv.lastMessageTime,
                                                  ),
                                                  style: TextStyle(
                                                    fontSize: 11.5,
                                                    fontWeight: hasUnread
                                                        ? FontWeight.w700
                                                        : FontWeight.w500,
                                                    color: hasUnread
                                                        ? _brandPrimary
                                                        : const Color(
                                                            0xFF94A3B8,
                                                          ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                            const SizedBox(height: 4),
                                            Row(
                                              children: [
                                                Expanded(
                                                  child: Text(
                                                    conv.lastMessage,
                                                    maxLines: 1,
                                                    overflow:
                                                        TextOverflow.ellipsis,
                                                    style: TextStyle(
                                                      fontSize: 13,
                                                      color: hasUnread
                                                          ? const Color(
                                                              0xFF1E293B,
                                                            )
                                                          : const Color(
                                                              0xFF64748B,
                                                            ),
                                                      fontWeight: hasUnread
                                                          ? FontWeight.w600
                                                          : FontWeight.w400,
                                                    ),
                                                  ),
                                                ),
                                                if (hasUnread)
                                                  Container(
                                                    margin:
                                                        const EdgeInsets.only(
                                                          left: 8,
                                                        ),
                                                    padding:
                                                        const EdgeInsets.symmetric(
                                                          horizontal: 7,
                                                          vertical: 2,
                                                        ),
                                                    decoration: BoxDecoration(
                                                      color: _brandPrimary,
                                                      borderRadius:
                                                          BorderRadius.circular(
                                                            10,
                                                          ),
                                                    ),
                                                    child: Text(
                                                      '${conv.unreadCount}',
                                                      style: const TextStyle(
                                                        color: Colors.white,
                                                        fontSize: 10.5,
                                                        fontWeight:
                                                            FontWeight.w800,
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
                    Icons.forum_outlined,
                    size: 30,
                    color: _brandPrimary,
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Mesajlar və Söhbətlər',
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
                  'Ustalar və müştərilərlə birbaşa yazışmaq, qiymət və xidmət detallarını dəqiqləşdirmək üçün hesabınıza daxil olun.',
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
                      if (mounted && ApiService.isAuthenticated) {
                        _loadConversations();
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

  Widget _buildEmptyConversationsState() {
    return ListView(
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
              child: const Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: _brandLight,
                    child: Icon(
                      Icons.chat_bubble_outline_rounded,
                      size: 26,
                      color: _brandPrimary,
                    ),
                  ),
                  SizedBox(height: 14),
                  Text(
                    'Hələ yazışmanız yoxdur',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  SizedBox(height: 6),
                  Text(
                    'İstənilən elana daxil olub "Mesaj" düyməsinə toxunaraq ustaya birbaşa yaza bilərsiniz.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 13,
                      color: Color(0xFF64748B),
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

