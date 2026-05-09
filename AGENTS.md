# Al-Khawarizmi Project - Agent Guidelines

This document provides guidelines for AI agents working on the Al-Khawarizmi project, an Arabic RTL POS/workshop management system for auto repair shops.

## Project Overview

**Al-Khawarizmi** is a Django-based workshop management system designed for auto repair shops in Libya/Libyan market. Key features include:
- Customer and vehicle management
- Repair order processing with parts and labor tracking
- Inventory management for spare parts and oils
- Worker salary management
- Invoice generation and reporting
- Arabic interface with Libyan Dinar (د.ل) currency

## Technology Stack

- **Backend**: Django 4.2 with Python 3.9
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap 5 RTL
- **Styling**: Custom CSS with HeroUI-inspired design system
- **JavaScript**: jQuery 3.6.0, SweetAlert2 11, custom utilities
- **Fonts**: Tajawal (Arabic), Material Icons Round
- **Deployment**: Gunicorn + Nginx (single server target)

## Coding Standards & Conventions

### 1. General Principles
- Keep changes minimal and focused
- Follow existing code patterns and conventions
- Maintain Arabic RTL interface throughout
- Preserve `PROTECT` on foreign keys where data integrity is critical
- Use Decimal fields for all monetary values (never Float)

### 2. Django-Specific Guidelines
- Models: Use `DecimalField(max_digits=12, decimal_places=2)` for monetary values
- Views: Use function-based views with clear separation of concerns
- Forms: Use ModelForms with Arabic labels and placeholders
- Templates: Extend `base.html`, use template includes for reusable components
- URLs: Use descriptive names with consistent patterns (`add_*`, `edit_*`, `delete_*`, `*_details`)

### 3. Database Constraints
- All monetary fields must have `CheckConstraint` for non-negative values
- Quantity fields must have `CheckConstraint` for positive values where appropriate
- Use `PROTECT` on foreign keys where deletion would cause data loss
- Use `SET_NULL` where appropriate for optional relationships

### 4. Security Requirements
- All delete operations must use POST with CSRF protection
- Login attempts must be rate-limited (5 attempts per 5 minutes)
- Logout must use POST form
- `@login_required` decorator on all views except login/index
- Production security settings in `settings.py` (HTTPS, HSTS, secure cookies)

### 5. Internationalization & Localization
- Language: Arabic (`ar-LY`)
- Text direction: RTL (right-to-left)
- Currency: Libyan Dinar (د.ل)
- Date format: Local Libyan format
- All user-facing strings must be in Arabic

### 6. File Organization
- Keep sidebar design consistent (do not modify unless explicitly requested)
- Static assets:
  - CSS: `/static/css/` (style.css, sidebar.css, fixes.css)
  - JavaScript: `/static/js/` (script.js, repair-form.js, arabic-date.js)
  - Libraries: `/static/libs/` (localized jQuery and SweetAlert2)
  - Images: `/static/img/`
- Templates: `/templates/` with includes in `/templates/includes/`
- Translations: Not currently used (all text hardcoded in Arabic)

## Common Tasks & Patterns

### Adding New Model Fields
1. Add field to model in `core/models.py`
2. Add appropriate constraints (CheckConstraint for monetary/quantity fields)
3. Create and apply migration
4. Update forms in `core/forms.py` if needed
5. Update views to handle new field
6. Update templates to display/edit new field

### Adding New Views
1. Add view function in `core/views.py`
2. Add URL pattern in `core/urls.py`
3. Create template(s) in `/templates/`
4. Add navigation link in `core/context_processors.py` if needed
5. Update base template if adding major sections

### Modifying Existing Templates
1. Always extend `base.html` (must be first tag)
2. Load static files after extends: `{% load static %}`
3. Use `{% include 'includes/page_header.html' %}` for consistent headers
4. Use existing template patterns for forms, tables, action buttons
5. Follow ARIA attributes and semantic HTML where appropriate

### Working with Money
1. Always use `Decimal` for monetary calculations
2. Import `Decimal` from `decimal` module
3. Use string initialization: `Decimal("0.00")`
4. Format display with `|floatformat:2` template filter
5. Never use `float()` for money except for display percentages

## Testing Guidelines

- All changes must maintain or improve test coverage
- Run `python3 manage.py test` before considering work complete
- Focus on testing:
  - Model constraints and validation
  - Form validation and saving
  - View responses and redirects
  - Template rendering and context
  - Service functions and business logic

## UI/UX Guidelines

- Use HeroUI-inspired design system (soft shadows, glassmorphism, vibrant colors)
- Maintain consistent spacing using the 8px grid system
- Use appropriate badge colors for status indicators:
  - Success: Green (#10b981)
  - Warning: Amber (#f59e0b)
  - Error/Danger: Red (#f43f5e)
  - Info: Blue (#3b82f6)
  - Primary: Cyan (#06b6d4)
- Buttons should have clear hover and active states
- Forms should show validation errors clearly
- Tables should be responsive and readable on mobile
- Loading states should be provided for async operations

## Performance Considerations

- Minimize database queries (use `select_related`, `prefetch_related`)
- Use pagination for large lists (25 items per page)
- Cache expensive operations where appropriate
- Optimize template rendering with efficient queries
- Consider database indexing for frequently queried fields

## Deployment Notes

- Target deployment: Single server with Gunicorn + Nginx
- Static files served by WhiteNoise in production
- Environment variables managed via python-decouple
- Database migrations must be backward compatible
- Backup strategy: Automatic backup before restore operations

## File References

Key files to understand before making changes:
- `core/models.py` - Data models and constraints
- `core/views.py` - Application logic and view functions
- `core/services.py` - Business logic and helper functions
- `core/forms.py` - Form definitions and validation
- `core/decorators.py` - Custom decorators (rate limiting)
- `templates/base.html` - Base template with CSS/JS includes
- `static/css/style.css` - Main styling (HeroUI-inspired)
- `static/css/sidebar.css` - Sidebar styling
- `static/css/fixes.css` - Component-level fixes
- `alkhawarizmi/settings.py` - Django configuration
- `core/urls.py` - URL routing