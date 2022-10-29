def format_str(text,
               font_size=16,
               back_color=(16, 28, 44),
               font_color=(55, 139, 216),
               border_color=(55, 139, 216),
               border_width=1,
               line_height=1):
    """
    Format a string to be displayed in a Markdown cell.
    :param text: the string to format
    :param font_size: size of the font
    :param back_color: color of the background
    :param font_color: color of the font
    :param border_color: color of the border
    :param border_width: width of the border
    :param line_height: height of the line
    :return: formatted string
    """
    return f'''<span style="
    font-size:{font_size}px; 
    background: rgb{back_color};
    color: rgb{font_color}; 
    padding: 0.65em 0.65em; 
    margin: 0.5em 0.5em;
    margin-top: 10%; 
    line-height:{line_height};
    border: {border_width}px solid rgb{border_color}; 
    border-radius: 0.35em;
    ">{text}</span>'''
