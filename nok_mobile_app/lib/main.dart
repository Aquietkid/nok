import 'package:flutter/material.dart';
import 'package:nok_mobile_app/screens/home_screen.dart';
import 'package:nok_mobile_app/screens/signin_screen.dart';
import 'package:nok_mobile_app/screens/signup_screen.dart';

final GlobalKey<ScaffoldMessengerState> rootScaffoldMessengerKey =
    GlobalKey<ScaffoldMessengerState>();

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Nok',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.black),
      ),
      scaffoldMessengerKey: rootScaffoldMessengerKey,
      initialRoute: '/signin',
      routes: {
        '/home': (context) => const HomeScreen(),
        '/signin': (context) => const SignInScreen(),
        '/signup': (context) => const SignUpScreen(),
      },
    );
  }
}
