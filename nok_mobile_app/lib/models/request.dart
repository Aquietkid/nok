import 'package:uuid/uuid.dart';

class OutstandingRequest {
  final String requestId;
  final DateTime timestamp;
  final List<String> images;
  String status;

  // The duration for approval/decline is 2 minutes
  static const approvalDuration = Duration(minutes: 2);

  OutstandingRequest({
    required this.requestId,
    required this.timestamp,
    required this.images,
    this.status = "pending",
  });

  // Helper to check if the request is expired
  bool get isExpired {
    final expiryTime = timestamp.toUtc().add(approvalDuration);

    final nowUtc = DateTime.now().toUtc();

    return nowUtc.isAfter(expiryTime);
  }

  @override
  String toString() {
    // Calculate values we want to print
    final expiryTime = timestamp.toUtc().add(approvalDuration);
    final nowUtc = DateTime.now().toUtc();

    print("Now: ${nowUtc}, expiryTime: ${expiryTime}");

    return "";
  }
}
