import re
import random
# import dependency_parsing
import spacy
from dependency_parsing import DependencyParsing

pronouns_dict = {
  "I": "you",
  "me": "you",
  "my": "your",
  "myself":"yourself",
  "Me": "You",
  "My": "Your",
  "Myself":"Yourself",
  "I'm": "you are"
}

verbs_dict = {
  "am": "are",
  "was": "were"
}

starts = [
  "Why do you say that you ",
  "What would it mean to you ",
  "Do you often feel like you want to "
]

nlp = spacy.load("en_core_web_sm")

def transform(sentence):

  #Special Cases
  if " no " in sentence: 
    return "Are you saying no just to be negative?"
  if " you" in sentence or "You " in sentence or "you " in sentence:
    return "You're not really talking about me, are you?"
  if " sorry " in sentence or " apologize " in sentence:
    return "What feelings do you have when you apologize?"
  if "?" in sentence:
    return "What do you think?"
  if " feel " in sentence or " feeling " in sentence:
    return "Tell me more about those feelings"

  dependency_parsing = DependencyParsing(sentence)

  doc = nlp(sentence)
  verb_chunk = dependency_parsing.find_verb_chunk(doc)
  adj_chunk = dependency_parsing.find_adjective_chunk()
  # print("VERB CHUNK:", verb_chunk)
  # print("ADJ CHUNK:", adj_chunk)

  #Catching sentences with adjectives
  ran = random.random()
  if adj_chunk != None and str(adj_chunk['subject']) == "I":
    if ran < 0.5:
      if bool(adj_chunk['negative']):
        return 'Do you think not being ' + str(adj_chunk['adjective']) + ' is normal?'
      else:
        return 'Do you think being ' + str(adj_chunk['adjective']) + ' is normal?'
    if bool(adj_chunk['negative']):
      return "How long have you not been " + str(adj_chunk['adjective']) + "?" 
    else:
      return "How long have you been " + str(adj_chunk['adjective']) + "?" 
 
  #Use verb chunk if you can, find subject, obj to be able to decide which pronouns to change .
  if verb_chunk != None:
    if str(verb_chunk['subject']) == "I":
      begin = random.choice(starts)
      begin += str(verb_chunk['verb'])
      begin += " "
      begin += str(verb_chunk['object'])
      begin += "?"
      return begin
  
  ran = random.random()
  if ran < 0.1:
    return 'Interesting. "' + sentence + '"' + ' Tell me more about that.'
  #Last chance: simple swapping of pronouns and verbs
  if "I " in sentence or " me " in sentence:
    opt = ["Tell me more.", "Please expand on that.", "How does that make you feel?"]
    #simply swap pronouns and verbs and make questions
    transformed = ""
    tokens = re.findall(r"[\w']+|[.,!?;]", sentence)
    for token in tokens:
      if token == ".":
        token = "?"
        transformed = transformed[:-1]
      elif token == "?":
        token = "."
        transformed = transformed[:-1]
      if token in pronouns_dict:
        transformed += pronouns_dict[token]
      elif token in verbs_dict:
        transformed += verbs_dict[token]
      else:
        transformed += token
    
      transformed += " "
    transformed = transformed[0].upper() + transformed[1:]
    if not ("." in transformed or "?" in transformed):
      transformed = transformed[:-1]
      transformed += "."
    if ran < 0.6:
      transformed += " "
      transformed += random.choice(opt)
    return transformed
  
  #if none of the options are triggered, just prompt for more information
  options = [
    "Tell me more.",
    "Come come. Elucidate your thoughts.",
    "Let's come back to that later. What else would you like to talk about?",
    "I understand."
  ]
  return random.choice(options)
