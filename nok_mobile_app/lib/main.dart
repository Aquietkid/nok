import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:nok_mobile_app/screens/home_screen.dart';
import 'package:nok_mobile_app/screens/outstanding_screen.dart';
import 'package:nok_mobile_app/screens/request_detail_screen.dart';
import 'package:nok_mobile_app/screens/request_list_screen.dart';
import 'package:nok_mobile_app/screens/signin_screen.dart';
import 'package:nok_mobile_app/screens/signup_screen.dart';
import 'package:nok_mobile_app/services/api_service.dart';
import 'package:nok_mobile_app/utils/auth_gate.dart';
import 'package:nok_mobile_app/utils/flutter_local_notification.dart';

Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
}

final GlobalKey<ScaffoldMessengerState> rootScaffoldMessengerKey =
    GlobalKey<ScaffoldMessengerState>();

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  late FirebaseMessaging messaging;
  final api = ApiService();

  @override
  void initState() {
    messaging = FirebaseMessaging.instance;
    messaging.requestPermission();
    super.initState();

    setupNotificationListeners();
  }

  void setupNotificationListeners() {
    FirebaseMessaging.onMessageOpenedApp.listen((message) {
      print("Notification tapped (background)");
      handleRedirect("outstanding");
    });

    FirebaseMessaging.instance.getInitialMessage().then((message) {
      if (message != null) {
        print("Notification tapped (terminated)");
        handleRedirect("outstanding");
      }
    });

    FirebaseMessaging.onMessage.listen((message) {
      print("Message in foreground");
      rootScaffoldMessengerKey.currentState?.showSnackBar(
        SnackBar(
          content: Text(message.notification?.title ?? "New notification"),
          duration: Duration(seconds: 3),
        ),
      );
    });
  }

  void handleRedirect(String screenName) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (screenName == "outstanding") {
        navigatorKey.currentState?.push(
          MaterialPageRoute(builder: (_) => const OutstandingScreen()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: navigatorKey,
      title: 'Nok',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.black),
      ),
      scaffoldMessengerKey: rootScaffoldMessengerKey,
      home: const AuthGate(),
      routes: {
        '/home': (context) => const HomeScreen(),
        '/signin': (context) => const SignInScreen(),
        '/signup': (context) => const SignUpScreen(),
        '/outstanding': (context) => const RequestsListScreen(),
      },
    );
  }
}
