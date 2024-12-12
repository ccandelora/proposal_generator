"""HTML generation utilities."""
from typing import Dict, Any, List
from ..models.mockup_model import (
    ContentElements,
    ContentElement,
    ElementType,
    DeviceType
)

class HTMLGenerator:
    """Utility class for generating HTML code."""

    @staticmethod
    def generate_html(content: ContentElements, device_type: DeviceType) -> str:
        """Generate HTML code from content elements."""
        doctype = '<!DOCTYPE html>\n'
        html_start = '<html lang="en">\n'
        head = HTMLGenerator._generate_head()
        body = HTMLGenerator._generate_body(content, device_type)
        html_end = '</html>'
        
        return f"{doctype}{html_start}{head}{body}{html_end}"

    @staticmethod
    def _generate_head() -> str:
        """Generate HTML head section."""
        return """<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Mockup</title>
    <link rel="stylesheet" href="styles.css">
</head>\n"""

    @staticmethod
    def _generate_body(content: ContentElements, device_type: DeviceType) -> str:
        """Generate HTML body section."""
        device_class = f"device-{device_type.value}"
        body = f'<body class="{device_class}">\n'
        
        # Header
        body += '    <header>\n'
        body += HTMLGenerator._generate_elements(content.header)
        body += '    </header>\n'
        
        # Navigation
        body += '    <nav>\n'
        body += HTMLGenerator._generate_elements(content.navigation)
        body += '    </nav>\n'
        
        # Hero
        if content.hero:
            body += '    <section class="hero">\n'
            body += HTMLGenerator._generate_elements(content.hero)
            body += '    </section>\n'
        
        # Main content
        body += '    <main>\n'
        body += HTMLGenerator._generate_elements(content.main)
        body += '    </main>\n'
        
        # Footer
        body += '    <footer>\n'
        body += HTMLGenerator._generate_elements(content.footer)
        body += '    </footer>\n'
        
        body += '</body>\n'
        return body

    @staticmethod
    def _generate_elements(elements: List[ContentElement]) -> str:
        """Generate HTML for content elements."""
        html = ''
        for element in elements:
            html += HTMLGenerator._generate_element(element)
        return html

    @staticmethod
    def _generate_element(element: ContentElement) -> str:
        """Generate HTML for a single content element."""
        element_type = element.type.lower()
        content = element.content
        style_class = f'class="{element_type}"' if element_type else ''
        
        # Generate element-specific attributes
        attributes = HTMLGenerator._generate_attributes(element)
        
        if element_type == 'image':
            return f'        <img src="{content["src"]}" alt="{content.get("alt", "")}" {style_class} {attributes}/>\n'
        
        elif element_type == 'button':
            return f'        <button {style_class} {attributes}>{content["text"]}</button>\n'
        
        elif element_type == 'link':
            return f'        <a href="{content["href"]}" {style_class} {attributes}>{content["text"]}</a>\n'
        
        elif element_type == 'heading':
            level = content.get('level', 2)
            return f'        <h{level} {style_class} {attributes}>{content["text"]}</h{level}>\n'
        
        elif element_type == 'paragraph':
            return f'        <p {style_class} {attributes}>{content["text"]}</p>\n'
        
        elif element_type == 'list':
            list_type = content.get('type', 'ul')
            items = content.get('items', [])
            list_html = f'        <{list_type} {style_class} {attributes}>\n'
            for item in items:
                list_html += f'            <li>{item}</li>\n'
            list_html += f'        </{list_type}>\n'
            return list_html
        
        elif element_type == 'form':
            form_html = f'        <form {style_class} {attributes}>\n'
            for field in content.get('fields', []):
                form_html += HTMLGenerator._generate_form_field(field)
            form_html += '        </form>\n'
            return form_html
        
        elif element_type == 'container' or element_type == 'section':
            container_html = f'        <div {style_class} {attributes}>\n'
            for child in content.get('children', []):
                container_html += HTMLGenerator._generate_element(child)
            container_html += '        </div>\n'
            return container_html
        
        else:
            # Default to div for unknown types
            return f'        <div {style_class} {attributes}>{str(content)}</div>\n'

    @staticmethod
    def _generate_attributes(element: ContentElement) -> str:
        """Generate HTML attributes for an element."""
        attributes = []
        
        # Add ID if present
        if 'id' in element.content:
            attributes.append(f'id="{element.content["id"]}"')
        
        # Add data attributes
        for key, value in element.content.get('data', {}).items():
            attributes.append(f'data-{key}="{value}"')
        
        # Add ARIA attributes for accessibility
        for key, value in element.content.get('aria', {}).items():
            attributes.append(f'aria-{key}="{value}"')
        
        # Add role if present
        if 'role' in element.content:
            attributes.append(f'role="{element.content["role"]}"')
        
        # Add custom attributes
        for key, value in element.content.get('attributes', {}).items():
            attributes.append(f'{key}="{value}"')
        
        return ' '.join(attributes)

    @staticmethod
    def _generate_form_field(field: Dict[str, Any]) -> str:
        """Generate HTML for a form field."""
        field_type = field.get('type', 'text')
        label = field.get('label', '')
        name = field.get('name', '')
        required = 'required' if field.get('required', False) else ''
        placeholder = field.get('placeholder', '')
        
        if field_type == 'textarea':
            return f"""            <div class="form-field">
                <label for="{name}">{label}</label>
                <textarea name="{name}" id="{name}" placeholder="{placeholder}" {required}></textarea>
            </div>\n"""
        
        elif field_type == 'select':
            options = field.get('options', [])
            options_html = '\n'.join(
                f'                <option value="{opt["value"]}">{opt["label"]}</option>'
                for opt in options
            )
            return f"""            <div class="form-field">
                <label for="{name}">{label}</label>
                <select name="{name}" id="{name}" {required}>
{options_html}
                </select>
            </div>\n"""
        
        else:
            return f"""            <div class="form-field">
                <label for="{name}">{label}</label>
                <input type="{field_type}" name="{name}" id="{name}" placeholder="{placeholder}" {required}>
            </div>\n""" 