from game_state import GameState
# from understander import Understander
from markov_chain import MarkovChain
import eliza_transform
from textblob import TextBlob
from profanity import profanity
from dependency_parsing import DependencyParsing
from grammar_engine import *
import random

class Generator:
  questions = []

  def __init__(self, goal):    
    self.engine = GrammarEngine('./dialogueSystem/grammar/generator.txt')

    f_dracula= open('./dialogueSystem/dracula.txt')
    whole_dracula = f_dracula.read()
    train_dracula = whole_dracula[:int(len(whole_dracula)*0.8)]
    train_dracula_file = open('./dialogueSystem/train_dracula.txt',"w+")
    train_dracula_file.write(train_dracula)

    self.identity_chain = MarkovChain('./dialogueSystem/train_dracula.txt', "word", 3)
    
    if goal == "Friend":
      f_questions = open('./dialogueSystem/questionsFriendGoal.txt')
    else: # User
      f_questions = open('./dialogueSystem/questionsUserGoal.txt')
    self.questions = f_questions.read().splitlines()
    # print(self.questions)
    self.asked_questions = []
    self.prev_count = -1

  # Resolve obligation: Starr
  def resObligation(self, gameState, userResponse):
    engine = GrammarEngine('./dialogueSystem/grammar/response_question.txt')
    return engine.generate('response')
  
  # Strong sentiment
  def addressPositiveSentiment(self, gameState, userResponse):
    engine = GrammarEngine('./dialogueSystem/grammar/polarity_response.txt')
    return engine.generate('positive')

  def addressNegativeSentiment(self, gameState, userResponse):
    engine = GrammarEngine('./dialogueSystem/grammar/polarity_response.txt')
    return engine.generate('negative')

  # Subjectivity: Rie
  def addressSubj(self, gameState, userResponse):
    response = TextBlob(userResponse)
    subjectivity = response.sentiment.subjectivity
    if subjectivity < 0.4:
      return "That sounds like a fact. I believe you for that."
    elif subjectivity >=0.4 and subjectivity < 0.8:
      return "Actually, are you sure about that? That sounds a bit subjective."
    else:
      return "Oh, but that's just your opinion, right? I don't know if I should trust that as a fact, my friend."
    return "ERROR"

  # Keyphrase: Allison
  '''
  The keyphrases that trigger this:
  - askedWhoTheCallerIs: Markov Chain (Dracula)
  - greetedCaller
  - saidGoodbye
  '''
  def keyphraseTrigger(self, gameState, userResponse, keyphrase):
    if keyphrase == "askedWhoTheCallerIs":
      # MarkovChain
      response = "Well, I'm glad you asked. I'm a travelling storyteller, and I would love to hear your story. But wait! I'll tell you my story first. I hope you like it.\n\n"
      return response+self.identity_chain.generate(55)
    elif keyphrase == "greetedCaller":
      return "Hello, my friend. Good to hear your voice. I hope I'm not interrupting anything. I just wanted to ask you a few questions if that's okay."
    else: # saidGoodbye
      return "I guess this is the end of our call. Maybe we'll talk again some other day...maybe we won't. Goodbye now."
    return "ERROR"
  
  # Profanity: Rie
  def addressProf(self, gameState, userResponse):
    # if profanity.contains_profanity(userResponse):
    dirtyWords = userResponse.split(" ")
    cleanWords = profanity.censor(userResponse).split(" ")
    for i in range(len(dirtyWords)):
      dirtyWord = ""
      cleanWord = ""
      if dirtyWords[i] != cleanWords[i]:
        if dirtyWords[i][-1] in [',', '.', '!', '?']:
          dirtyWord = dirtyWords[i][:-1]
          dirtyWord = '"' + dirtyWord + '"'
        else:
          dirtyWord = '"' + dirtyWords[i] + '"'
        if cleanWords[i][-1] in [',', '.', '!', '?']:
          cleanWord = cleanWords[i][:-1]
        else:
          cleanWord = cleanWords[i]
        self.engine.set_variable("dirty", dirtyWord)
        self.engine.set_variable("clean", cleanWord)
        return self.engine.generate('profanity')
    return "Something has gone wrong"
    
  # Nothing detected: Rie
  def fallback(self, gameState, userResponse):
    return self.engine.generate('fallback')
    # print("What do you mean? Give me more detail, or I will come to you tonight.")

  # Default/ user info getting questions: Allison
  # should be determined by which goal we have for this game gameState.getGoal()
  def askQuestion(self, gameState, userResponse):
    # print("INFO COUNT: ", gameState.informationCount)
    # response = self.questions[gameState.informationCount]

    if self.prev_count == gameState.informationCount:
      response = self.asked_questions[-1]
    elif gameState.informationCount == 0:
      response = self.questions[0]
      self.asked_questions.append(response)
      self.prev_count = gameState.informationCount
    else:
      response = random.choice(self.questions)
      while response in self.asked_questions:
        response = random.choice(self.questions)
      self.asked_questions.append(response)
      self.prev_count = gameState.informationCount

    if '%' in response:
      words = response.split()
      temp_words = words.copy()

      for i in range(0,len(words)):
        some_word = words[i]
        first_mem = ""
        last_mem = ""

        # print("SOME WORD: ", some_word)
        if some_word[-1] == "s" and some_word[-2] == "'" :
          last_mem += some_word[-2:]
          some_word = some_word[:-2]
          # print("NO 's WORD: ", some_word)
        if some_word[-1] in '!#$&()*+, -./:;<=>?@[\]^_`{|}~':
          last_mem += some_word[-1]
          some_word = some_word[:-1]
        if some_word[0] in '!#$&()*+, -./:;<=>?@[\]^_`{|}~':
          first_mem += some_word[0]
          some_word = some_word[1:]

        # print("PROCESSED WORD: ", some_word)
        if some_word[0] == '%' and some_word[-1] == '%':
          key = some_word[1:-1]
          if key not in gameState.information:
            # self.askQuestion(gameState, userResponse)
            terms = key.split('_')
            if terms[0] == "grow":
              replace = "your town"
            else:
              replace = "a "+terms[0]
          else:
            replace = gameState.information[some_word[1:-1]]
          temp_words[i] = first_mem+replace+last_mem
      
      # print(temp_words)
      response = " ".join(temp_words)
      if response[-1] != '?':
        response += "?"

    if gameState.informationCount > 0 and self.prev_count != gameState.informationCount:
      transitions = [
      "I see. ",
      "Interesting...",
      "Oh really? ",
      "Ah, ok. ",
      "Hm...",
      "Yeah? ",
      "Alright. ",
      "Aha. "
      ]
      response = random.choice(transitions)+response
    return response

  # Allison
  # If the user gave information, let's respond to it!
  # Use the gameState to see what info we asked for, and then say something about it
  def addressAvoidance(self, gameState, userResponse):
    options = [
      "I'm not sure what you mean.",
      "You're avoiding my questions.",
      "I won't be able to write a good story if you don't answer my questions.",
      "I don't think I get it.",
      "Could you say that again?"
    ]
    return random.choice(options)

  def elizaTransformation(self, gameState, userResponse):
    transformed_response = eliza_transform.transform(userResponse)
    return transformed_response

  def addressQuestion(self, gameState, userResponse):
    options = [
      "Let's focus on your experiences for now.",
      "Let's not talk about me.",
      "Are you sure you should be asking me questions?",
      "We don't have time to both ask questions!",
      "You can ask me questions later"
    ]
    return random.choice(options)



# G = Generator("User")
# print(G.addressPositiveSentiment(None, "I love you"))
# print(G.addressNegativeSentiment(None, "I hate you"))


# # G.addressSubj(None, "I am happy")
# # G.fallback(None, "I am happy")
# # print(G.addressProf(None, "You smell like shit."))
# # print(G.keyphraseTrigger(None, "Who are you?", "askedWhoTheCallerIs"))
# test_gameState = GameState()
# test_gameState.informationCount = 7
# test_gameState.information["park"] = "Allison's Private Park"
# print(G.askQuestion(test_gameState, "Hi"))