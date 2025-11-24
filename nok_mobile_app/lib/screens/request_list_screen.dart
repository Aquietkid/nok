import 'package:flutter/material.dart';
import 'package:flutter_countdown_timer/flutter_countdown_timer.dart';
import 'package:nok_mobile_app/models/request.dart';
import 'package:nok_mobile_app/screens/request_detail_screen.dart';
import 'package:nok_mobile_app/services/api_service.dart';

class RequestsListScreen extends StatefulWidget {
  const RequestsListScreen({super.key});

  @override
  State<RequestsListScreen> createState() => _RequestsListScreenState();
}

class _RequestsListScreenState extends State<RequestsListScreen> {
  // Use a List of requests that will be populated by the API call
  List<OutstandingRequest> _requests = [];
  bool _isLoading = true;
  String? _error; // To store any error message
  final ApiService api = ApiService();

  @override
  void initState() {
    super.initState();
    _fetchRequests();
  }

  // Function to call the API
  Future<void> _fetchRequests() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Assuming RequestService is where your API function resides
      final fetchedRequests = await api.getAllOutstandingRequests();

      print('\n--- OUTSTANDING REQUESTS DEBUG START ---');
      for (var request in _requests) {
        // This calls the overridden toString() function
        print(request);
      }
      print('--- OUTSTANDING REQUESTS DEBUG END ---\n');

      setState(() {
        _requests = fetchedRequests ?? [];
        _isLoading = false;
      });
    } catch (e) {
      // Handle potential API errors (network, parsing, etc.)
      setState(() {
        _error = 'Failed to load requests. Please try again later. Error: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Outstanding Requests',
          style: TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.black,
        actions: [
          // Add a refresh button to manually reload data
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _isLoading ? null : _fetchRequests,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      // Show loading indicator while data is being fetched
      return const Center(
        child: CircularProgressIndicator(color: Colors.black),
      );
    }

    if (_error != null) {
      // Show error message if fetch failed
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.red, fontSize: 16),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: _fetchRequests,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (_requests.isEmpty) {
      // Show message if no requests were returned
      return const Center(
        child: Text(
          'No outstanding requests found.',
          style: TextStyle(fontSize: 16, color: Colors.grey),
        ),
      );
    }

    // Display the list of requests
    return ListView.builder(
      itemCount: _requests.length,
      itemBuilder: (context, index) {
        final request = _requests[index];
        // Calculate the exact millisecond time when the request expires
        int endTime =
            request.timestamp
                .toUtc()
                .add(OutstandingRequest.approvalDuration)
                .millisecondsSinceEpoch;
        print('End time for request ${request.requestId}: $endTime');

        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          elevation: 2,
          child: ListTile(
            onTap: () async {
              // Navigate to detail view and await status change
              await Navigator.of(context).push(
                MaterialPageRoute(
                  builder:
                      (context) => RequestDetailsScreen(
                        request: request,
                        onStatusChange: (newStatus) {
                          // This callback updates the original request object
                          request.status = newStatus;
                        },
                      ),
                ),
              );
              // Refresh the list UI after returning from the detail screen
              setState(() {});
            },

            // ... (rest of your ListTile code remains the same)
            leading: Icon(
              request.status == 'approved'
                  ? Icons.check_circle
                  : request.status == 'denied'
                  ? Icons.cancel
                  : Icons.pending,
              color:
                  request.status == 'approved'
                      ? Colors.green
                      : request.status == 'denied'
                      ? Colors.red
                      : Colors.indigo,
            ),
            title: Text('Request ID: ${request.requestId.substring(0, 8)}...'),
            subtitle: Text(
              'Status: ${request.status.toUpperCase()}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: request.status == 'pending' ? Colors.orange : null,
              ),
            ),
            trailing:
                request.status == 'pending'
                    ? (request.isExpired
                        ? const Text(
                          'EXPIRED',
                          style: TextStyle(
                            color: Colors.red,
                            fontWeight: FontWeight.bold,
                          ),
                        )
                        : CountdownTimer(
                          endTime: endTime,
                          widgetBuilder: (_, time) {
                            if (time == null) {
                              // Timer finished - now expired
                              return const Text(
                                'EXPIRED',
                                style: TextStyle(
                                  color: Colors.red,
                                  fontWeight: FontWeight.bold,
                                ),
                              );
                            }
                            // Display MM:SS
                            return Text(
                              '${time.min ?? 0}:${time.sec.toString().padLeft(2, '0')}',
                              style: const TextStyle(
                                color: Colors.orange,
                                fontWeight: FontWeight.bold,
                              ),
                            );
                          },
                          onEnd: () {
                            // Force a refresh when the timer hits zero
                            setState(() {});
                          },
                        ))
                    : null,
          ),
        );
      },
    );
  }
}
