import 'dart:async';
import 'package:flutter/material.dart';
import 'package:nok_mobile_app/models/request.dart';
import 'package:cached_network_image/cached_network_image.dart';
// Assuming ApiService is accessible (or RequestService wrapper)
import 'package:nok_mobile_app/services/api_service.dart';
import 'package:nok_mobile_app/services/snackbar_service.dart';

class RequestDetailsScreen extends StatefulWidget {
  final OutstandingRequest request;
  final Function(String) onStatusChange;

  const RequestDetailsScreen({
    super.key,
    required this.request,
    required this.onStatusChange,
  });

  @override
  State<RequestDetailsScreen> createState() => _DetailScreenState();
}

class _DetailScreenState extends State<RequestDetailsScreen> {
  late Timer _expirationTimer;
  late int _remainingSeconds;
  final double imageSize = 250.0;
  // New state variable for tracking API action loading
  bool _isActionProcessing = false;

  @override
  void initState() {
    super.initState();
    _startCountdown();
  }

  void _startCountdown() {
    final now = DateTime.now();
    final expirationTime = widget.request.timestamp.add(
      OutstandingRequest.approvalDuration,
    );

    if (expirationTime.isAfter(now)) {
      _remainingSeconds = expirationTime.difference(now).inSeconds;
    } else {
      _remainingSeconds = 0;
    }

    // Start a 1-second timer to update the display
    _expirationTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_remainingSeconds > 0) {
        setState(() {
          _remainingSeconds--;
        });
      } else {
        timer.cancel();
        // If the status is still 'pending' after expiration, update UI
        if (widget.request.status == 'pending') {
          setState(() {});
        }
      }
    });
  }

  @override
  void dispose() {
    _expirationTimer.cancel();
    super.dispose();
  }

  // MODIFIED: Function to handle button click, API call, and navigation
  void _handleAction(String newStatus) async {
    if (widget.request.isExpired ||
        widget.request.status != 'pending' ||
        _isActionProcessing) {
      return; // Prevent action if expired, already processed, or currently processing
    }

    setState(() {
      _isActionProcessing = true; // Show loader
    });

    try {
      // 1. Call the API to update the status
      final success = await ApiService().updateStatusOutstandingRequests(
        widget.request.requestId,
        newStatus,
      );

      if (success == true) {
        // 2. Local status update and success feedback
        setState(() {
          widget.request.status = newStatus;
          _isActionProcessing = false;
        });

        SnackbarService.show(
          'Request ${newStatus.toUpperCase()} successful! ✅',
        );

        // 3. Notify the list screen and go back
        widget.onStatusChange(newStatus);
        Navigator.of(context).pop();
      } else {
        // API call returned false (or null), show failure
        setState(() {
          _isActionProcessing = false;
        });
        SnackbarService.show('Action failed. Please try again.', isError: true);
      }
    } catch (e) {
      // 4. Handle exceptions (network error, timeout, etc.)
      setState(() {
        _isActionProcessing = false;
      });
      SnackbarService.show('An error occurred: $e', isError: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isPending = widget.request.status == 'pending';
    // isActionable is now ANDed with the processing state
    final isActionable =
        isPending && _remainingSeconds > 0 && !_isActionProcessing;

    // Format the remaining time (MM:SS)
    String formattedTime = '0:00';
    if (_remainingSeconds > 0) {
      int minutes = _remainingSeconds ~/ 60;
      int seconds = _remainingSeconds % 60;
      formattedTime = '$minutes:${seconds.toString().padLeft(2, '0')}';
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Request ID: ${widget.request.requestId.substring(0, 8)}...',
          style: const TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.black,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Countdown Timer Section
          Container(
            padding: const EdgeInsets.all(16.0),
            color:
                isActionable ? Colors.lightGreen.shade100 : Colors.red.shade100,
            child: Column(
              children: [
                Text(
                  isActionable ? 'Time Remaining for Action' : 'Action Status',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Text(
                  isActionable
                      ? formattedTime
                      : widget.request.isExpired
                      ? 'EXPIRED'
                      : widget.request.status.toUpperCase(),
                  style: TextStyle(
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                    color:
                        isActionable
                            ? Colors.green.shade700
                            : Colors.red.shade700,
                  ),
                ),
              ],
            ),
          ),

          const Divider(),

          // Images Section (using AspectRatio for square images)
          Expanded(
            child:
                widget.request.images.isEmpty
                    ? const Center(child: Text('No images provided'))
                    : ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: widget.request.images.length,
                      itemBuilder: (context, index) {
                        final imageUrl = widget.request.images[index];
                        return Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8.0),
                            child: AspectRatio(
                              aspectRatio: 1.0,
                              child: CachedNetworkImage(
                                imageUrl: imageUrl,
                                placeholder:
                                    (context, url) => const Center(
                                      child: CircularProgressIndicator(),
                                    ),
                                errorWidget:
                                    (context, url, error) =>
                                        const Icon(Icons.error),
                                fit: BoxFit.cover,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
          ),

          // Action Buttons Section
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child:
                  _isActionProcessing
                      ? const Center(
                        child: CircularProgressIndicator(), // Show loader here
                      )
                      : Row(
                        // Show buttons only if not processing
                        children: [
                          Expanded(
                            child: ElevatedButton(
                              onPressed:
                                  isActionable
                                      ? () => _handleAction('approved')
                                      : null,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.green,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(
                                  vertical: 15,
                                ),
                              ),
                              child: const Text(
                                'Approve',
                                style: TextStyle(fontSize: 18),
                              ),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: ElevatedButton(
                              onPressed:
                                  isActionable
                                      ? () => _handleAction('denied')
                                      : null,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.red,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(
                                  vertical: 15,
                                ),
                              ),
                              child: const Text(
                                'Decline',
                                style: TextStyle(fontSize: 18),
                              ),
                            ),
                          ),
                        ],
                      ),
            ),
          ),
        ],
      ),
    );
  }
}
