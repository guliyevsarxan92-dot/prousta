import 'dart:async';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import '../widgets/prousta_wordmark.dart';
import 'auth_screen.dart';

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

class ChatDetailScreen extends StatefulWidget {
  final int otherUserId;
  final String otherUserName;
  final int? elanId;
  final String? elanTitle;

  const ChatDetailScreen({
    super.key,
    required this.otherUserId,
    required this.otherUserName,
    this.elanId,
    this.elanTitle,
  });

  @override
  State<ChatDetailScreen> createState() => _ChatDetailScreenState();
}

class _ChatDetailScreenState extends State<ChatDetailScreen> {
  static const Color _brandPrimary = Color(0xFF007B52);
  static const Color _brandLight = Color(0xFFEAF6F1);

  final _messageCtrl = TextEditingController();
  final _scrollCtrl = ScrollController();

  final List<ChatMessageModel> _messages = [];
  bool _isLoading = true;
  bool _isSending = false;
  bool _fetching = false;
  bool _hasOlder = true;
  bool _loadingOlder = false;
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _loadMessages();
    _pollTimer = Timer.periodic(const Duration(seconds: 6), (_) {
      _loadMessages(silent: true);
    });
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _messageCtrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadMessages({bool silent = false}) async {
    if (_fetching || !mounted || !ApiService.isAuthenticated) return;
    _fetching = true;
    final sessionToken = ApiService.token;
    if (!silent) setState(() => _isLoading = true);
    try {
      final list = await ApiService.getChatMessages(
        widget.otherUserId,
        afterId: _messages.isNotEmpty ? _messages.last.id : null,
      );
      if (!mounted || ApiService.token != sessionToken) return;
      setState(() {
        if (_messages.isEmpty) _hasOlder = list.length == 100;
        final ids = _messages.map((message) => message.id).toSet();
        _messages.addAll(list.where((message) => !ids.contains(message.id)));
        _messages.sort((a, b) => a.id.compareTo(b.id));
        _isLoading = false;
      });
      if (list.isNotEmpty) _scrollToBottom();
    } catch (e) {
      if (mounted && !silent) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Mesajlar yüklənmədi. Yenidən cəhd edin.'),
          ),
        );
      }
    } finally {
      _fetching = false;
    }
  }

  Future<void> _loadOlder() async {
    if (_loadingOlder || _messages.isEmpty) return;
    setState(() => _loadingOlder = true);
    final sessionToken = ApiService.token;
    try {
      final list = await ApiService.getChatMessages(
        widget.otherUserId,
        beforeId: _messages.first.id,
      );
      if (!mounted || ApiService.token != sessionToken) return;
      setState(() {
        final ids = _messages.map((message) => message.id).toSet();
        _messages.insertAll(
          0,
          list.where((message) => !ids.contains(message.id)),
        );
        _hasOlder = list.length == 100;
      });
    } finally {
      if (mounted) setState(() => _loadingOlder = false);
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  String _formatMsgTime(String raw) {
    final dt = DateTime.tryParse(raw)?.toLocal();
    if (dt == null) return raw;
    String two(int n) => n.toString().padLeft(2, '0');
    return '${two(dt.hour)}:${two(dt.minute)}';
  }

  Future<void> _sendMessage() async {
    final text = _messageCtrl.text.trim();
    if (text.isEmpty || _isSending) return;

    setState(() => _isSending = true);
    try {
      final msg = await ApiService.sendMessage(
        otherUserId: widget.otherUserId,
        metn: text,
        elanId: widget.elanId,
      );
      if (!mounted) return;
      _messageCtrl.clear();
      if (mounted) {
        setState(() {
          _messages.add(msg);
        });
        _scrollToBottom();
      }
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
        setState(() => _isSending = false);
      }
    }
  }

  void _showReportDialog() {
    String selectedReason = 'uygunsuz';
    final qeydCtrl = TextEditingController();
    bool isSubmitting = false;

    final reasons = [
      {'key': 'uygunsuz', 'label': 'Uyğunsuz / təhqiramiz mesajlar'},
      {'key': 'spam', 'label': 'Spam və ya reklam'},
      {'key': 'saxta', 'label': 'Fırıldaqçılıq cəhdi'},
      {'key': 'tehdid', 'label': 'Təhdid və ya təqib'},
      {'key': 'diger', 'label': 'Digər'},
    ];

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) {
          return AlertDialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(18),
            ),
            title: Row(
              children: const [
                Icon(Icons.flag_outlined, color: Color(0xFFEF4444)),
                SizedBox(width: 8),
                Text(
                  'İstifadəçidən şikayət',
                  style: TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
                ),
              ],
            ),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Şikayət səbəbini seçin:',
                    style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                  ),
                  const SizedBox(height: 8),
                  RadioGroup<String>(
                    groupValue: selectedReason,
                    onChanged: (val) {
                      if (val != null) {
                        setDialogState(() => selectedReason = val);
                      }
                    },
                    child: Column(
                      children: reasons
                          .map(
                            (r) => RadioListTile<String>(
                              value: r['key']!,
                              dense: true,
                              contentPadding: EdgeInsets.zero,
                              title: Text(
                                r['label']!,
                                style: const TextStyle(fontSize: 13.5),
                              ),
                            ),
                          )
                          .toList(),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: qeydCtrl,
                    maxLines: 2,
                    decoration: const InputDecoration(
                      hintText: 'Əlavə qeyd (istəyə bağlı)',
                      border: OutlineInputBorder(),
                      isDense: true,
                    ),
                  ),
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
                ),
                onPressed: isSubmitting
                    ? null
                    : () async {
                        setDialogState(() => isSubmitting = true);
                        final messenger = ScaffoldMessenger.of(context);
                        try {
                          final msg = await ApiService.reportContent(
                            userId: widget.otherUserId,
                            elanId: widget.elanId,
                            sebeb: selectedReason,
                            qeyd: qeydCtrl.text.trim(),
                          );
                          if (ctx.mounted) Navigator.pop(ctx);
                          messenger.showSnackBar(SnackBar(content: Text(msg)));
                        } catch (e) {
                          setDialogState(() => isSubmitting = false);
                          messenger.showSnackBar(
                            SnackBar(
                              content: Text(
                                e.toString().replaceFirst('Exception: ', ''),
                              ),
                            ),
                          );
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
                    : const Text('Göndər'),
              ),
            ],
          );
        },
      ),
    );
  }

  void _showBlockConfirmation() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
        title: const Text(
          'İstifadəçini blokla',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        content: Text(
          '${widget.otherUserName} adlı istifadəçini bloklamaq istəyirsiniz?\n\nBloklandıqdan sonra onun elanları və mesajları sizə görünməyəcək.',
          style: const TextStyle(height: 1.45),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('İmtina'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEF4444),
              foregroundColor: Colors.white,
            ),
            onPressed: () async {
              Navigator.pop(ctx);
              try {
                final blocked = await ApiService.toggleBlockUser(
                  widget.otherUserId,
                );
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        blocked
                            ? '${widget.otherUserName} bloklandı'
                            : '${widget.otherUserName} blokdan çıxarıldı',
                      ),
                    ),
                  );
                  if (blocked) {
                    Navigator.pop(context);
                  }
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        e.toString().replaceFirst('Exception: ', ''),
                      ),
                    ),
                  );
                }
              }
            },
            child: const Text('Blokla'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final currentUser = context.watch<AuthProvider>().user;
    final isSystem = widget.otherUserName.toLowerCase().contains('sistem');
    final myInitial = (currentUser != null && currentUser.fullName.isNotEmpty)
        ? currentUser.fullName[0].toUpperCase()
        : 'M';

    return Scaffold(
      backgroundColor: const Color(0xFFF4F8F6),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        titleSpacing: 0,
        title: Row(
          children: [
            CircleAvatar(
              radius: 19,
              backgroundColor: _brandLight,
              child: isSystem
                  ? const Icon(
                      Icons.campaign_rounded,
                      color: _brandPrimary,
                      size: 20,
                    )
                  : Text(
                      widget.otherUserName.isNotEmpty
                          ? widget.otherUserName[0].toUpperCase()
                          : 'U',
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        color: _brandPrimary,
                        fontSize: 15,
                      ),
                    ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.otherUserName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 15.5,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 1),
                  Text(
                    isSystem
                        ? 'Rəsmi Bildiriş'
                        : (widget.elanTitle != null && widget.elanTitle!.isNotEmpty)
                            ? 'Online • ${widget.elanTitle!}'
                            : 'Online',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 11.5,
                      color: isSystem
                          ? const Color(0xFF007B52)
                          : const Color(0xFF0FA968),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () => _loadMessages(),
            icon: const Icon(
              Icons.refresh_rounded,
              color: Color(0xFF0F172A),
              size: 21,
            ),
          ),
          if (!isSystem)
            PopupMenuButton<String>(
            icon: const Icon(
              Icons.more_vert_rounded,
              color: Color(0xFF0F172A),
              size: 21,
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
            onSelected: (val) {
              if (val == 'report') {
                _showReportDialog();
              } else if (val == 'block') {
                _showBlockConfirmation();
              }
            },
            itemBuilder: (ctx) => [
              const PopupMenuItem(
                value: 'report',
                child: Row(
                  children: [
                    Icon(
                      Icons.flag_outlined,
                      size: 20,
                      color: Color(0xFFEF4444),
                    ),
                    SizedBox(width: 10),
                    Text('Şikayət et'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'block',
                child: Row(
                  children: [
                    Icon(
                      Icons.block_rounded,
                      size: 20,
                      color: Color(0xFF64748B),
                    ),
                    SizedBox(width: 10),
                    Text('İstifadəçini blokla'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Column(
            children: [
              if (_hasOlder && _messages.isNotEmpty)
                TextButton(
                  onPressed: _loadingOlder ? null : _loadOlder,
                  child: Text(
                    _loadingOlder ? 'Yüklənir…' : 'Əvvəlki mesajları yüklə',
                  ),
                ),
              const Divider(height: 1, color: Color(0xFFE2E8F0)),
              Expanded(
                child: _isLoading
                    ? const Center(
                        child: CircularProgressIndicator(color: _brandPrimary),
                      )
                    : _messages.isEmpty
                    ? const Center(
                        child: Text(
                          'Mesaj yazaraq söhbətə başlayın',
                          style: TextStyle(
                            color: Color(0xFF64748B),
                            fontSize: 13.5,
                          ),
                        ),
                      )
                    : ListView.separated(
                        controller: _scrollCtrl,
                        physics: const BouncingScrollPhysics(),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 14,
                          vertical: 16,
                        ),
                        itemCount: _messages.length,
                        separatorBuilder: (_, _) =>
                            const SizedBox(height: 14.0),
                        itemBuilder: (context, index) {
                          final msg = _messages[index];
                          final isMine = msg.isMine;
                          return _buildChatTwoMessageRow(
                            msg: msg,
                            isMine: isMine,
                            myInitial: myInitial,
                            myAvatarUrl: currentUser?.profil.avatar,
                          );
                        },
                      ),
              ),
              // ChatTwoPage (chat2.dart) Floating Pill Input Bar
              SafeArea(
                top: false,
                child: Container(
                  margin: const EdgeInsets.symmetric(
                    vertical: 10.0,
                    horizontal: 14.0,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(30.0),
                    border: Border.all(color: const Color(0xFFDCECE5)),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF0F172A).withValues(alpha: 0.06),
                        blurRadius: 14,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  padding: const EdgeInsets.symmetric(
                    vertical: 4.0,
                    horizontal: 16.0,
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _messageCtrl,
                          textInputAction: TextInputAction.send,
                          onSubmitted: (_) => _sendMessage(),
                          style: const TextStyle(
                            fontSize: 14.5,
                            color: Color(0xFF0F172A),
                            fontWeight: FontWeight.w500,
                          ),
                          decoration: const InputDecoration(
                            hintText: 'Mesaj yazın...',
                            hintStyle: TextStyle(
                              color: Color(0xFF94A3B8),
                              fontSize: 14,
                            ),
                            border: InputBorder.none,
                            contentPadding: EdgeInsets.symmetric(
                              vertical: 10.0,
                              horizontal: 4.0,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Container(
                        width: 40,
                        height: 40,
                        decoration: const BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Color(0xFF0FA968), Color(0xFF007B52)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          shape: BoxShape.circle,
                        ),
                        child: IconButton(
                          padding: EdgeInsets.zero,
                          color: Colors.white,
                          onPressed: _isSending ? null : _sendMessage,
                          icon: _isSending
                              ? const SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Colors.white,
                                  ),
                                )
                              : const Icon(Icons.send_rounded, size: 19),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Adapted directly from `flutter_ui_challenges/lib/src/pages/misc/chat2.dart` (`_buildMessageRow`)
  Widget _buildChatTwoMessageRow({
    required ChatMessageModel msg,
    required bool isMine,
    required String myInitial,
    String? myAvatarUrl,
  }) {
    const double radius = 20.0;
    return Row(
      mainAxisAlignment: isMine
          ? MainAxisAlignment.end
          : MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: <Widget>[
        if (!isMine) ...[
          CircleAvatar(
            radius: 16.0,
            backgroundColor: _brandLight,
            child: Text(
              widget.otherUserName.isNotEmpty
                  ? widget.otherUserName[0].toUpperCase()
                  : 'U',
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w800,
                color: _brandPrimary,
              ),
            ),
          ),
          const SizedBox(width: 6.0),
        ],
        Flexible(
          child: Column(
            crossAxisAlignment: isMine
                ? CrossAxisAlignment.end
                : CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  vertical: 10.0,
                  horizontal: 15.0,
                ),
                constraints: BoxConstraints(
                  maxWidth: MediaQuery.of(context).size.width * 0.70,
                ),
                decoration: BoxDecoration(
                  color: isMine ? const Color(0xFF007B52) : Colors.white,
                  borderRadius: BorderRadius.only(
                    topLeft: const Radius.circular(radius),
                    topRight: const Radius.circular(radius),
                    bottomLeft: isMine
                        ? const Radius.circular(radius)
                        : Radius.zero,
                    bottomRight: isMine
                        ? Radius.zero
                        : const Radius.circular(radius),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF0F172A).withValues(alpha: 0.05),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      msg.metn,
                      style: TextStyle(
                        color: isMine ? Colors.white : const Color(0xFF0F172A),
                        fontSize: 14.0,
                        height: 1.38,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 3.0),
                    Icon(
                      Icons.done_all_rounded,
                      size: 13.0,
                      color: isMine
                          ? Colors.white.withValues(alpha: 0.85)
                          : const Color(0xFF0FA968),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 3.0),
              Text(
                _formatMsgTime(msg.yaradildi),
                style: const TextStyle(
                  fontSize: 11.0,
                  color: Color(0xFF64748B),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
        if (isMine) ...[
          const SizedBox(width: 6.0),
          CircleAvatar(
            radius: 16.0,
            backgroundColor: const Color(0xFF0FA968),
            backgroundImage:
                (myAvatarUrl != null && myAvatarUrl.trim().isNotEmpty)
                ? CachedNetworkImageProvider(myAvatarUrl)
                : null,
            child: (myAvatarUrl == null || myAvatarUrl.trim().isEmpty)
                ? Text(
                    myInitial,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                    ),
                  )
                : null,
          ),
        ],
      ],
    );
  }
}
