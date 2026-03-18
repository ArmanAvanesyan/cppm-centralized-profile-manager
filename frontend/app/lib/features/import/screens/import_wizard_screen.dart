import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/models/import_models.dart';
import '../providers/import_provider.dart';
import '../../../router/app_router.dart';

class ImportWizardScreen extends ConsumerStatefulWidget {
  const ImportWizardScreen({super.key, this.source});

  final ImportSource? source;

  @override
  ConsumerState<ImportWizardScreen> createState() => _ImportWizardScreenState();
}

class _ImportWizardScreenState extends ConsumerState<ImportWizardScreen> {
  @override
  void initState() {
    super.initState();
    if (widget.source != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ref.read(importSourceProvider.notifier).state = widget.source;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final step = ref.watch(importStepProvider);
    final source = ref.watch(importSourceProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Import Profile'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () {
            resetImportState(ref);
            context.go(RouteNames.home);
          },
        ),
      ),
      body: ResponsiveContainer(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.all(AppSpacing.lg),
              child: LinearProgressIndicator(
                value: step / 4,
                backgroundColor: theme.colorScheme.surfaceContainerHighest,
              ),
            ),
            Expanded(
              child: _stepContent(step, source, theme),
            ),
          ],
        ),
      ),
    );
  }

  Widget _stepContent(int step, ImportSource? source, ThemeData theme) {
    switch (step) {
      case 1:
        return _Step1ChooseSource(
          onNext: (s) {
            ref.read(importSourceProvider.notifier).state = s;
            ref.read(importStepProvider.notifier).state = 2;
          },
        );
      case 2:
        return _Step2SelectFile(
          source: source ?? ImportSource.resume,
          onNext: (path) {
            ref.read(importFilePathProvider.notifier).state = path;
            ref.read(importStepProvider.notifier).state = 3;
            _runParse(ref, source ?? ImportSource.resume, path);
          },
        );
      case 3:
        return const _Step3Parsing();
      case 4:
        return _Step4Review(
          onConfirm: () {
            resetImportState(ref);
            context.go(RouteNames.home);
          },
        );
      default:
        return const Center(child: Text('Unknown step'));
    }
  }

  Future<void> _runParse(WidgetRef r, ImportSource source, String path) async {
    r.read(importParsingProvider.notifier).state = true;
    final result = await parseImportFile(source, path);
    if (mounted) {
      r.read(importParsedResultProvider.notifier).state = result;
      r.read(importParsingProvider.notifier).state = false;
      r.read(importStepProvider.notifier).state = 4;
    }
  }
}

class _Step1ChooseSource extends StatelessWidget {
  const _Step1ChooseSource({required this.onNext});

  final ValueChanged<ImportSource> onNext;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Choose import source',
            style: theme.textTheme.titleLarge,
          ),
          const SizedBox(height: AppSpacing.lg),
          AppCard(
            onTap: () => onNext(ImportSource.resume),
            child: Row(
              children: [
                const Icon(Icons.description, size: 40),
                const SizedBox(width: AppSpacing.lg),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Resume (PDF or DOCX)', style: theme.textTheme.titleMedium),
                      Text(
                        'Extract experience and skills',
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.arrow_forward_ios, size: 16),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          AppCard(
            onTap: () => onNext(ImportSource.linkedIn),
            child: Row(
              children: [
                const Icon(Icons.business_center, size: 40),
                const SizedBox(width: AppSpacing.lg),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('LinkedIn export (PDF)', style: theme.textTheme.titleMedium),
                      Text(
                        'Extract experience and education',
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.arrow_forward_ios, size: 16),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Step2SelectFile extends StatelessWidget {
  const _Step2SelectFile({required this.source, required this.onNext});

  final ImportSource source;
  final ValueChanged<String> onNext;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            source == ImportSource.resume
                ? 'Select a resume file (PDF or DOCX)'
                : 'Select your LinkedIn PDF export',
            style: theme.textTheme.titleLarge,
          ),
          const SizedBox(height: AppSpacing.xl),
          AppButton(
            label: 'Choose file',
            variant: AppButtonVariant.primary,
            onPressed: () => onNext('/placeholder/path/to/file.pdf'),
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            'On desktop you can also drag and drop a file here.',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }
}

class _Step3Parsing extends ConsumerWidget {
  const _Step3Parsing();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 24),
          Text(
            'Parsing your file…',
            style: Theme.of(context).textTheme.bodyLarge,
          ),
        ],
      ),
    );
  }
}

class _Step4Review extends ConsumerWidget {
  const _Step4Review({required this.onConfirm});

  final VoidCallback onConfirm;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final result = ref.watch(importParsedResultProvider);
    final theme = Theme.of(context);
    if (result == null) {
      return const Center(child: CircularProgressIndicator());
    }
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Review imported data', style: theme.textTheme.titleLarge),
          const SizedBox(height: AppSpacing.lg),
          if (result.experiences.isNotEmpty) ...[
            Text('Experience', style: theme.textTheme.titleMedium),
            ...result.experiences.map(
              (e) => AppCard(
                child: ListTile(
                  title: Text(e.title),
                  subtitle: Text('${e.company}${e.dates != null ? ' · ${e.dates}' : ''}'),
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
          ],
          if (result.education.isNotEmpty) ...[
            Text('Education', style: theme.textTheme.titleMedium),
            ...result.education.map(
              (e) => AppCard(
                child: ListTile(
                  title: Text(e.institution),
                  subtitle: Text([e.degree, e.dates].whereType<String>().join(' · ')),
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
          ],
          if (result.skills.isNotEmpty) ...[
            Text('Skills', style: theme.textTheme.titleMedium),
            Wrap(
              spacing: 8,
              children: result.skills.map((s) => Chip(label: Text(s))).toList(),
            ),
            const SizedBox(height: AppSpacing.xxl),
          ],
          AppButton(
            label: 'Merge into profile',
            variant: AppButtonVariant.primary,
            onPressed: onConfirm,
          ),
        ],
      ),
    );
  }
}
