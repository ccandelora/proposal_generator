"""Color utility functions for SEO Screenshotter."""

import re
from typing import Optional, Tuple, Dict, Any

def normalize_color(color: str) -> Optional[str]:
    """Convert various color formats to normalized hex format."""
    # Remove whitespace
    color = color.strip().lower()
    
    # Already hex format
    if re.match(r'^#[0-9a-f]{6}$', color):
        return color
        
    # Short hex format
    if re.match(r'^#[0-9a-f]{3}$', color):
        return f"#{color[1]*2}{color[2]*2}{color[3]*2}"
        
    # RGB format
    rgb_match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color)
    if rgb_match:
        r, g, b = map(int, rgb_match.groups())
        return f"#{r:02x}{g:02x}{b:02x}"
        
    # RGBA format (ignore alpha)
    rgba_match = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*[\d.]+\)', color)
    if rgba_match:
        r, g, b = map(int, rgba_match.groups())
        return f"#{r:02x}{g:02x}{b:02x}"
        
    # Named colors
    color_map = {
        'black': '#000000',
        'white': '#ffffff',
        'red': '#ff0000',
        'green': '#00ff00',
        'blue': '#0000ff',
        'yellow': '#ffff00',
        'purple': '#800080',
        'gray': '#808080',
        'grey': '#808080',
        'silver': '#c0c0c0',
        'maroon': '#800000',
        'olive': '#808000',
        'navy': '#000080',
        'aqua': '#00ffff',
        'teal': '#008080',
        'fuchsia': '#ff00ff',
        'lime': '#00ff00'
    }
    return color_map.get(color)

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSL color space."""
    r, g, b = r/255.0, g/255.0, b/255.0
    
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin
    
    # Calculate hue
    if delta == 0:
        h = 0
    elif cmax == r:
        h = 60 * (((g-b)/delta) % 6)
    elif cmax == g:
        h = 60 * (((b-r)/delta) + 2)
    else:
        h = 60 * (((r-g)/delta) + 4)
        
    # Calculate lightness
    l = (cmax + cmin) / 2
    
    # Calculate saturation
    s = 0 if delta == 0 else delta / (1 - abs(2*l - 1))
    
    return h, s*100, l*100

def hex_to_hsl(hex_color: str) -> Dict[str, float]:
    """Convert hex color to HSL color space."""
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(*rgb)
    return {
        "hue": round(h, 2),
        "saturation": round(s, 2),
        "lightness": round(l, 2)
    }

def get_color_category(hsl: Dict[str, float]) -> str:
    """Categorize color based on HSL values."""
    h, s, l = hsl["hue"], hsl["saturation"], hsl["lightness"]
    
    # Check for grayscale
    if s < 10:
        if l < 20:
            return "black"
        elif l > 80:
            return "white"
        else:
            return "gray"
            
    # Determine hue category
    hue_categories = {
        (0, 30): "red",
        (31, 60): "orange",
        (61, 120): "yellow",
        (121, 180): "green",
        (181, 240): "blue",
        (241, 300): "purple",
        (301, 360): "red"
    }
    
    for (start, end), category in hue_categories.items():
        if start <= h <= end:
            # Add intensity modifier
            if l < 30:
                return f"dark_{category}"
            elif l > 70:
                return f"light_{category}"
            else:
                return category
                
    return "undefined"

def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    def get_luminance(hex_color: str) -> float:
        r, g, b = hex_to_rgb(hex_color)
        # Convert to sRGB
        rs = r/255.0
        gs = g/255.0
        bs = b/255.0
        
        # Convert to linear RGB
        rs = rs/12.92 if rs <= 0.03928 else ((rs+0.055)/1.055)**2.4
        gs = gs/12.92 if gs <= 0.03928 else ((gs+0.055)/1.055)**2.4
        bs = bs/12.92 if bs <= 0.03928 else ((bs+0.055)/1.055)**2.4
        
        # Calculate luminance
        return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
        
    l1 = get_luminance(color1)
    l2 = get_luminance(color2)
    
    # Calculate contrast ratio
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def analyze_color_harmony(colors: list[str]) -> Dict[str, Any]:
    """Analyze color harmony between multiple colors."""
    if len(colors) < 2:
        return {"harmony_type": "monochromatic", "score": 1.0}
        
    hsl_colors = [hex_to_hsl(c) for c in colors]
    hues = [c["hue"] for c in hsl_colors]
    
    # Calculate hue differences
    hue_diffs = []
    for i in range(len(hues)):
        for j in range(i+1, len(hues)):
            diff = abs(hues[i] - hues[j])
            if diff > 180:
                diff = 360 - diff
            hue_diffs.append(diff)
            
    avg_diff = sum(hue_diffs) / len(hue_diffs)
    
    # Determine harmony type
    harmony_types = {
        (0, 20): "monochromatic",
        (21, 50): "analogous",
        (80, 100): "complementary",
        (110, 130): "triadic",
        (150, 180): "split-complementary"
    }
    
    harmony_type = "discordant"
    for (min_diff, max_diff), h_type in harmony_types.items():
        if min_diff <= avg_diff <= max_diff:
            harmony_type = h_type
            break
            
    # Calculate harmony score
    harmony_scores = {
        "monochromatic": 0.8,
        "analogous": 0.9,
        "complementary": 1.0,
        "triadic": 0.9,
        "split-complementary": 0.85,
        "discordant": 0.5
    }
    
    return {
        "harmony_type": harmony_type,
        "score": harmony_scores[harmony_type],
        "average_hue_difference": avg_diff
    } 