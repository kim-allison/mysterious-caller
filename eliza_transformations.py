import re
import random
# from dependency_parsing import find_verb_chunk, find_noun_chunk, find_adjective_chunk
from dependency_parsing import *
import spacy


'''
Other tricks that ELIZA does:

If asked a question, Eliza responds with something like “What do you think?” 

If something is mentioned about Eliza: "You're not really talking about me, are you?"

If you include a “no”, Eliza akss if you are being negative

With a “I am … “ : responds “How long have you been …”

Will quote you with a “Tell me more”

Apologies : “What feelings do you have when you apologize?"

If there's nothing to rearrange, Eliza responds with something like "tell me more" or a netural prompt

If there's feel or feelings, Eliza responds "Tell me more about those feelings"
'''

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


  doc = nlp(sentence)
  verb_chunk = find_verb_chunk(doc)
  adj_chunk = find_adjective_chunk(doc)
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

def main():
  print("You: My boyfriend made me come here.")
  print("ELIZA: " + transform("My boyfriend made me come here."))
  print("You: I am sad.")
  print("ELIZA: " + transform("I am sad."))
  print("You: I want to run away from my parents.")
  print("ELIZA: " + transform("I want to run away from my parents."))
  print("You: What should I do?")
  print("ELIZA: " + transform("What should I do?"))
  print("You: What are you?")
  print("ELIZA: " + transform("What are you?"))
  print("You: I am so sorry I did that.")
  print("ELIZA: " + transform("I am so sorry I did that."))
  print("You: Pumpkin pie is my favorite!")
  print("ELIZA: " + transform("Pumpkin pie is my favorite!"))
  print("You: I run every Thursday")
  print("ELIZA: " + transform("I run every Thursday"))

main()