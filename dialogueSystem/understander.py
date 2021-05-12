from game_state import GameState
from profanity import profanity
from island_parser import IslandParser
from grammar_engine import GrammarEngine
import re
import string
import spacy
from textblob import TextBlob
from langdetect import detect, detect_langs
import enchant

class Understander:

  def __init__(self):
    greeting_grammar = './dialogueSystem/grammar/greeting.txt'
    self.greeting_IP = IslandParser(greeting_grammar)

    goodbye_grammar = './dialogueSystem/grammar/goodbye.txt'
    self.goodbye_IP = IslandParser(goodbye_grammar)

    identity_grammar = './dialogueSystem/grammar/identity.txt'
    self.identity_IP = IslandParser(identity_grammar)

    self.nlp = spacy.load("en_core_web_sm")

    self.lang_dict = enchant.Dict("en_US")

  '''
  codeResponse will return a list of integers that represent responseCodes (labeled below) and an updated gameState object
    responseCodes:
    1. asks question
    2. ask who the caller is
    3. greet caller
    4. goodbye caller
    5. strong negative sentiment
    6. profanity
    7. nonsense
    8. avoided question
    9. subjectivity
    10. strong positive sentiment
    11. DialogueTag type of question was asked -> generator: resolveObligation -> and then check 1
    12. non-English response
  '''
  def codeResponse(self, userResponse, gameState):
    responseCodes = []

    if self.hasPositiveSentiment(userResponse):
      responseCodes.append(10)
      # gameState.confused = True

    if self.hasNegativeSentiment(userResponse):
      responseCodes.append(5)
      gameState.rudeCount += 1
    
    if self.hasStrongSubjectivity(userResponse):
      responseCodes.append(9)

    if self.hasProfanity(userResponse):
      responseCodes.append(6)
      gameState.rudeCount += 1

    if self.isGoodbye(userResponse):
      responseCodes.append(4)

    if self.isNonsense(userResponse):
      responseCodes.append(7)
      gameState.unreadableCount += 1
    
    # *need to use caller's question
    if gameState.askedQuestion:
      # print("ASKED QUESTION")
      avoid_check, information = self.isAvoid(userResponse, gameState)
      if not avoid_check:
        if len(information) == 2 and information[0] != "NO SAVE":
          # print("NEW INFO ADDED: ", information[0], '->', information[1])
          gameState.information[information[0]] = information[1]
        gameState.newInfo = information[0]
        gameState.informationCount += 1
      else:
        responseCodes.append(8)
        gameState.unreadableCount += 1

    if self.isIdentityQuestion(userResponse):
      responseCodes.append(2)
    elif self.isGreeting(userResponse):
      responseCodes.append(3)
    elif self.isQuestion(userResponse):
      responseCodes.append(1)

    if gameState.lang_sensitive and not self.isEnglish(userResponse):
      return [12], gameState

    return responseCodes, gameState
  
  def isEnglish(self, userResponse):
    what_lang = detect(userResponse)
    if what_lang != 'en' and not self.lang_dict.check(userResponse):
      return False
    return True

  def isQuestion(self, userResponse):
    '''
      1) check if the the user asked a question
      *use DialogueTag and update GameState (make new variable to identiy type of question)
    '''
    # ? -> DialogueAct
    if '?' in userResponse:
      return True
    # TODO(Allison): elif (DialogueAct)

    # this code might be helpful for dialogue act 
    # from dialog_tag import DialogTag
    # model = DialogTag('distilbert-base-uncased')

    # sentence = "I'll probably go to shopping today."
    # output = model.predict_tag(sentence)
    # output can be: Yes-No-Question	)
    # (Declarative Yes-No-Question
    return False 

  def isIdentityQuestion(self, userResponse):
    '''
      1) check against identity grammar: is the user asking for caller's identity
    '''
    parse_tree, tree_check = self.identity_IP.parse(userResponse)
    return tree_check

  #Starr
  def hasPositiveSentiment(self, userResponse):
    text = TextBlob(userResponse)
    sentiment = text.sentiment.polarity
    # print("Sentiment: ", text.sentiment.polarity)
    # edge cases: if it has "best" in the sentence, the sentiment will be 1.0, but we don't wannt to mark it as positive sentiment
    if "best" in userResponse.lower().split():
      return False
    return sentiment>=0.5 

  # #Starr
  def hasNegativeSentiment(self, userResponse):
    text = TextBlob(userResponse)
    sentiment = text.sentiment.polarity
    # print("Sentiment: ", text.sentiment.polarity)
    return sentiment<=-0.2 

  def hasStrongSubjectivity(self, userResponse):
    '''
      1) check if user's resposne contains subjectivity
    '''
    text = TextBlob(userResponse)
    subjectivity = text.sentiment.subjectivity
    # print("Subjectivity: ", text.sentiment.subjectivity)
    if subjectivity > 0.7:
      return True
    return False  

  def hasProfanity(self, userResponse):
    '''
      1) check if user used profanity
      * increment rude count 
    '''
    return profanity.contains_profanity(userResponse)

  def isGreeting(self, userResponse):
    '''
      1) check if user is greeting caller
      (grammar + key phrase)
    '''
    # for long greetings
    # *check DialogueTag for opening
    parse_tree, tree_check = self.greeting_IP.parse(userResponse)

    # for short greetings (one token response)
    short_greetings = ["hi", "hello"]
    if any(some_greeting in userResponse.lower().split() for some_greeting in short_greetings):
      return True
    return tree_check
  
  def isGoodbye(self, userResponse):
    '''
      1) check if user is saying goodbye to caller
      (grammar + key phrase)
      *last bot resposne
    '''
    # for long goodbyes
    # *check DialogueTag for closing
    parse_tree, tree_check = self.goodbye_IP.parse(userResponse)

    # for short goodbyes (one token response)
    short_greetings = ["goodbye", "bye"]
    if any(some_greeting in userResponse.lower().split() for some_greeting in short_greetings):
      return True
    return tree_check

  def isNonsense(self, userResponse):
    if "":
      return True
    return False

  def get_ner(self, userResponse):
    doc = self.nlp(userResponse)

    ner_info = []
    for ent in doc.ents:
      ent_info = [ent.text, ent.start_char, ent.end_char, ent.label_]
      ner_info.append(ent_info)
    return ner_info
  
  def get_tagged(self, tag, ner_info):
    for info in ner_info:
      if info[3] == tag:
        return info[0]
    return "ERROR"

  def check_ner(self, tag, userResponse):
    ner_info = self.get_ner(userResponse)
    return self.get_tagged(tag, ner_info)
  
  def check_grammar(self, grammar_name, userResponse, get_val=False):
    grammar = './dialogueSystem/grammar/'+grammar_name+'.txt'
    IP = IslandParser(grammar)
    parse_tree, tree_check = IP.parse(userResponse)
    # print("TREE: ", parse_tree)

    if not tree_check:
      return "ERROR"

    if get_val:
      tokens = userResponse.split()
      tree = re.findall('\(.*?\)', parse_tree[0][0])[0]
      indexes = [index for index, element in enumerate(tree) if element == '(']
      first_tree = tree[indexes[len(indexes)-1]:]
      first_tokens = first_tree.split()
      first_token = first_tokens[len(first_tokens)-1][:-1]
      value = tokens[tokens.index(first_token)+1:][0]
      if value[-1] in string.punctuation:
        value = value[:-1]
      return value
    return "WHAT"

  def isAvoid(self, userResponse, gameState):
    '''
      1) when user info question was asked, and the user's response just doesn't make sense
      (DialogueAct -> NER tag -> grammar)

      *increment unreadable count (True)
      *check if it's a set_variable situation!
      (in gameState: was Question)
      *update information, information count
    '''
    information = []
    bot_question = gameState.lastBotResponse

    if len(userResponse) < 1:
      return True, information
    elif userResponse[-1] not in '!#$&()*+, -./:;<=>?@[\]^_`{|}~':
      userResponse += "."

    # name questions
    if "name" in bot_question or "who" in bot_question.lower():
      if "siblings" in bot_question:
        information.append("sibling")
      if "best friend" in bot_question:
        information.append("friend_name")
      else:
        information.append(gameState.goal.lower()+"_name")

      name_key_bf = ["I'm"]

      # TODO(Allison): *DialogueAct check first
      ner_value = self.check_ner("PERSON", userResponse)
      if ner_value != "ERROR":
        information.append(ner_value)
        return False, information
      
      grammar_value = self.check_grammar("name", userResponse, True)
      if grammar_value != "ERROR":
        information.append(grammar_value)
        return False, information

      for some_name in name_key_bf:
        response_words = userResponse.split()
        if some_name in response_words:
          bf_num = response_words.index(some_name)
          value = response_words[bf_num+1]
          if value[len(value)-1] in string.punctuation:
            value = value[:-1]
          information.append(value)
          return False, information

    # time questions
    elif "time" in bot_question or "when" in bot_question.lower():
      time_key_bf = ["at", "around"]
      time_key_af = ["am", "pm"]
      information.append("time")

      day_key = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

      ner_value = self.check_ner("TIME", userResponse)
      if ner_value != "ERROR":
        information.append(ner_value)
        return False, information
      
      grammar_value = self.check_grammar("time", userResponse, True)
      if grammar_value != "ERROR":
        information.append(grammar_value)
        return False, information

      for some_time in time_key_bf:
        response_words = userResponse.split()
        if some_time in response_words:
          bf_num = response_words.index(some_time)
          value = response_words[bf_num+1]
          if value[len(value)-1] in string.punctuation:
            value = value[:-1]
          information.append(value)
          return False, information
      
      for some_time in time_key_af:
        response_words = userResponse.split()
        if some_time in response_words:
          bf_num = response_words.index(some_time)
          value = response_words[bf_num-1]
          if value[len(value)-1] in string.punctuation:
            value = value[:-1]
          information.append(value)
          return False, information

      for some_day in day_key:
        response_words = userResponse.lower()
        if some_day in response_words:
          return False, information

    # event questions
    elif "doing" in bot_question or "like working out" in bot_question or "like to hang out" in bot_question or "like to do" in bot_question:
      if "for fun" in bot_question:
        information.append("activity")

      elif "events" in bot_question:
        information.append("event")

        ner_value = self.check_ner("EVENT", userResponse)
        # print("NER: ", ner_value)
        if ner_value != "ERROR":
          information.append(ner_value)
          return False, information

      else:
        information.append("NO SAVE")

        choice_key = ["yes", "no", "yeah", "maybe", "think so"]

        for some_choice in choice_key:
          response_words = userResponse.lower()
          if some_choice in response_words:
            return False, information

      # lazy ha -- just using existing grammar ("I like" <blah>)
      grammar_value = self.check_grammar("what_location_af", userResponse, True)
      if grammar_value != "ERROR":
        information.append(grammar_value)
        return False, information
    
    # WHAT IS-location questions
    # user: restaurant, park
    elif "what is" in bot_question.lower() or "where" in bot_question.lower() or "what country" in bot_question.lower():
      if "restaurant" in bot_question:
        information.append("restaurant")
      elif "park" in bot_question:
        information.append("park")
      elif "work" in bot_question:
        information.append("work")
      elif "shop" in bot_question:
        information.append("shop")
      elif "grow" in bot_question:
        information.append("grow")
      else:
        information.append("NO SAVE")

      # location_key_bf = ["It's", "It is", "Probably"]
      # location_key_af = ["is my favorite"]
      possible_tags = ["FAC", "ORG", "GPE", "LOC"]

      for some_tag in possible_tags:
        ner_value = self.check_ner(some_tag, userResponse)
        # print("NER: ", ner_value)
        if ner_value != "ERROR":
          information.append(ner_value)
          return False, information

      grammar_value = self.check_grammar("what_location_af", userResponse, True)
      # print("GRAMMAR: ", grammar_value)
      if grammar_value != "ERROR":
        information.append(grammar_value)
        return False, information

      response_words = userResponse.split()
      if userResponse[0:5] == "It is":
        value = response_words[2]
        if value[len(value)-1] in string.punctuation:
          value = value[:-1]
        information.append(value)
        return False, information
      elif userResponse[0:4] == "It's":
        value = response_words[1]
        if value[len(value)-1] in string.punctuation:
          value = value[:-1]
        information.append(value)
        return False, information
    
    elif "frequently" in bot_question or "weekly" in bot_question or "what days" in bot_question.lower():
      information.append("NO SAVE")

      value = userResponse.lower()
      if value[len(value)-1] in string.punctuation:
        value = value[:-1]
      grammar_value = self.check_grammar("frequency", value)

      freq_key = ["always", "often", "sometimes", "occasionally", "seldom", "usually", "hardly", "rarely", "never", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "weekly", "monthly", "yearly"]

      if grammar_value != "ERROR":
        return False, information
      
      for some_freq in freq_key:
        response_words = userResponse.lower()
        if some_freq in response_words:
          return False, information
    
    elif "too" in bot_question or "have" in bot_question.lower() or "do you" in bot_question.lower() or "like to run" in bot_question or "would you" in bot_question.lower():
      information.append("NO SAVE")

      # yes or no questions
      choice_key = ["yes", "no", "yeah", "maybe", "think so"]

      for some_choice in choice_key:
        response_words = userResponse.lower()
        if some_choice in response_words:
          return False, information

    return True, information