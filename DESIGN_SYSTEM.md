# RTC KPI System - Modern Black & White Design System

## Overview

This document describes the comprehensive design system implemented for the RTC KPI System. The design follows a modern, minimalist black and white aesthetic with professional brutalist elements, smooth animations, and consistent spacing.

---

## 🎨 Color Palette

### Primary Colors

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| **Primary Black** | `#000000` | Primary actions, headings, important text |
| **Rich Black** | `#0a0a0a` | Alternate black shade for depth |
| **Dark Gray** | `#1a1a1a` | Navigation bars, dark backgrounds |
| **Medium Gray** | `#404040` | Secondary text, borders |
| **Light Gray** | `#808080` | Tertiary text, disabled states |
| **Soft Gray** | `#a0a0a0` | Placeholder text, subtle elements |
| **Pale Gray** | `#d0d0d0` | Light borders, dividers |
| **Off White** | `#f5f5f5` | Page background, subtle backgrounds |
| **Pure White** | `#ffffff` | Cards, primary backgrounds |

### Usage Guidelines

- **Black (#000000)**: Use for primary CTAs, headings, and important information
- **Grays**: Use progressively lighter grays for less important information
- **White**: Use for content cards and primary surfaces
- **Off White**: Use for page backgrounds to reduce eye strain

---

## 📐 Spacing System

The design system uses a consistent spacing scale based on rem units:

| Name | Value | Pixels | Usage |
|------|-------|--------|-------|
| `--space-xs` | 0.25rem | 4px | Tight spacing, icon gaps |
| `--space-sm` | 0.5rem | 8px | Small gaps, form field spacing |
| `--space-md` | 1rem | 16px | Standard spacing, card padding |
| `--space-lg` | 1.5rem | 24px | Section spacing |
| `--space-xl` | 2rem | 32px | Large section spacing |
| `--space-2xl` | 3rem | 48px | Page section spacing |

### Utility Classes

```css
.mt-lg { margin-top: 1.5rem; }
.mb-xl { margin-bottom: 2rem; }
.p-md { padding: 1rem; }
.gap-sm { gap: 0.5rem; }
```

---

## 📝 Typography

### Font Family

**Primary Font**: Inter
- Weights: 400 (Regular), 500 (Medium), 600 (Semi-Bold), 700 (Bold), 800 (Extra Bold), 900 (Black)
- Source: Google Fonts
- Fallback: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif`

### Type Scale

| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| **H1** | 2.5rem (40px) | 700 (Bold) | 1.2 | Page titles |
| **H2** | 2rem (32px) | 700 (Bold) | 1.2 | Section headings |
| **H3** | 1.5rem (24px) | 700 (Bold) | 1.2 | Subsection headings |
| **H4** | 1.25rem (20px) | 700 (Bold) | 1.2 | Card titles |
| **H5** | 1rem (16px) | 700 (Bold) | 1.2 | Small headings |
| **H6** | 0.875rem (14px) | 700 (Bold) | 1.2 | Tiny headings |
| **Body** | 1rem (16px) | 400 (Regular) | 1.6 | Standard text |
| **Small** | 0.875rem (14px) | 400 (Regular) | 1.6 | Secondary text |
| **Tiny** | 0.75rem (12px) | 400 (Regular) | 1.6 | Labels, captions |

### Typography Classes

```css
.font-normal { font-weight: 400; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
.font-black { font-weight: 900; }
```

---

## 🎭 Animations

### Animation Timings

| Speed | Duration | Usage |
|-------|----------|-------|
| **Fast** | 150ms | Quick hover effects, icon transitions |
| **Normal** | 300ms | Standard transitions, button effects |
| **Slow** | 500ms | Page loads, complex animations |

### Easing Function

**Primary**: `cubic-bezier(0.4, 0, 0.2, 1)` - Smooth, natural motion

### Key Animations

#### 1. Fade In (Page Load)
```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
/* Duration: 500ms */
```

#### 2. Hover Lift
```css
/* Lift effect on hover */
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}
/* Transition: 300ms */
```

#### 3. Button Press
```css
.btn:active {
    transform: scale(0.98);
}
/* Transition: 150ms */
```

#### 4. Slide Down (Modals/Dropdowns)
```css
@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
/* Duration: 300ms */
```

#### 5. Brutal Shadow Hover
```css
.card-brutal:hover {
    box-shadow: 12px 12px 0 #000000;
    transform: translate(-2px, -2px);
}
/* Transition: 300ms */
```

---

## 🧩 Components

### Buttons

#### Primary Button
- **Background**: Black (#000000)
- **Text**: White
- **Border**: 2px solid black
- **Hover**: Darker background, lift effect
- **Active**: Scale down to 0.98

```html
<button class="btn-primary">Primary Action</button>
```

#### Secondary Button
- **Background**: White
- **Text**: Black
- **Border**: 2px solid black
- **Hover**: Inverted colors

```html
<button class="btn-secondary">Secondary Action</button>
```

#### Button Sizes
- **Small**: `btn-sm` - Padding: 0.5rem 1rem
- **Default**: Standard padding: 0.75rem 1.5rem
- **Large**: `btn-lg` - Padding: 1rem 2rem

### Cards

#### Standard Card
- **Background**: White
- **Border**: 2px solid pale gray
- **Border Radius**: 0.75rem
- **Padding**: 2rem
- **Shadow**: Medium (0 4px 8px)
- **Hover**: Lift + stronger shadow

```html
<div class="card">
    <!-- Card content -->
</div>
```

#### Brutal Card
- **Background**: White
- **Border**: 3px solid black
- **Box Shadow**: 8px 8px 0 black
- **Hover**: Stronger shadow + position shift

```html
<div class="card-brutal">
    <!-- Card content -->
</div>
```

#### Stat Card
- **Background**: White
- **Border**: 3px solid black
- **Style**: Brutalist with centered content
- **Contains**: Large numeric value + label

```html
<div class="stat-card">
    <div class="stat-card-value">250</div>
    <div class="stat-card-label">Total Users</div>
</div>
```

### Tables

- **Header**: Black gradient background, white text
- **Border**: 3px bottom border on header
- **Rows**: Alternating backgrounds (striped)
- **Hover**: Light gray background
- **Container**: Card-style with border and shadow

```html
<div class="table-container">
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
            </tr>
        </tbody>
    </table>
</div>
```

### Forms

#### Input Fields
- **Border**: 2px solid pale gray
- **Padding**: 0.75rem 1rem
- **Hover**: Border darkens to soft gray
- **Focus**: Black border + shadow ring

```html
<div class="form-group">
    <label class="form-label">Field Label</label>
    <input type="text" class="form-input" placeholder="Enter value">
</div>
```

#### Select Dropdowns
- Same styling as input fields
- Smooth transition on hover/focus

```html
<select class="form-select">
    <option>Option 1</option>
    <option>Option 2</option>
</select>
```

### Badges

- **Border Radius**: Full (pill shape)
- **Padding**: 0.375rem 0.75rem
- **Font**: Bold, uppercase, letter-spacing

#### Variants
- `badge-active`: Black background, white text
- `badge-inactive`: White background, black text, black border
- `badge-approved`: Black background, white text
- `badge-rejected`: White background, black text
- `badge-draft`: Pale gray background, dark text

```html
<span class="badge badge-active">Active</span>
```

### Navigation

- **Background**: Black (#000000)
- **Height**: 80px (5rem)
- **Items**: Spaced with gap-2 (8px margin)
- **Hover**: Darker background, slight lift

```html
<a href="#" class="navbar-item">Menu Item</a>
```

### Alerts

Four types with consistent styling:
- **Success**: White bg, black text, black border
- **Error**: Black bg, white text
- **Warning**: Off-white bg, medium gray text
- **Info**: White bg, dark gray text

```html
<div class="alert alert-success">
    Success message
</div>
```

---

## 🔄 Transitions

### Standard Transitions

All interactive elements use consistent transition properties:

```css
transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
```

### Hover States

- **Cards**: Lift up 2px, increase shadow
- **Buttons**: Lift up 2px, darken background
- **Links**: Change color to medium gray
- **Table Rows**: Change background to off-white

### Active States

- **Buttons**: Scale down to 98%
- **Links**: No additional effect beyond hover

---

## 📱 Responsive Design

### Breakpoints

| Breakpoint | Width | Usage |
|------------|-------|-------|
| **Mobile** | < 768px | Single column layouts |
| **Tablet** | ≥ 768px | Multi-column layouts |
| **Desktop** | ≥ 1024px | Full feature layouts |

### Mobile Optimizations

- Reduced heading sizes (H1: 2rem instead of 2.5rem)
- Reduced card padding (1.5rem instead of 2rem)
- Smaller table fonts (0.75rem instead of 0.875rem)
- Stack navigation items vertically
- Full-width buttons

---

## 🎯 Shadows

### Shadow Scale

| Name | CSS Value | Usage |
|------|-----------|-------|
| **Small** | `0 2px 4px rgba(0,0,0,0.05)` | Small cards, dropdowns |
| **Medium** | `0 4px 8px rgba(0,0,0,0.08)` | Standard cards |
| **Large** | `0 8px 16px rgba(0,0,0,0.12)` | Elevated cards, modals |
| **XL** | `0 12px 24px rgba(0,0,0,0.16)` | Prominent elements |
| **Brutal** | `8px 8px 0 #000000` | Brutalist cards |
| **Brutal Hover** | `12px 12px 0 #000000` | Brutalist hover state |

---

## 🔲 Border Radius

| Name | Value | Usage |
|------|-------|-------|
| **Small** | 0.25rem (4px) | Buttons, small elements |
| **Medium** | 0.5rem (8px) | Inputs, badges |
| **Large** | 0.75rem (12px) | Cards, containers |
| **XL** | 1rem (16px) | Large cards, sections |
| **Full** | 9999px | Circular/pill shapes |

---

## ♿ Accessibility

### Focus States

All interactive elements have visible focus outlines:
```css
:focus {
    outline: 2px solid var(--color-black);
    outline-offset: 2px;
}
```

### Color Contrast

All text meets WCAG AA standards:
- Black text on white: 21:1 ratio
- White text on black: 21:1 ratio
- Medium gray text on white: 7:1 ratio

### Screen Reader Support

- Semantic HTML elements used throughout
- ARIA labels on icon-only buttons
- `.sr-only` class for screen reader-only text

---

## 📦 Component Library

### Quick Reference

```html
<!-- Buttons -->
<button class="btn-primary">Primary</button>
<button class="btn-secondary">Secondary</button>
<button class="btn-outline">Outline</button>

<!-- Cards -->
<div class="card">Standard Card</div>
<div class="card-brutal">Brutal Card</div>
<div class="stat-card">Stat Card</div>

<!-- Forms -->
<input type="text" class="form-input">
<select class="form-select"></select>
<textarea class="form-textarea"></textarea>

<!-- Badges -->
<span class="badge badge-active">Active</span>
<span class="badge badge-approved">Approved</span>

<!-- Tables -->
<div class="table-container">
    <table class="table"></table>
</div>

<!-- Alerts -->
<div class="alert alert-success">Success!</div>
<div class="alert alert-error">Error!</div>
```

---

## 🎨 Design Principles

### 1. Minimalism
- Focus on essential elements only
- Remove unnecessary decoration
- Use whitespace generously

### 2. Hierarchy
- Clear visual hierarchy through size, weight, and color
- Most important elements are largest and boldest
- Consistent spacing creates rhythm

### 3. Consistency
- Same patterns used across all pages
- Consistent spacing and sizing
- Predictable interactions

### 4. Performance
- Smooth, subtle animations
- Fast load times
- Optimized CSS delivery

### 5. Accessibility
- High contrast ratios
- Keyboard navigation support
- Screen reader friendly

---

## 🚀 Implementation Notes

### CSS Architecture

The design system is implemented in a single CSS file (`custom.css`) with:
- CSS Custom Properties (variables) for all design tokens
- Utility classes for common patterns
- Component classes for reusable UI elements
- Responsive utilities using media queries

### File Structure

```
static/
└── css/
    └── custom.css  (Main design system file)

templates/
├── base.html                    (Base template with design system)
├── partials/
│   ├── navbar.html             (Navigation component)
│   ├── messages.html           (Alert messages)
│   └── pagination.html         (Pagination component)
└── [other templates]           (All use design system classes)
```

### Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid and Flexbox required
- CSS Custom Properties required

---

## 📚 Resources

### Fonts
- [Inter on Google Fonts](https://fonts.google.com/specimen/Inter)

##