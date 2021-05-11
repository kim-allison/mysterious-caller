import spacy

'''
download:
pip install spacy
python -m spacy download en_core_web_sm
python dependency_parsing.py
'''

'''
HOW TO USE self FOR OUR PROJECT
  - to scare/threat the user, we can repeat what they say in a question for (ex. "Are you sure Starr is visiting Hawaii?", "Is it really true that you met Ellie yesterday?")
  - get the correct person that the caller is looking for (ex. "Who do you think the most popular person in your school?" --> "I think Allison is the most popular person." --> dependency parsing can get the subject "Allison" instead of "I".)
'''
class DependencyParsing:
  # nlp = spacy.load("en_core_web_sm")
  # doc = ""
  def __init__(self, text):
    nlp = spacy.load("en_core_web_sm")
    self.doc = nlp(text)

  def find_noun_chunk(self, doc):
    chunks = []
    for chunk in doc.noun_chunks:
        chunks.append({ "CHUNK": chunk.text, 
                  "ROOT": chunk.root.text, 
                    "DEP": chunk.root.dep_,
                  "HEAD": chunk.root.head.text})
    return chunks

  def explain(self, label):
    return label + ": " + spacy.explain(label)

  def find_verb_chunk(self, doc):
    """
    Returns a dictionary representing a simple verb chunk
    with a subject, verb, object.
    """
    for noun_chunk in doc.noun_chunks:
      if noun_chunk.root.dep_ != 'nsubj':
        continue
      subj = noun_chunk.root
      verb = subj.head
      for child in verb.children:
        obj = child
        if child.dep_ == 'dobj':
          verb_chunk = {
                        "subject": subj,
                        "verb": verb,
                        "object": obj
                        }
          return verb_chunk 
    return None 

  def derive_question(self, doc):
    """
    Return a string that rephrases an action in the
    doc in the form of a question.
    'doc' is expected to be a spaCy doc.
    """
    verb_chunk = self.find_verb_chunk(doc)
    if not verb_chunk:
      return None
    subj = verb_chunk['subject'].text
    obj = verb_chunk['object'].text
    # print(verb_chunk)
    if verb_chunk['verb'].tag_ != 'VB':
      # If the verb is not in its base form ("to ____" form),
      # use the spaCy lemmatizer to convert it to such
      verb = verb_chunk['verb'].lemma_
    else:
      verb = verb_chunk['verb'].text
    question = f"Why did {subj} {verb} {obj}?"
    return question 

  # lemmarization
  def lemmarize(self):
    """
    Find verbs which is not in the base form and show the form before and after lemmarization.
    """
    verb_chunk = self.find_verb_chunk(self.doc)
    lemmas = []
    if not verb_chunk:
      return None
    if verb_chunk['verb'].tag_ != 'VB':
      lemmarized = verb_chunk['verb'].lemma_
      lemmas.append((verb_chunk['verb'].text, lemmarized))
    return lemmas  

  def test_sentence(self):
    for noun_chunk in self.doc.noun_chunks:
      root = noun_chunk.root
      head = root.head
      children = head.children

      print("ROOT", root, root.dep_)
      print("HEAD", head, head.dep_)
      for child in children:
        print(child, child.dep_)
      # for i in range(len(children)):
      #   print("CHILD" + i, children[i].dep_)
    return None


  '''
  COMPONENT3 EXAMPLES OF EXTRACTORS
  (something like find_verb_chunks())
  '''
  # 1. Negative Sentence
  def find_negative_chunk(self):
    """
    Returns a dictionary representing a simple verb chunk
    with a subject, verb, object of negative sentences.
    """
    for noun_chunk in self.doc.noun_chunks:
      if noun_chunk.root.dep_ != 'nsubj':
        continue
      subj = noun_chunk.root
      verb = subj.head
      negative = False
      for child in verb.children:
        obj = child
        if child.dep_ == 'neg':
          negative = True
        if child.dep_ == 'dobj':
          if negative == True:
            neg_chunk = {
                        "subject": subj,
                        "verb": verb,
                        "object": obj,
                        "negative": negative
                        }
            return neg_chunk 
    return None

  # 2. Feeling
  def find_adjective_chunk(self):
    """
    Returns a dictionary representing a simple verb chunk
    with a subject, be-verb, adjective of negative sentences.
    """
    for noun_chunk in self.doc.noun_chunks:
      if noun_chunk.root.dep_ != 'nsubj':
        continue
      subj = noun_chunk.root
      verb = subj.head
      negative = False
      for child in verb.children:
        if child.dep_ == 'neg':
          negative = True
        if child.dep_ == 'acomp':
          adj = child
          if negative == True:
            adj_chunk = {
                        "subject": subj,
                        "verb": verb,
                        "adjective": adj,
                        "negative": negative
                        }
            return adj_chunk 
    return None

  # 3. Reason
  def find_reason_chunk(self):
    """
    Returns a dictionary representing a simple chunk with a reason starting with because/since/as
    """
    reason = False
    for noun_chunk in self.doc.noun_chunks:
      if noun_chunk.root.dep_ != 'nsubj':
        continue
      subj = noun_chunk.root
      verb = subj.head
      negative = False
      negative_text = "affirmative"
      for child in verb.children:
        if child.dep_ == 'neg':
          negative = True
          negative_text = "negative"
        if child.dep_ == 'mark' and child.text in ['because', 'as', 'since']:
          reason = True
        if reason == True:
          if child.dep_ == 'nsubj':
            subj = child
          if child.dep_ == 'verb':
            verb = child
          if child.dep_ == 'dobj':
            obj = child
            reason_chunk = {
                        "subject": subj,
                        "verb": verb,
                        "object": obj,
                        "negative": negative_text
                        }
            return reason_chunk 
    return None

  # 4. Question
  def find_question_chunk(self):
    """
    Returns a dictionary representing a simple question chunk with auxiliary verb, subject, verb, and object
    """
    for noun_chunk in self.doc.noun_chunks:
      if noun_chunk.root.dep_ != 'nsubj':
        continue
      subj = noun_chunk.root
      verb = subj.head
      question = False
      for child in verb.children:
        if child.dep_ == 'aux':
          aux = child
        if child.dep_ == 'dobj':
          obj = child
          question_chunk = {
                      "auxiliary": aux,
                      "subject": subj,
                      "verb": verb,
                      "object": obj,
                      }
          return question_chunk 
    return None

  # 5. If
  def find_if_chunk(self):
    """
    Returns a dictionary representing a simple chunk with a if question with subject, verb, and object
    """
    if_statement = False
    for noun_chunk in self.doc.noun_chunks:
      if noun_chunk.root.dep_ != 'nsubj':
        continue
      subj = noun_chunk.root
      verb = subj.head
      negative = False
      negative_text = "affirmative"
      for child in verb.children:
        if child.dep_ == 'neg':
          negative = True
          negative_text = "negative"
        if child.dep_ == 'mark' and child.text in ['if']:
          if_statement = True
        if if_statement == True:
          if child.dep_ == 'nsubj':
            subj = child
          if child.dep_ == 'verb':
            verb = child
          if child.dep_ == 'dobj':
            obj = child
            if_chunk = {
                        "subject": subj,
                        "verb": verb,
                        "object": obj,
                        "negative": negative_text
                        }
            return if_chunk 
    return None

if __name__ == "__main__":
  

  text1 = "I don't believe you."
  text2 = "He was not happy about the rain."
  text3 = "It is because he forgot his umbrella."
  text4 = "Do I do anything to you?"
  text5 = "What happens if I call the police?"
  text6 = "I tried to tell him the truth but I was scared."
  text7 = "I don't want you to kill either my dad or my mom."


  DP = DependencyParsing(text1)
  print(DP.find_noun_chunk())
  # test_num = 1
  # if test_num == 0:
  #   print(test_sentence(nlp(text5)))

  # if test_num == 1:
  #   doc = nlp(text1)
  #   print(find_verb_chunk(doc))
  # elif test_num == 2:
  #   doc = nlp(text2)
  #   print(find_adjective_chunk(doc))
  # elif test_num == 3:
  #   doc = nlp(text3)
  #   print(find_reason_chunk(doc))
  # elif test_num == 4:
  #   doc = nlp(text4)
  #   print(find_question_chunk(doc))
  # elif test_num == 5:
  #   doc = nlp(text5)
  #   print(find_if_chunk(doc))


# James' examples
  sample_text1 = "Buster ghosted Schiller and they both ran across the Brooklyn Bridge"
  sample_text2 = "Both Buster and I ghosted Schiller"
  sample_text3 = "both our children are cute"

  # print(find_noun_chunk(doc))

  labels = ["root", "acl", "acomp", "advcl", "advmod", "agent", "amod", "appos", "attr", "aux", "auxpass", "case", "cc", "ccomp", "compound", "conj", "csubj", "csubjpass", "dative", "dep", "det", "dobj", "expl", "intj", "mark", "meta", "neg", "nmod", "npadvmod", "nsubj", "nsubjpass", "nummod", "oprd", "parataxis", "pcomp", "pobj", "poss", "preconj", "prep", "prt", "punct", "quantmod", "relcl", "xcomp"]
  # "predet" could not be processed
  # for label in labels:
  #   print(explain(label))

  # print(derive_question(doc))

  # print(lemmarize(doc))