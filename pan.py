import re
import logging

PAN_REGEX = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'

def check_if_pan(results):
    correct_pan_number(results) # Correct the PAN number if misinterpreted
    text = extract_text_from_list(results)
    if re.search(PAN_REGEX, text):
        return True
    return False

def correct_pan_number(results):
    """Extract PAN number from the given image."""
    for idx, (_, text, _) in enumerate(results):
        text = text.strip().upper()  # Standardize text case
        corrected_text = rectify_pan_number(text)

        if re.fullmatch(PAN_REGEX, corrected_text):
            results[idx] = (results[idx][0], corrected_text, results[idx][2])  # Update the OCR results
            break

def rectify_pan_number(pan_text):
    """Fix PAN misinterpretation of 'O' (letter O) instead of '0' (zero)."""
    prefix_part = pan_text[:5]
    number_part = pan_text[5:9]
    suffix_part = pan_text[9:]

    # Convert all letters to digits in number part
    corrected_number = number_part.replace("O", "0").replace("o", "0").replace("I", "1").replace("l", "1")

    corrected_pan = prefix_part + corrected_number + suffix_part
    # If the corrected version matches the PAN pattern, return it
    if re.fullmatch(PAN_REGEX, corrected_pan):
        return corrected_pan

    return pan_text  # Return original if correction is not valid

def process_pan(results):
    text = extract_text_from_image(results)
    logging.info(f"Text: {text}")
    print(f"Text: {text}")
    pan_number = extract_pan_number(text)
    name = extract_name(text, results)
    dob = extract_dob(text, results)
    father_name = extract_father_name(text, results, name)
    logging.info(f"PAN: {pan_number}" + f" Name: {name}" + f" DOB: {dob}" + f" Father Name: {father_name}")
    return {
        "document_type": "PAN",
        "pan_number": pan_number,
        "name": name,
        "fathers_name": father_name,
        "dob": dob
    }

def extract_pan_number(text):
    pan_number = re.search(PAN_REGEX, text)
    if pan_number:
        print(f"PAN Number: {pan_number}")
        return pan_number.group(0)
    return None

def extract_name(text, results):
    name_pattern_1 = r'(?i)(?:Permanent Account Number Card)'
    name_pattern_2 = r'(?i)(?:Government of India|Govt. of India|Govt of India|GovtofIndia|Govtof India|Govt ofIndia)[\s\n]*'
    name_pattern_3 = r'^.*?(?<!\S)([A-Z]+\s[A-Z\s]+)(?!\S).*?$'
    name_pattern_4 = r'(?i)(?:Name)'
    name_pattern_5 = r'^(.*?)(?:\b(?:Father\'s Name|Father\'sName|Fathers Name|FathersName|Father Name)\b)'

    idx = 0
    for i, (_, text, _) in enumerate(results):
        if re.search(name_pattern_1, text):
            idx = i
            break
    if idx == 0:
        for i, (_, text, _) in enumerate(results):
            if re.search(name_pattern_2, text):
                idx = i
                break
    if idx != 0:
        for (_, text, _) in results[idx+1:]:
            name = re.search(name_pattern_3, text, re.DOTALL)
            if name:
                print(f"Name1: {name}")
                return name.group(1).strip()
    name1 = re.search(name_pattern_4, text)
    if name1:
        name = re.search(name_pattern_5, text[name1.end():], re.DOTALL)
        if name:
            name = re.search(name_pattern_3, name.group(1))
            if name:
                print(f"Name2: {name}")
                return name.group(1).strip()
    return None

def extract_dob(text, results):
    dob_pattern_1 = r'(?i)(?:DOB|Date of Birth|D\.O\.B|D\.O\.B\.)[\s:-]+(\d{2}[-\/]\d{2}[-\/]\d{4})'
    dob_pattern_2 = r'\b\d{2}[-/]\d{2}[-/]\d{4}\b'

    dob = re.search(dob_pattern_1, text)
    if dob:
        print(f"DOB1: {dob}")
        return dob.group(1)
    dob = re.search(dob_pattern_2, text)
    if dob:
        print(f"DOB2: {dob}")
        return dob.group(0)
    dob = re.search(dob_pattern_2, extract_text_from_list(results))
    if dob:
        print(f"DOB3: {dob}")
        return dob.group(0)
    return None

def extract_father_name(text, results, name):
    father_name_pattern_1 = fr'(?:{name})'
    father_name_pattern_2 = r'^.*?(?<!\S)([A-Z]+\s[A-Z\s]+)(?!\S).*?$'
    father_name_pattern_3 = r'(?i)(?:Father\'s Name|Father\'sName|Fathers Name|FathersName|Father Name)'
    father_name_pattern_4 = r'^(.*?)(?:\b(?:DOB|Date of Birth|D\.O\.B|D\.O\.B\.)\b)'

    idx = 0
    for i, (_, text, _) in enumerate(results):
        if re.search(father_name_pattern_1, text):
            idx = i
            break
    if idx != 0:
        for (_, text, _) in results[idx+1:]:
            father_name = re.search(father_name_pattern_2, text, re.DOTALL)
            if father_name:
                print(f"Father Name1: {father_name}")
                return father_name.group(1).strip()
    father_name1 = re.search(father_name_pattern_3, text)
    if father_name1:
        father_name = re.search(father_name_pattern_4, text[father_name1.end():], re.DOTALL)
        if father_name:
            father_name = re.search(father_name_pattern_2, father_name.group(1))
            if father_name:
                print(f"Father Name2: {father_name}")
                return father_name.group(1).strip()
    return None

def extract_text_from_list(text_list):
    return " ".join([res[1] for res in text_list])

def extract_text_from_image(results):
    return " ".join([res[1] for res in results if res[2] >= 0.40])