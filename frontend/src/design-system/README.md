# Charney Companies Design System

This directory contains the design system implementation for the Charney Companies brand.

## Files Structure

```
frontend/src/design-system/
├── charney-design-system.html    # Complete design system reference
├── charney-variables.css          # CSS variables and base styles
├── CharneyComponents.jsx          # React component library
└── README.md                      # This file
```

## Usage

### 1. CSS Variables
The design system variables are automatically imported in `index.css`. You can use them in your CSS:

```css
.my-element {
  background: var(--charney-red);
  color: var(--charney-black);
  padding: var(--spacing-md);
}
```

### 2. Tailwind Classes
Updated Tailwind config includes Charney-specific utilities:

```jsx
<div className="bg-charney-red text-charney-black">
  <h1 className="text-charney-red font-franklin">
    THE ART OF <span className="text-charney-red">ADMINISTRATION</span>
  </h1>
</div>
```

### 3. React Components
Import and use pre-built components:

```jsx
import { 
  DisplayLG, 
  Button, 
  Card, 
  CardContent, 
  AccentBar,
  MixedColorText 
} from './design-system/CharneyComponents';

function MyComponent() {
  return (
    <Card>
      <CardContent>
        <DisplayLG>
          <MixedColorText 
            blackText="THE ART OF" 
            redText="ADMINISTRATION" 
          />
        </DisplayLG>
        <AccentBar />
        <Button variant="primary">Learn More</Button>
      </CardContent>
    </Card>
  );
}
```

## Key Design Principles

### 1. Typography-Driven
- Use Franklin Gothic exclusively
- Rely on scale, weight, and case for hierarchy
- Mix black and red text in headlines for signature treatment

### 2. Color Usage
- **Charney Red (#FF5959)**: Primary brand color, use sparingly for impact
- **Black (#000000)**: Primary text and UI elements
- **Cream (#F6F1EB)**: Background color
- **White (#FFFFFF)**: Content areas and cards

### 3. CRITICAL: Red Background Rule
When using red backgrounds, text MUST be black (#000000). This is enforced in the `RedSection` component.

```jsx
// ✅ Correct
<RedSection>
  <h1 style={{color: '#000000'}}>Black text on red</h1>
</RedSection>

// ❌ Wrong
<div className="bg-charney-red text-white">
  White text on red background
</div>
```

## Component Reference

### Typography
- `DisplayXL` - 72px, black, uppercase, tight tracking
- `DisplayLG` - 56px, black, uppercase, tight tracking  
- `DisplayMD` - 42px, black, uppercase, tight tracking
- `HeadingLG` - 32px, bold, uppercase
- `HeadingMD` - 24px, bold
- `BodyLG` - 18px, regular, relaxed leading
- `BodyMD` - 16px, regular, relaxed leading

### Buttons
- `variant="primary"` - Red background, white text
- `variant="secondary"` - Black background, white text
- `variant="outline"` - Transparent with black border

### Layout
- `Container` - Max-width container with proper padding
- `Card` - White background with subtle shadow
- `CardContent` - Proper content padding
- `AccentBar` - 6px red divider bar
- `RedSection` - Red background with enforced black text

## Spacing System
- `xs`: 8px
- `sm`: 16px  
- `md`: 24px
- `lg`: 40px
- `xl`: 60px
- `2xl`: 80px

Use with Tailwind: `p-md`, `m-lg`, `gap-xl`, etc.

## Examples

### Mixed Color Headlines (Signature Pattern)
```jsx
<DisplayLG>
  WHY YOU SHOULD <span className="text-charney-red">CHOOSE US</span>
</DisplayLG>

// Or using the helper component
<DisplayLG>
  <MixedColorText blackText="WHY YOU SHOULD" redText="CHOOSE US" />
</DisplayLG>
```

### Cards with Accent Bars
```jsx
<Card>
  <CardContent>
    <HeadingMD>Property Management</HeadingMD>
    <AccentBar />
    <BodyMD>We see shared spaces as a creative canvas.</BodyMD>
    <Button variant="primary">Learn More</Button>
  </CardContent>
</Card>
```

### Red Background Sections
```jsx
<RedSection className="p-xl">
  <DisplayMD>UNDER OUR MANAGEMENT</DisplayMD>
  <AccentBar color="black" />
  <BodyLG>We see shared spaces as a creative canvas.</BodyLG>
</RedSection>
```

## Development Guidelines

### Do's ✅
- Use uppercase typography for headers and CTAs
- Mix black and red in headlines for signature treatment
- Use red backgrounds with black text only
- Let typography create hierarchy through scale and weight
- Use Charney Red sparingly for maximum impact
- Embrace white space and simplicity
- Stick to the spacing system

### Don'ts ❌
- Don't use additional typefaces beyond Franklin Gothic
- Don't use colored text on red backgrounds (always black)
- Don't overuse red - maintain its power as an accent
- Don't add unnecessary decorative elements
- Don't use gradients or complex effects
- Don't use lowercase for major headlines
