# Import Flows

Resume and LinkedIn import flows and data models.

## Resume import (PDF / DOCX)

1. **Select file** – File picker (mobile) or drag-drop (desktop). Validate type (PDF, DOCX).
2. **Upload & parse** – Send to backend; show progress. Backend returns extracted text and parsed structure (experience, skills).
3. **Review** – Show detected positions, companies, titles, skills. User can edit, remove, or add before merge.
4. **Confirm** – Merge into profile; show success and navigate to profile or home.

## LinkedIn import (PDF)

1. **Select file** – Same as resume; typically one PDF export from LinkedIn.
2. **Upload & parse** – Backend parses experience and education sections.
3. **Review** – Side-by-side or stacked: existing vs imported. User chooses what to merge and resolves conflicts.
4. **Confirm** – Merge into profile.json; success and navigation.

## Data models

- **Parsed experience**: title, company, dates, description (optional).
- **Parsed education**: institution, degree, dates.
- **Parsed skills**: list of strings or tagged entities.
- Frontend maps these to app core models (Experience, Education, Skill) for display and merge.

## Implementation (frontend)

- **Route**: `/import` – ImportWizardScreen (4 steps).
- **State**: importStepProvider (1–4), importSourceProvider (resume | linkedIn), importFilePathProvider, importParsingProvider, importParsedResultProvider. Stub `parseImportFile()` returns sample ParsedImportResult; replace with backend upload + parse API.
- **Steps**: 1) Choose source (Resume PDF/DOCX or LinkedIn PDF), 2) Select file (button; desktop can add drag-drop later), 3) Parsing (progress), 4) Review (experiences, education, skills) and "Merge into profile". Uses AppCard, AppButton, design system.
- **Models**: ParsedExperience, ParsedEducation, ParsedImportResult in core/models/import_models.dart.

## Error handling

- Unsupported file or parse failure → clear message and option to try another file.
- Partial parse → show what was detected and allow user to correct.
