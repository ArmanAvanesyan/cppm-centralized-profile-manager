import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/models/import_models.dart';

/// Current step in the import wizard (1-based).
final importStepProvider = StateProvider<int>((ref) => 1);

/// Selected import source.
final importSourceProvider = StateProvider<ImportSource?>((ref) => null);

/// Selected file path (stub: use string; replace with platform file reference).
final importFilePathProvider = StateProvider<String?>((ref) => null);

/// Parsing in progress.
final importParsingProvider = StateProvider<bool>((ref) => false);

/// Parsed result for review.
final importParsedResultProvider = StateProvider<ParsedImportResult?>((ref) => null);

/// Reset import state (e.g. when leaving wizard).
void resetImportState(Ref ref) {
  ref.read(importStepProvider.notifier).state = 1;
  ref.read(importSourceProvider.notifier).state = null;
  ref.read(importFilePathProvider.notifier).state = null;
  ref.read(importParsingProvider.notifier).state = false;
  ref.read(importParsedResultProvider.notifier).state = null;
}

/// Stub: simulate parse and return sample data.
Future<ParsedImportResult> parseImportFile(ImportSource source, String path) async {
  await Future.delayed(const Duration(seconds: 2));
  return const ParsedImportResult(
    experiences: [
      ParsedExperience(title: 'Senior Engineer', company: 'Acme Inc', dates: '2020 – Present'),
      ParsedExperience(title: 'Engineer', company: 'Startup Co', dates: '2018 – 2020'),
    ],
    education: [
      ParsedEducation(institution: 'University', degree: 'B.S. Computer Science', dates: '2014 – 2018'),
    ],
    skills: ['Flutter', 'Dart', 'Python', 'API design'],
  );
}
