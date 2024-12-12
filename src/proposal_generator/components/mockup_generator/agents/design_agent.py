"""Design agent for mockup generation."""
import logging
from typing import Dict, Any, List
from ..models.mockup_model import (
    MockupRequest,
    DesignElements,
    ColorScheme,
    Typography,
    DeviceType
)

logger = logging.getLogger(__name__)

class DesignAgent:
    """Agent responsible for generating mockup design elements."""

    def generate_design(self, request: MockupRequest, device_type: DeviceType) -> DesignElements:
        """Generate design elements for a specific device type."""
        try:
            # Generate color scheme
            colors = self._generate_color_scheme(request.branding)
            
            # Generate typography
            typography = self._generate_typography(request.style_preferences, device_type)
            
            # Generate spacing rules
            spacing = self._generate_spacing(device_type)
            
            # Generate shadows
            shadows = self._generate_shadows()
            
            # Generate borders
            borders = self._generate_borders()
            
            # Generate animations
            animations = self._generate_animations(device_type)
            
            # Generate icons
            icons = self._generate_icons(request.style_preferences)
            
            return DesignElements(
                colors=colors,
                typography=typography,
                spacing=spacing,
                shadows=shadows,
                borders=borders,
                animations=animations,
                icons=icons
            )
            
        except Exception as e:
            logger.error(f"Error generating design elements: {str(e)}")
            return self._create_default_design()

    def _generate_color_scheme(self, branding: Dict[str, Any]) -> ColorScheme:
        """Generate color scheme based on branding."""
        primary = branding.get('primary_color', '#007bff')
        secondary = branding.get('secondary_color', '#6c757d')
        
        return ColorScheme(
            primary=primary,
            secondary=secondary,
            accent=self._generate_accent_color(primary),
            background='#ffffff',
            text='#212529',
            links=primary
        )

    def _generate_typography(self, preferences: Dict[str, Any], device_type: DeviceType) -> Typography:
        """Generate typography settings."""
        base_size = 16 if device_type == DeviceType.DESKTOP else 14
        
        return Typography(
            headings={
                'h1': {
                    'font-family': preferences.get('heading_font', 'Arial'),
                    'font-size': f"{base_size * 2.5}px",
                    'font-weight': '700',
                    'line-height': '1.2'
                },
                'h2': {
                    'font-family': preferences.get('heading_font', 'Arial'),
                    'font-size': f"{base_size * 2}px",
                    'font-weight': '600',
                    'line-height': '1.3'
                },
                'h3': {
                    'font-family': preferences.get('heading_font', 'Arial'),
                    'font-size': f"{base_size * 1.75}px",
                    'font-weight': '600',
                    'line-height': '1.4'
                }
            },
            body={
                'font-family': preferences.get('body_font', 'Arial'),
                'font-size': f"{base_size}px",
                'line-height': '1.5',
                'font-weight': '400'
            },
            special={
                'font-family': preferences.get('special_font', 'Arial'),
                'font-size': f"{base_size * 1.25}px",
                'line-height': '1.4',
                'font-weight': '500'
            },
            font_pairs=[
                ('Arial', 'Helvetica'),
                ('Georgia', 'Times New Roman'),
                ('Roboto', 'Open Sans')
            ]
        )

    def _generate_spacing(self, device_type: DeviceType) -> Dict[str, str]:
        """Generate spacing rules."""
        base = '1rem'
        return {
            'xs': '0.25rem',
            'sm': '0.5rem',
            'md': '1rem',
            'lg': '1.5rem',
            'xl': '2rem',
            'xxl': '3rem'
        }

    def _generate_shadows(self) -> Dict[str, str]:
        """Generate shadow styles."""
        return {
            'sm': '0 1px 2px rgba(0,0,0,0.05)',
            'md': '0 4px 6px rgba(0,0,0,0.1)',
            'lg': '0 10px 15px rgba(0,0,0,0.1)',
            'xl': '0 20px 25px rgba(0,0,0,0.1)',
            'inner': 'inset 0 2px 4px rgba(0,0,0,0.05)'
        }

    def _generate_borders(self) -> Dict[str, str]:
        """Generate border styles."""
        return {
            'thin': '1px solid',
            'medium': '2px solid',
            'thick': '4px solid',
            'rounded-sm': '0.25rem',
            'rounded': '0.5rem',
            'rounded-lg': '1rem',
            'circle': '50%'
        }

    def _generate_animations(self, device_type: DeviceType) -> Dict[str, Any]:
        """Generate animation settings."""
        return {
            'transition': {
                'fast': '0.15s ease-in-out',
                'medium': '0.3s ease-in-out',
                'slow': '0.5s ease-in-out'
            },
            'hover': {
                'scale': 'transform: scale(1.05)',
                'lift': 'transform: translateY(-2px)',
                'glow': 'box-shadow: 0 0 8px rgba(0,0,0,0.2)'
            },
            'loading': {
                'spinner': 'rotate 1s linear infinite',
                'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
            }
        }

    def _generate_icons(self, preferences: Dict[str, Any]) -> Dict[str, str]:
        """Generate icon settings."""
        icon_set = preferences.get('icon_set', 'material')
        return {
            'menu': f'{icon_set}-menu',
            'close': f'{icon_set}-close',
            'search': f'{icon_set}-search',
            'user': f'{icon_set}-user',
            'cart': f'{icon_set}-cart',
            'arrow-right': f'{icon_set}-arrow-right',
            'arrow-left': f'{icon_set}-arrow-left',
            'social-facebook': f'{icon_set}-facebook',
            'social-twitter': f'{icon_set}-twitter',
            'social-instagram': f'{icon_set}-instagram'
        }

    def _generate_accent_color(self, primary_color: str) -> str:
        """Generate an accent color based on primary color."""
        # Simple implementation - in reality, would use color theory
        return primary_color[:-6] + 'ff9900'  # Example: changes last 6 chars to orange

    def _create_default_design(self) -> DesignElements:
        """Create default design elements in case of errors."""
        return DesignElements(
            colors=ColorScheme(
                primary='#007bff',
                secondary='#6c757d',
                accent='#ff9900',
                background='#ffffff',
                text='#212529',
                links='#007bff'
            ),
            typography=Typography(
                headings={
                    'h1': {'font-family': 'Arial', 'font-size': '2.5rem'},
                    'h2': {'font-family': 'Arial', 'font-size': '2rem'},
                    'h3': {'font-family': 'Arial', 'font-size': '1.75rem'}
                },
                body={'font-family': 'Arial', 'font-size': '1rem'},
                special={'font-family': 'Arial', 'font-size': '1.25rem'},
                font_pairs=[('Arial', 'Helvetica')]
            ),
            spacing={
                'base': '1rem',
                'large': '2rem',
                'small': '0.5rem'
            },
            shadows={
                'default': '0 2px 4px rgba(0,0,0,0.1)'
            },
            borders={
                'default': '1px solid #dee2e6'
            },
            animations={
                'transition': {'default': '0.3s ease-in-out'}
            },
            icons={
                'menu': 'default-menu',
                'close': 'default-close'
            }
        ) 