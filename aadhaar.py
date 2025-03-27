import re

AADHAAR_REGEX = r'\b\d{4} \d{4} \d{4}\b'

def check_if_aadhaar(results):
    correct_aadhaar_number(results) # Correct the AADHAAR number if misinterpreted
    text = extract_text_from_list(results)
    if re.search(AADHAAR_REGEX, text):
        return True
    return False

def correct_aadhaar_number(results):
    """Extract AADHAAR number from the given image."""
    for idx, (_, text, _) in enumerate(results):
        text = text.strip().upper()  # Standardize text case
        corrected_text = rectify_aadhaar_number(text)

        if re.fullmatch(r'\b\d{4}\b', corrected_text):
            results[idx] = (results[idx][0], corrected_text, results[idx][2])  # Update the OCR results

def rectify_aadhaar_number(aadhaar_text):
    """Fix AADHAAR misinterpretation of 'O' (letter O) instead of '0' (zero)."""
    # Convert all 'O' to '0' and recheck validity
    corrected_number = aadhaar_text.replace("O", "0")

    # If the corrected version matches the PAN pattern, return it
    if re.fullmatch(r'\b\d{4}\b', corrected_number):
        return corrected_number

    return aadhaar_text  # Return original if correction is not valid

def process_aadhaar(results):
    text = extract_text_from_image(results)
    print(f"Text: {text}")
    aadhaar_number = extract_aadhaar_number(text)
    name = extract_name(text, results)
    dob = extract_dob(text, results)
    gender = extract_gender(text, results)
    return {
        "aadhaar_number": aadhaar_number,
        "name": name,
        "dob": dob,
        "gender": gender
    }

def extract_aadhaar_number(text):
    aadhaar_number = re.search(AADHAAR_REGEX, text)
    if aadhaar_number:
        print(f"Aadhaar Number: {aadhaar_number}")
        return aadhaar_number.group(0)
    return None

def extract_name(text, results):
    name_pattern_1 = r'(?i)(?:name)[\s:-]+([A-Za-z ]+)'
    name_pattern_2_1 = r'(?i)(?:Government of India|Govt. of India|GovernmentofIndia|Governmentof India|Government ofIndia|Unique Identification Authority of India)[\s\n]+(?:Government of India|Govt. of India|GovernmentofIndia|Governmentof India|Government ofIndia|Unique Identification Authority of India)?[\s\n]*'
    name_pattern_2_2 = r'^(.*?)(?:\b(?:Address|DOB|Date of Birth|Year of Birth)\b)'
    name_pattern_2_3 = r'^.*?(?<!\S)([A-Za-z]+\s[A-Za-z\s]+)(?!\S).*?$'

    name = re.search(name_pattern_2_2, text, re.DOTALL)
    if name:
        name = re.search(name_pattern_1, name.group(1))
        if name:
            print(f"Name1: {name}")
            return name.group(1).strip()
    end_idx = findLastOccurenceIndex(text, name_pattern_2_1)
    if end_idx != 0:
        name = re.search(name_pattern_2_2, text[end_idx:], re.DOTALL)
        if name:
            name = re.search(name_pattern_2_3, name.group(1))
            if name:
                print(f"Name2: {name}")
                return name.group(1).strip()
    text1 = extract_text_from_list(results)
    end_idx = findLastOccurenceIndex(text1, name_pattern_2_1)
    if end_idx != 0:
        name = re.search(name_pattern_2_2, text1[end_idx:], re.DOTALL)
        if name:
            name = re.search(name_pattern_2_3, name.group(1))
            if name:
                print(f"Name3: {name}")
                return name.group(1).strip()
    return None

def extract_dob(text, results):
    dob_pattern_1 = r'(?i)(?:DOB|Date of Birth)[\s:-]+(\d{2}[-\/]\d{2}[-\/]\d{4})'
    dob_pattern_2 = r'(?i)(?:Year of Birth|YearofBirth)[\s:-]+(\d{4})'
    dob_pattern_3 = r'\b\d{2}[-/]\d{2}[-/]\d{4}\b'

    dob = re.search(dob_pattern_1, text)
    if dob:
        print(f"DOB1: {dob}")
        return dob.group(1)
    dob = re.search(dob_pattern_2, text)
    if dob:
        print(f"DOB2: {dob}")
        return dob.group(1)
    dob = re.search(dob_pattern_3, text)
    if dob:
        print(f"DOB3: {dob}")
        return dob.group(0)
    dob = re.search(dob_pattern_3, extract_text_from_list(results))
    if dob:
        print(f"DOB4: {dob}")
        return dob.group(0)
    return None

def extract_gender(text, results):
    gender_pattern_1 = r'(?i)(?:Gender|Sex)[\s:-]+(?:Male|Female|Transgender)'
    gender_pattern_2 = r'(?i)(?:Male|Female|Transgender)'

    gender = re.search(gender_pattern_1, text)
    if gender:
        print(f"Gender1: {gender}")
        return gender.group(0)
    gender = re.search(gender_pattern_2, text)
    if gender:
        print(f"Gender2: {gender}")
        return gender.group(0)
    gender = re.search(gender_pattern_2, extract_text_from_list(results))
    if gender:
        print(f"Gender3: {gender}")
        return gender.group(0)
    return None

def findLastOccurenceIndex(text1, pattern):
    idx = 0
    match = re.search(pattern, text1)
    if match == None:
        return idx
    nextmatch = match
    idx += match.end()
    while nextmatch != None:    
        text1 = text1[nextmatch.end():]
        nextmatch = re.search(pattern, text1)
        if nextmatch != None:
            match = nextmatch
            idx += nextmatch.end()
    return idx

def extract_text_from_image(results):
    return " ".join([res[1] for res in results if res[2] >= 0.40])

def extract_text_from_list(results):
    return " ".join([res[1] for res in results])