def cleanText(text):
    return text.replace('\n', '').replace('\r', '').replace('\t', '').strip()

def clean_posting_date(text):
    return text.replace('by', '').strip()

def clean_id(text):
    return int(text.strip("Reference: "))