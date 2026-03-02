# Content Idea Generator Skill - TDD Test Suite

## Test Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TDD Test Pyramid                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────────────────────────────────────────────┐    │
│   │              End-to-End Tests (3)                      │    │
│   │  - Complete user workflow                              │    │
│   │  - Daily report delivery                               │    │
│   │  - Content suggestion interaction                      │    │
│   └───────────────────────────────────────────────────────┘    │
│                                                                 │
│   ┌───────────────────────────────────────────────────────┐    │
│   │           Integration Tests (3)                        │    │
│   │  - Voice → STT → Storage flow                          │    │
│   │  - Screenshot → OCR → Storage flow                     │    │
│   │  - Daily analysis → Report generation                  │    │
│   └───────────────────────────────────────────────────────┘    │
│                                                                 │
│   ┌───────────────────────────────────────────────────────┐    │
│   │              Unit Tests (16)                           │    │
│   │  - Database operations (CRUD)                          │    │
│   │  - Tag/category management                             │    │
│   │  - Full-text search                                    │    │
│   │  - Content parsing                                     │    │
│   └───────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Test Data Strategy

### Test Fixtures
- `fixtures/ideas.json` - Sample content ideas
- `fixtures/voice_samples/` - Audio test files
- `fixtures/screenshots/` - Image test files
- `fixtures/reports/` - Expected report outputs

### Mock External Services
- STT (Speech-to-Text) service
- OCR (Optical Character Recognition) service
- LLM API for content analysis
- Notification service

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run in TDD mode (watch)
pytest-watch tests/ -- -v
```
