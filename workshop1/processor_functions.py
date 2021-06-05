def cleanText(text):
    """Function that cleans the text that the Crawler will extract

    :param text: text extracted from the web page by the crawler
    :type text: str
    :return: cleaned text ready to be saved  on the file 
    :rtype: str
    """
    return text.replace('\n', '').replace('\r', '').replace('\t', '').strip()

def clean_posting_date(text):
    """Function that cleans the text of the attribute posting_date
    that the Crawler will extract

    :param text: text that belongs to the posting_date attribute of the job_posting
    :type text: str
    :return: cleaned text ready to be saved  on the file
    :rtype: str
    """
    return text.replace('by', '').strip()

def clean_id(text):
    """Function that cleans the ids of the job postings and also parse it to
    an integer value

    :param text: text corresponding to the id of the job_posting
    :type text: str
    :return: Number of reference corresponding to the id of the job_posting
    :rtype: int
    """
    return int(text.strip("Reference: "))