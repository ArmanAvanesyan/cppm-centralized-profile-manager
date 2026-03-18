import 'package:flutter/material.dart';

/// CPPM design system color palette.
/// Light and dark semantic colors for background, surface, primary, and feedback.
abstract class AppColors {
  AppColors._();

  // ---------- Light palette ----------
  static const Color primaryLight = Color(0xFF2563EB);
  static const Color primaryContainerLight = Color(0xFFDBEAFE);
  static const Color onPrimaryLight = Color(0xFFFFFFFF);
  static const Color onPrimaryContainerLight = Color(0xFF1E3A8A);

  static const Color secondaryLight = Color(0xFF64748B);
  static const Color secondaryContainerLight = Color(0xFFF1F5F9);
  static const Color onSecondaryLight = Color(0xFFFFFFFF);
  static const Color onSecondaryContainerLight = Color(0xFF334155);

  static const Color backgroundLight = Color(0xFFF8FAFC);
  static const Color surfaceLight = Color(0xFFFFFFFF);
  static const Color onBackgroundLight = Color(0xFF0F172A);
  static const Color onSurfaceLight = Color(0xFF0F172A);
  static const Color onSurfaceVariantLight = Color(0xFF64748B);
  static const Color outlineLight = Color(0xFFCBD5E1);

  static const Color errorLight = Color(0xFFDC2626);
  static const Color onErrorLight = Color(0xFFFFFFFF);
  static const Color errorContainerLight = Color(0xFFFEE2E2);

  static const Color successLight = Color(0xFF16A34A);
  static const Color warningLight = Color(0xFFD97706);
  static const Color infoLight = Color(0xFF0284C7);

  // ---------- Dark palette ----------
  static const Color primaryDark = Color(0xFF60A5FA);
  static const Color primaryContainerDark = Color(0xFF1E3A8A);
  static const Color onPrimaryDark = Color(0xFF0F172A);
  static const Color onPrimaryContainerDark = Color(0xFFDBEAFE);

  static const Color secondaryDark = Color(0xFF94A3B8);
  static const Color secondaryContainerDark = Color(0xFF334155);
  static const Color onSecondaryDark = Color(0xFF1E293B);
  static const Color onSecondaryContainerDark = Color(0xFFE2E8F0);

  static const Color backgroundDark = Color(0xFF0F172A);
  static const Color surfaceDark = Color(0xFF1E293B);
  static const Color onBackgroundDark = Color(0xFFF1F5F9);
  static const Color onSurfaceDark = Color(0xFFF1F5F9);
  static const Color onSurfaceVariantDark = Color(0xFF94A3B8);
  static const Color outlineDark = Color(0xFF475569);

  static const Color errorDark = Color(0xFFF87171);
  static const Color onErrorDark = Color(0xFF7F1D1D);
  static const Color errorContainerDark = Color(0xFF7F1D1D);

  static const Color successDark = Color(0xFF4ADE80);
  static const Color warningDark = Color(0xFFFBBF24);
  static const Color infoDark = Color(0xFF38BDF8);
}
