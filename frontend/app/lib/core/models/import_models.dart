/// Source of import (resume PDF/DOCX or LinkedIn PDF).
enum ImportSource {
  resume,
  linkedIn,
}

/// Parsed experience entry for review.
class ParsedExperience {
  const ParsedExperience({
    required this.title,
    required this.company,
    this.dates,
    this.description,
  });

  final String title;
  final String company;
  final String? dates;
  final String? description;
}

/// Parsed education entry for review.
class ParsedEducation {
  const ParsedEducation({
    required this.institution,
    this.degree,
    this.dates,
  });

  final String institution;
  final String? degree;
  final String? dates;
}

/// Result of parsing (resume or LinkedIn).
class ParsedImportResult {
  const ParsedImportResult({
    this.experiences = const [],
    this.education = const [],
    this.skills = const [],
  });

  final List<ParsedExperience> experiences;
  final List<ParsedEducation> education;
  final List<String> skills;
}
