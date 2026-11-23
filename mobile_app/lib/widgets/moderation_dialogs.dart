import 'package:flutter/material.dart';
import '../services/api_service.dart';

/// Shared report dialog for listings and chat conversations (Google Play UGC).
Future<void> showReportContentDialog({
  required BuildContext context,
  required String title,
  required List<Map<String, String>> reasons,
  required String initialReason,
  int? elanId,
  int? userId,
}) {
  String selectedReason = initialReason;
  final qeydCtrl = TextEditingController();
  bool isSubmitting = false;

  return showDialog<void>(
    context: context,
    builder: (ctx) => StatefulBuilder(
      builder: (dialogContext, setDialogState) {
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
          title: Row(
            children: [
              const Icon(Icons.flag_outlined, color: Color(0xFFEF4444)),
              const SizedBox(width: 8),
              Flexible(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 17,
                  ),
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
                          elanId: elanId,
                          userId: userId,
                          sebeb: selectedReason,
                          qeyd: qeydCtrl.text.trim(),
                        );
                        if (ctx.mounted) Navigator.pop(ctx);
                        messenger.showSnackBar(SnackBar(content: Text(msg)));
                      } catch (e) {
                        if (ctx.mounted) {
                          setDialogState(() => isSubmitting = false);
                        }
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
  ).whenComplete(qeydCtrl.dispose);
}

/// Shared block confirmation dialog for listing owners and chat peers.
Future<void> showBlockUserDialog({
  required BuildContext context,
  required int userId,
  required String userName,
  VoidCallback? onBlocked,
}) {
  return showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      title: const Text(
        'İstifadəçini blokla',
        style: TextStyle(fontWeight: FontWeight.w800),
      ),
      content: Text(
        '$userName adlı istifadəçini bloklamaq istəyirsiniz?\n\nBloklandıqdan sonra onun elanları və mesajları sizə görünməyəcək.',
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
            final messenger = ScaffoldMessenger.of(context);
            try {
              final blocked = await ApiService.toggleBlockUser(userId);
              if (!context.mounted) return;
              messenger.showSnackBar(
                SnackBar(
                  content: Text(
                    blocked
                        ? '$userName bloklandı'
                        : '$userName blokdan çıxarıldı',
                  ),
                ),
              );
              if (blocked) {
                onBlocked?.call();
              }
            } catch (e) {
              if (!context.mounted) return;
              messenger.showSnackBar(
                SnackBar(
                  content: Text(e.toString().replaceFirst('Exception: ', '')),
                ),
              );
            }
          },
          child: const Text('Blokla'),
        ),
      ],
    ),
  );
}
