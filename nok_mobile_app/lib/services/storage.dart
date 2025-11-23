import 'dart:convert';

import 'package:nok_mobile_app/models/user.dart';
import 'package:shared_preferences/shared_preferences.dart';

class Storage {
  static const _tokenKey = 'auth_token';
  static const _userKey = 'user';

  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  static Future<void> saveUser(User _user) async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = jsonEncode(_user.toJson());
    await prefs.setString(_userKey, userJson);
  }

  static Future<User?> getUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString(_userKey); // use correct key

    if (userJson == null || userJson.isEmpty) {
      return null;
    }

    final Map<String, String> userMap = jsonDecode(userJson);
    final user = User.fromJson(userMap);

    return user;
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }
}
