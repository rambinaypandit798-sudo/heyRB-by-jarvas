import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/rbai_service.dart';
import 'screens/home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => RBAIService()),
      ],
      child: const RBAssistantApp(),
    ),
  );
}

class RBAssistantApp extends StatelessWidget {
  const RBAssistantApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RB Agent — Autonomous Operating System',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.light().copyWith(
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        primaryColor: const Color(0xFF0077FE),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: Color(0xFF0F172A),
          elevation: 0.5,
        ),
        colorScheme: const ColorScheme.light(
          primary: Color(0xFF0077FE),
          secondary: Color(0xFF00E5FF),
          surface: Colors.white,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
