from nltk import ne_chunk, pos_tag, word_tokenize
import nltk
from tqdm import tqdm
from nltk.tree import Tree
import re

def flatten(l): 
    return [item for sublist in l for item in sublist]

def unique(l): 
    l = list(filter(lambda i: i is not None, l))
    l = [a.strip() for a in l]
    return sorted(list(set(l)), key=str.casefold)

def get_people(text): 
    """For a string of text, return people."""
    people = []
    nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
    for nltk_result in nltk_results:
        if type(nltk_result) == Tree:
            name = ''
            for nltk_result_leaf in nltk_result.leaves():
                name += nltk_result_leaf[0] + ' '
            if nltk_result.label() == "PERSON":
                people.append(name.strip())
    return people


def get_thanks(commits):
    """Search all commit messages for people manually thanked. 
    Often associated with security fixes, as these are processed by Fellows with attributing the people who
    notified them about the issue."""


    print("Processing all commit messages...")

    thanks_messages = [c.message for c in commits if "Thanks" in c.message]

    thanks = []
    security_thanks = []
    second_pass = []

    for msg in thanks_messages: 
        thanks = re.findall("Thanks (.*) for", msg)
        if not thanks:
            second_pass.append(msg)
            continue
        # Some messages contain multiple people, so split them out. 
        for thank in thanks:
            thank = thank.replace("to ", "")
            if "," in thank:
                thank = thank.split(",")
                security_thanks += [t.strip() for t in thank]
            elif "and" in thank:
                thank = thank.split("and")
                security_thanks += [t.strip() for t in thank]
            else:
                security_thanks.append(thank)

    # inline cleanup
    for i, thank in enumerate(security_thanks):
        security_thanks[i] = thank.split("for")[0]
        
    for i, thank in enumerate(security_thanks):
        security_thanks[i] = thank.split("and")[0]
        
        
    # remove duplicates
    security_thanks = unique(security_thanks)
    complex_thanks = []
    people = []

    # split out our thanks to parse and keep
    for person in security_thanks:
        if "," in person:
            complex_thanks.append(person)
        else:
            people.append(person)
            
    for thank in complex_thanks:
        people += get_people(thank)
    
    
    # Remove word set
    word_set = ["Fixed", "Changed", "Django", "Matches", "Redis", "Catalan", "Exact", 
                "Ref", "Sphinx", "Splunk", "Moved", "Month", "Python", "Switched"]
        
    people = unique(people)
    for i, person in enumerate(people):
        # Trim out word set
        people[i] = person.replace("Thanks ", "")
        if person in word_set:
            people.pop(i)

    return people


def install_nltk_data(): 

    print("Downloading NLTK data packages...")
    for package in tqdm(["punkt", "averaged_perceptron_tagger", "maxent_ne_chunker", "words" ]):
        nltk.download(package, quiet=True)