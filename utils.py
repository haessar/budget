from datetime import datetime

def tokenizer(description):
    return [str(x.strip()) for x in description.split(',')]

def remove_apostrophe(str):
    if str.startswith("'"):
        return str[1:]
    else:
        return str

def format_header(item):
    return item.strip().lower().replace(' ', '_')

def format_datetime(item):
    try:
        return datetime.strptime(item, '%d/%m/%Y').date()
    except ValueError:
        try:
            return datetime.strptime(item, '%d %b %Y').date()
        except ValueError:
            raise ValueError('Unrecognised date format.')

def format_category(category):
    return category.lower().replace(' ', '_')

def reverse_format_category(category):
    return category.replace('_', ' ').title()
