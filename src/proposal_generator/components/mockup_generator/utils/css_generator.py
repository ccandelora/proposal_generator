"""CSS generation utilities."""
from typing import Dict, Any
from ..models.mockup_model import (
    DesignElements,
    ColorScheme,
    Typography,
    DeviceType
)

class CSSGenerator:
    """Utility class for generating CSS code."""

    @staticmethod
    def generate_css(design: DesignElements, device_type: DeviceType) -> str:
        """Generate CSS code from design elements."""
        css = []
        
        # Add CSS reset
        css.append(CSSGenerator._generate_reset())
        
        # Add root variables
        css.append(CSSGenerator._generate_variables(design.colors))
        
        # Add base styles
        css.append(CSSGenerator._generate_base_styles(design))
        
        # Add typography styles
        css.append(CSSGenerator._generate_typography_styles(design.typography))
        
        # Add layout styles
        css.append(CSSGenerator._generate_layout_styles(design.spacing))
        
        # Add component styles
        css.append(CSSGenerator._generate_component_styles(design))
        
        # Add responsive styles
        css.append(CSSGenerator._generate_responsive_styles(device_type))
        
        # Add utility classes
        css.append(CSSGenerator._generate_utility_classes())
        
        # Add animations
        css.append(CSSGenerator._generate_animations(design.animations))
        
        return '\n\n'.join(css)

    @staticmethod
    def _generate_reset() -> str:
        """Generate CSS reset."""
        return """/* Reset styles */
*, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    font-size: 16px;
    line-height: 1.5;
    -webkit-text-size-adjust: 100%;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

body {
    min-height: 100vh;
    scroll-behavior: smooth;
    text-rendering: optimizeSpeed;
}

img, picture, video, canvas, svg {
    display: block;
    max-width: 100%;
}

input, button, textarea, select {
    font: inherit;
}"""

    @staticmethod
    def _generate_variables(colors: ColorScheme) -> str:
        """Generate CSS variables."""
        return f"""/* CSS Variables */
:root {{
    /* Colors */
    --color-primary: {colors.primary};
    --color-secondary: {colors.secondary};
    --color-accent: {colors.accent};
    --color-background: {colors.background};
    --color-text: {colors.text};
    --color-links: {colors.links};
    
    /* Spacing */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 2rem;
    --space-xl: 4rem;
    
    /* Border radius */
    --radius-sm: 0.25rem;
    --radius-md: 0.5rem;
    --radius-lg: 1rem;
    
    /* Transitions */
    --transition-fast: 150ms ease-in-out;
    --transition-normal: 300ms ease-in-out;
    --transition-slow: 500ms ease-in-out;
}}"""

    @staticmethod
    def _generate_base_styles(design: DesignElements) -> str:
        """Generate base styles."""
        return f"""/* Base styles */
body {{
    background-color: var(--color-background);
    color: var(--color-text);
    font-family: {design.typography.body.get('font-family', 'system-ui')};
}}

a {{
    color: var(--color-links);
    text-decoration: none;
    transition: var(--transition-fast);
}}

a:hover {{
    text-decoration: underline;
}}

button {{
    cursor: pointer;
    border: none;
    background-color: var(--color-primary);
    color: white;
    padding: var(--space-sm) var(--space-md);
    border-radius: var(--radius-sm);
    transition: var(--transition-fast);
}}

button:hover {{
    filter: brightness(1.1);
}}

img {{
    border-radius: var(--radius-sm);
    {design.shadows.get('default', '')}
}}"""

    @staticmethod
    def _generate_typography_styles(typography: Typography) -> str:
        """Generate typography styles."""
        styles = ["/* Typography */"]
        
        # Headings
        for level, props in typography.headings.items():
            font_size = props.get('font-size', '1rem')
            font_weight = props.get('font-weight', '700')
            line_height = props.get('line-height', '1.2')
            styles.append(f"""
{level} {{
    font-size: {font_size};
    font-weight: {font_weight};
    line-height: {line_height};
    margin-bottom: var(--space-md);
}}""")
        
        # Body text
        styles.append(f"""
p {{
    font-size: {typography.body.get('font-size', '1rem')};
    line-height: {typography.body.get('line-height', '1.5')};
    margin-bottom: var(--space-md);
}}""")
        
        return '\n'.join(styles)

    @staticmethod
    def _generate_layout_styles(spacing: Dict[str, str]) -> str:
        """Generate layout styles."""
        return f"""/* Layout */
.container {{
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-md);
}}

header {{
    padding: var(--space-md) 0;
    background-color: var(--color-background);
    border-bottom: 1px solid rgba(0,0,0,0.1);
}}

nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.hero {{
    padding: var(--space-xl) 0;
    background-color: var(--color-primary);
    color: white;
    text-align: center;
}}

main {{
    padding: var(--space-xl) 0;
}}

footer {{
    padding: var(--space-lg) 0;
    background-color: var(--color-secondary);
    color: white;
}}

.grid {{
    display: grid;
    gap: {spacing.get('gap', 'var(--space-md)')};
    grid-template-columns: repeat(12, 1fr);
}}"""

    @staticmethod
    def _generate_component_styles(design: DesignElements) -> str:
        """Generate component styles."""
        return f"""/* Components */
.card {{
    background-color: white;
    border-radius: var(--radius-md);
    padding: var(--space-md);
    {design.shadows.get('default', '')}
}}

.form-field {{
    margin-bottom: var(--space-md);
}}

.form-field label {{
    display: block;
    margin-bottom: var(--space-xs);
    font-weight: 500;
}}

.form-field input,
.form-field textarea,
.form-field select {{
    width: 100%;
    padding: var(--space-sm);
    border: 1px solid rgba(0,0,0,0.2);
    border-radius: var(--radius-sm);
}}

.form-field input:focus,
.form-field textarea:focus,
.form-field select:focus {{
    outline: none;
    border-color: var(--color-primary);
}}

.button {{
    display: inline-block;
    padding: var(--space-sm) var(--space-md);
    background-color: var(--color-primary);
    color: white;
    border-radius: var(--radius-sm);
    text-decoration: none;
    transition: var(--transition-fast);
}}

.button:hover {{
    filter: brightness(1.1);
}}

.icon {{
    width: 24px;
    height: 24px;
}}"""

    @staticmethod
    def _generate_responsive_styles(device_type: DeviceType) -> str:
        """Generate responsive styles."""
        styles = ["/* Responsive styles */"]
        
        if device_type == DeviceType.MOBILE:
            styles.append("""
@media (max-width: 768px) {
    html {
        font-size: 14px;
    }
    
    .grid {
        grid-template-columns: 1fr;
    }
    
    nav {
        flex-direction: column;
        gap: var(--space-md);
    }
    
    .hero {
        padding: var(--space-lg) 0;
    }
}""")
        
        elif device_type == DeviceType.TABLET:
            styles.append("""
@media (max-width: 1024px) {
    .grid {
        grid-template-columns: repeat(6, 1fr);
    }
}""")
        
        return '\n'.join(styles)

    @staticmethod
    def _generate_utility_classes() -> str:
        """Generate utility classes."""
        return """/* Utility classes */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mt-1 { margin-top: var(--space-sm); }
.mt-2 { margin-top: var(--space-md); }
.mt-3 { margin-top: var(--space-lg); }
.mt-4 { margin-top: var(--space-xl); }

.mb-1 { margin-bottom: var(--space-sm); }
.mb-2 { margin-bottom: var(--space-md); }
.mb-3 { margin-bottom: var(--space-lg); }
.mb-4 { margin-bottom: var(--space-xl); }

.hidden { display: none; }
.visible { display: block; }

.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.gap-1 { gap: var(--space-sm); }
.gap-2 { gap: var(--space-md); }
.gap-3 { gap: var(--space-lg); }"""

    @staticmethod
    def _generate_animations(animations: Dict[str, Any]) -> str:
        """Generate CSS animations."""
        return """/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideIn {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

@keyframes scaleIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

.animate-fade-in {
    animation: fadeIn var(--transition-normal);
}

.animate-slide-in {
    animation: slideIn var(--transition-normal);
}

.animate-scale-in {
    animation: scaleIn var(--transition-normal);
}""" 