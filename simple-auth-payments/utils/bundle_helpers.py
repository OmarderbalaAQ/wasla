"""
Helper functions for bundle management
"""
from pathlib import Path

def get_svg_html(logo_type: str) -> str:
    """Get SVG HTML code for the specified logo type"""
    svg_files = {
        "silver": "static/elements/svgs/silver svg html code.txt",
        "gold": "static/elements/svgs/gold svg html code.txt", 
        "diamond": "static/elements/svgs/diamond-plat svg html code.txt"
    }
    
    file_path = svg_files.get(logo_type, svg_files["silver"])
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fallback SVG if file not found
        return f'<div class="card-icon-wrapper"><span style="font-size: 3em;">💎</span></div>'

def get_predefined_description(desc_type: str) -> str:
    """Get predefined description HTML for the specified type"""
    desc_files = {
        "basic-silver": "static/elements/svgs/descriptions/basic-silver.txt",
        "upper-gold": "static/elements/svgs/descriptions/upper-gold.txt",
        "advanced-diamond": "static/elements/svgs/descriptions/advanced-diamond.txt"
    }
    
    file_path = desc_files.get(desc_type)
    if not file_path:
        return ""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Add opening <ul> tag if not present
            if content and not content.startswith('<ul>'):
                content = '<ul>' + content
            return content
    except FileNotFoundError:
        return ""

def get_logo_options():
    """Get available logo options"""
    return [
        {"value": "silver", "label": "Silver Medal"},
        {"value": "gold", "label": "Gold Crown"},
        {"value": "diamond", "label": "Diamond Premium"}
    ]

def get_description_options():
    """Get available predefined description options"""
    return [
        {"value": "basic-silver", "label": "Basic Silver Features"},
        {"value": "upper-gold", "label": "Upper Gold Features"},
        {"value": "advanced-diamond", "label": "Advanced Diamond Features"}
    ]