"""
GUI Styling Configuration
"""

import customtkinter as ctk

# Color themes
COLORS = {
    'primary': '#2B5CE6',
    'primary_dark': '#1E3A8A',
    'secondary': '#10B981',
    'accent': '#F59E0B',
    'danger': '#EF4444',
    'warning': '#F59E0B',
    'success': '#10B981',
    'info': '#3B82F6',
    'light': '#F8FAFC',
    'dark': '#1E293B',
    'gray': '#6B7280',
    'white': '#FFFFFF'
}

# Font configurations
FONTS = {
    'heading_large': ('Arial', 24, 'bold'),
    'heading': ('Arial', 18, 'bold'),
    'subheading': ('Arial', 14, 'bold'),
    'body': ('Arial', 12),
    'body_small': ('Arial', 10),
    'code': ('Consolas', 11),
    'button': ('Arial', 12, 'bold')
}

# Widget styling
WIDGET_STYLES = {
    'button_primary': {
        'fg_color': COLORS['primary'],
        'hover_color': COLORS['primary_dark'],
        'text_color': COLORS['white'],
        'font': FONTS['button'],
        'corner_radius': 8,
        'height': 40
    },
    'button_secondary': {
        'fg_color': COLORS['gray'],
        'hover_color': COLORS['dark'],
        'text_color': COLORS['white'],
        'font': FONTS['button'],
        'corner_radius': 8,
        'height': 40
    },
    'button_success': {
        'fg_color': COLORS['success'],
        'hover_color': '#059669',
        'text_color': COLORS['white'],
        'font': FONTS['button'],
        'corner_radius': 8,
        'height': 40
    },
    'button_danger': {
        'fg_color': COLORS['danger'],
        'hover_color': '#DC2626',
        'text_color': COLORS['white'],
        'font': FONTS['button'],
        'corner_radius': 8,
        'height': 40
    },
    'entry': {
        'font': FONTS['body'],
        'height': 35,
        'corner_radius': 6,
        'border_width': 1
    },
    'label_heading': {
        'font': FONTS['heading'],
        'text_color': COLORS['dark']
    },
    'label_subheading': {
        'font': FONTS['subheading'],
        'text_color': COLORS['gray']
    },
    'label_body': {
        'font': FONTS['body'],
        'text_color': COLORS['dark']
    },
    'frame': {
        'corner_radius': 10,
        'border_width': 1,
        'border_color': COLORS['gray']
    },
    'scrollable_frame': {
        'corner_radius': 10,
        'scrollbar_button_color': COLORS['primary'],
        'scrollbar_button_hover_color': COLORS['primary_dark']
    }
}

# Layout constants
LAYOUT = {
    'padding': {
        'small': 5,
        'medium': 10,
        'large': 20,
        'xlarge': 30
    },
    'spacing': {
        'small': 5,
        'medium': 10,
        'large': 15,
        'xlarge': 20
    },
    'window': {
        'min_width': 1200,
        'min_height': 800,
        'default_width': 1400,
        'default_height': 900
    },
    'sidebar_width': 250,
    'toolbar_height': 60
}

def apply_button_style(button: ctk.CTkButton, style: str = 'primary'):
    """Apply predefined style to button"""
    if style in WIDGET_STYLES:
        style_dict = WIDGET_STYLES[f'button_{style}']
        button.configure(**style_dict)

def apply_label_style(label: ctk.CTkLabel, style: str = 'body'):
    """Apply predefined style to label"""
    style_key = f'label_{style}'
    if style_key in WIDGET_STYLES:
        label.configure(**WIDGET_STYLES[style_key])

def create_styled_frame(parent, **kwargs) -> ctk.CTkFrame:
    """Create a styled frame with default styling"""
    frame_style = WIDGET_STYLES['frame'].copy()
    frame_style.update(kwargs)
    return ctk.CTkFrame(parent, **frame_style)

def create_styled_scrollable_frame(parent, **kwargs) -> ctk.CTkScrollableFrame:
    """Create a styled scrollable frame"""
    frame_style = WIDGET_STYLES['scrollable_frame'].copy()
    frame_style.update(kwargs)
    return ctk.CTkScrollableFrame(parent, **frame_style)