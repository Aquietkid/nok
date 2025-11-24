import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:nok_mobile_app/config.dart';
import 'package:nok_mobile_app/models/person.dart';
import 'package:nok_mobile_app/models/request.dart';
import 'package:nok_mobile_app/models/user.dart';
import 'package:nok_mobile_app/services/snackbar_service.dart';
import 'package:nok_mobile_app/services/storage.dart';
import 'package:nok_mobile_app/utils/api_handler.dart';

class ApiService {
  String baseUrl = Config().baseUrl;

  Future<bool?> signIn(String email, String password) async {
    final response = await apiHandler<Future<bool>>(
      () => http.post(
        Uri.parse("$baseUrl/api/auth/login"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email, "password": password}),
      ),
      (response) async {
        final token = response['data']?['token'];
        final user = response['data']?['user'];
        // also save response.data.user

        if (token != null) {
          await Storage.saveToken(token);
          final _user = User.fromJson(user);
          await Storage.saveUser(_user);
          SnackbarService.show("Login successful 🎉");
          return true;
        } else {
          SnackbarService.show("Login failed: Missing token");
          return false;
        }
      },
    );
    return response.success;
  }

  Future<List<Person>> getAllPerson() async {
    final token = await Storage.getToken();
    List<Person> p = [];

    final response = await apiHandler<List<Person>>(
      () => http.get(
        Uri.parse("$baseUrl/api/person/"),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      ),
      (data) {
        final persons =
            (data['data'] as List)
                .map((p) => Person(name: p["name"], image: p["picture"]))
                .toList();
        return persons;
      },
    );

    List<Person>? result = response.data;
    if (result != null) {
      p = result;
    }
    return p;
  }

  Future<bool?> authenticate() async {
    final token = await Storage.getToken();

    final response = await apiHandler<Future<bool>>(
      () => http.get(
        Uri.parse("$baseUrl/api/auth/authenticate"),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      ),
      (_data) async {
        final userJson = _data['data']?['user'];
        print(userJson);

        final _user = User.fromJson(userJson);
        await Storage.saveUser(_user);

        return true;
      },
    );
    return response.data;
  }

  Future<bool?> saveFCMToken(String fcm_token) async {
    final token = await Storage.getToken();

    final response = await apiHandler<Future<bool>>(
      () => http.post(
        Uri.parse("$baseUrl/api/fcm/save_fcm"),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
        body: jsonEncode({"token": fcm_token}),
      ),
      (_data) async {
        return true;
      },
    );
    return response.data;
  }

  Future<List<OutstandingRequest>?> getAllOutstandingRequests() async {
    final token = await Storage.getToken();

    final response = await apiHandler<Future<List<OutstandingRequest>>>(
      () => http.get(
        Uri.parse("$baseUrl/api/outstanding-request/all"),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      ),
      (_data) async {
        final List rawDataList = _data['data'] as List;

        final requests =
            rawDataList
                .map(
                  (p) => OutstandingRequest(
                    requestId: p["request_id"], // Use snake_case from JSON
                    // FIX 1: Parse the ISO 8601 timestamp string into a DateTime object.
                    timestamp: DateTime.parse(p["timestamp"]).toUtc(),

                    // FIX 2: Map the 'images' field (which is a List<String>)
                    images: List<String>.from(p["images"]),

                    // Add the 'status' field, which should also be present in the response
                    status: p["status"],
                  ),
                )
                .toList();
        return requests;
      },
    );
    return response.data;
  }

  Future<bool?> updateStatusOutstandingRequests(
    String request_id,
    String status, // approved, denied
  ) async {
    final token = await Storage.getToken();

    final response = await apiHandler<Future<bool>>(
      () => http.put(
        Uri.parse("$baseUrl/api/outstanding-request/update-status"),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
        body: jsonEncode({"request_id": request_id, "status": status}),
      ),
      (_data) async {
        return true;
      },
    );
    return response.data;
  }
}
