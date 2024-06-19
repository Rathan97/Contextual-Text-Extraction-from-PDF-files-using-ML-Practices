from flask import Flask, render_template, request
import PyPDF2
import nltk
import spacy
import re
import os

app = Flask(__name__)

def extract_text_from_pdf(pdf_path):
    text = ""  # Initialize variable to store text
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        # Iterate over each page in the PDF
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    # Tokenize the text into sentences
    sentences = nltk.sent_tokenize(text)
    return sentences,text

def find_director_sentences(sentences):
    director_sentences = []  # Initialize array to store sentences containing the word "director"
    for sentence in sentences:
        if 'director' in sentence.lower():
            director_sentences.append(sentence)
    return director_sentences


def find_person_names(sentences):
    # Load spaCy English language model
    nlp = spacy.load('en_core_web_sm')
    
    person_names = set()  # Initialize set to store unique person names
    for sentence in sentences:
        doc = nlp(sentence)
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                # Check if the entity consists of multiple tokens
                if len(ent.text.split()):
                    person_names.add(ent.text)
                else:
                    # If the entity consists of a single token, check if it starts with a title
                    if ent.text.istitle():
                        person_names.add(ent.text)
                    else:
                        # Otherwise, skip the entity
                        continue
    return list(person_names)

def clean_director_names(director_names, blacklist):
    cleaned_names = set()
    for name in director_names:
        # Remove spaces and dots from the name
        
        # Check if the cleaned name is not in the blacklist
        if name.lower() not in [item.lower() for item in blacklist]:
            cleaned_names.add(name)
    return cleaned_names

def find_din_and_status(director_names, all_sentences):
    director_info = {}  # Initialize dictionary to store DIN and status for each director
    for name in director_names:
        # Initialize variables to store DIN and status for the current director
        din = "DIN not found"
        status = "Status not specified"
        
        # Search for director name, DIN, and status in all sentences
        for sentence in all_sentences:
            # Check if the director name exists in the sentence
            if name in sentence:
                # Extract the line where the director's name is mentioned within the sentence
                lines = sentence.split('\n')
                for line in lines:
                    if name in line:
                        # Extract DIN number if present
                        din_match = re.search(r'\bDIN\s*:\s*(\d+)\b', line)
                        if din_match:
                            din = din_match.group(1)
                            break
                        
                        # Extract DIN number if mentioned one or two words after director's name
                        words = line.split()
                        if name in words:
                            name_index = words.index(name)
                            if name_index + 2 < len(words):
                                din_match = re.search(r'\b(\d+)\b', words[name_index + 2])
                                if din_match:
                                    din = din_match.group(1)
                                    break
                            
                        # Determine type (independent, executive, whole-time, non-executive, non-independent)
                        if 'independent' in line.lower():
                            status = "Independent"
                        elif 'executive' in line.lower():
                            status = "Executive"
                        elif 'whole-time' in line.lower():
                            status = "Whole-time"
                        elif 'non-executive' in line.lower():
                            status = "Non-Executive"
                        elif 'non-independent' in line.lower():
                            status = "Non-Independent"
                    
                # If DIN and status are not found in the line, check the entire sentence for director type
                if din == "DIN not found" or status == "Status not specified":
                    if 'independent' in sentence.lower():
                        status = "Independent"
                    elif 'executive' in sentence.lower():
                        status = "Executive"
                    elif 'whole-time' in sentence.lower():
                        status = "Whole-time"
                    elif 'non-executive' in sentence.lower():
                        status = "Non-Executive"
                    elif 'non-independent' in sentence.lower():
                        status = "Non-Independent"
                
                # Store DIN and status for the director
                director_info[name] = {'DIN': din, 'Status': status}
                break  # Exit the loop once information is found for the director
    
    return director_info

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        pdf_path = 'uploads/' + f.filename
        f.save(pdf_path)
        pdf_sentences, text = extract_text_from_pdf(pdf_path)
        director_sentences = find_director_sentences(pdf_sentences)
        director_names = find_person_names(director_sentences)
        blacklist = [
            'Chairperson', 'ALM', 'A-44 Hosiery Complex', 'BSEListingCentre Thru', 
            'Asabove', 'Copyto', 'Dhruv M.', 'Sawhney', 'Homai A. Daruwalla', 
            'Memberships/ Chairmanships', 'Noida Rajiv Sawhney', 'Date', 
            'Dhruv M. Sawhney', 'Lagnam', 'Spintex India Ltd.', 'C. Laddha', 
            'Qualifications B.Sc.', 'J. C. Laddha', 'and/or re -enactment(s', 
            'w. e. f.', 'NA Appointment', 'Directorships', 'Bandra Kurla Complex', 
            'Schedule III','Chairperson \nALM', 'A-44 Hosiery Complex', 'BSEListingCentre Thru', 'Asabove\nCopyto',  'Homai A. Daruwalla', 'Memberships/ Chairmanships',
            'Noida Rajiv Sawhney\nDate','Lagnam \nSpintex India Ltd.', 'Prashant Barve\nDirectorships','Lagnam \nSpintex India Ltd.','Mannepalli Lakshmi Kantam', 'M. Lakshmi','Jeet Singh Bagga',
            'Nikhil Sawhney','Tarun Sawhney','Dhruv M Sawhney','Dhruv M. \nSawhney','J','Kantam','modification(s','Schedule','RSWM','Bandra','Scrutinizer','Bhasin','Director','Bandra-KurlaComplex','Founder','Mumbai-400013',
            'Gangotra',            
        ] 
        cleaned_director_names = clean_director_names(director_names, blacklist)
        director_info = find_din_and_status(cleaned_director_names, director_sentences)
        for director, info in director_info.items():
            if info['Status'] == "Status not specified":
                info['Status'] = "Whole-time"
        return render_template('result.html', director_info=director_info)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
