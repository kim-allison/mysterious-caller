from understander import Understander
from generator import Generator
from game_state import GameState
import random
import time
from datetime import date
from datetime import datetime
from dialog_tag import DialogTag
import os

# from replit import audio

class Manager:
  
  '''
  create an understander, generator, and game state
  '''
  def __init__(self):

    # source = audio.play_file("./dialogueSystem/suspense.mp3")
    # volume = 1
    # loops = 0

    print("\n\n\n\n\nMYSTERIOUS CALLER v.1.0")
    print("©Big Ears®\n")
    print("Loading new game...\n\n\n\n\n")

    self.gameState = GameState()
    # lang_selection = input("Would you like to turn on language sensitivity? ")

    # if "yes" in lang_selection.lower():
    #   self.gameState.lang_sensitive = True
    # print("\nProcessing...\n\n\n\n\n")
    # time.sleep(2)

    lang_selection = [True, False]
    randomList = random.choices(lang_selection, weights=(10, 100), k=1)
    if randomList[0]:
      self.gameState.lang_sensitive = True

    self.understander = Understander()
    self.generator = Generator(self.gameState.goal)

    # print("WARNING! This game contains scenes of explicit violence.\n\n\n\n\n")
    # time.sleep(2)

    self.story = open('./dialogueSystem/story.txt', encoding="utf8").read().splitlines()
    self.achievement_path = './dialogueSystem/achievements.txt'

    self.model = DialogTag('distilbert-base-uncased')
    
  '''
  Based on the response codes, create a response to the user 
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
    11. resolve obligations
    12. not English
  '''
  def respond(self, userResponse):
  
    respCodes, self.gameState = self.understander.codeResponse(userResponse, self.gameState)
    self.gameState.askedQuestion = False
    # print("resp codes:", respCodes)
    takeMultipleTurns = False
    #if we need to respond with multiple things. Add them all to responses
    responses = []

    # if we have both subjectivity and sentiment, just address the sentiment, or sentiment and profanity
    # if 5 in respCodes and 9 in respCodes:
    #   respCodes.remove(9)
    # if 10 in respCodes and 9 in respCodes:
    #   respCodes.remove(9)
    # if 5 in respCodes and 6 in respCodes:
    #   respCodes.remove(random.choice([5,6]))
    # if 2 in respCodes:
    #   respCodes = [2]
    # if 4 in respCodes:
    #   respCodes = [4]
    
    #Given what tetermine what to do in each situation
    if respCodes == []: #no response codes were detected
      # print("EMPTY")
      responses.append(self.generator.askQuestion(self.gameState,userResponse))
      self.gameState.askedQuestion = True
    if 1 in respCodes: #User asked a question 
      responses.append(self.generator.addressQuestion(self.gameState, userResponse))
    if 2 in respCodes: #User asked who the caller was
      responses.append(self.generator.keyphraseTrigger(self.gameState, userResponse,"askedWhoTheCallerIs"))
      takeMultipleTurns = True
    if 3 in respCodes: #User greeted the caller
      responses.append(self.generator.keyphraseTrigger(self.gameState, userResponse,"greetedCaller"))
      takeMultipleTurns = True
    if 4 in respCodes: #User said goodbye 
      responses.append(self.generator.keyphraseTrigger(self.gameState, userResponse,"saidGoodbye"))
      self.gameState.goodbye = True
    if 6 in respCodes: #User used profanity
      responses.append(self.generator.addressProf(self.gameState, userResponse))
      takeMultipleTurns = True
    if 7 in respCodes: #User's response was nonsense
      responses.append(self.generator.fallback(self.gameState, userResponse))
      takeMultipleTurns = True
    if 9 in respCodes: #User's response was subjective
      responses.append(self.generator.addressSubj(self.gameState, userResponse))
      takeMultipleTurns = True
    if 10 in respCodes: #User had strong positive sentiment
      responses.append(self.generator.addressPositiveSentiment(self.gameState, userResponse))
      responses.append(self.generator.elizaTransformation(self.gameState, userResponse))
    if 11 in respCodes: # A dialog tag was identified in user response
      responses.append(self.generator.resolveObligation(self.gameState, userResponse))
    if 5 in respCodes: # User had strong negative sentiment
      responses.append(self.generator.addressNegativeSentiment(self.gameState, userResponse))
      responses.append(self.generator.elizaTransformation(self.gameState, userResponse))
      takeMultipleTurns = False
    if 8 in respCodes: #User avoided a question
      if self.gameState.avoidedQuestion > 1:
        self.gameState.avoidedQuestion = 0
        self.gameState.informationCount += 1
        responses.append(self.generator.askQuestion(self.gameState,userResponse))
      else:
        responses.append(self.generator.addressAvoidance(self.gameState, userResponse))
        if not takeMultipleTurns:
          responses.append(self.generator.askQuestion(self.gameState,userResponse))
        self.gameState.avoidedQuestion += 1
      #return [] <- uncomment for "Yield Floor" feature
    if 12 in respCodes: # User used some other language (not English)
      responses.append(self.generator.keyphraseTrigger(self.gameState, userResponse,"otherLanguage"))
      self.gameState.confused = True
    
    if takeMultipleTurns:
      responses.append(self.generator.askQuestion(self.gameState,userResponse))
      self.gameState.askedQuestion = True

    return responses
   
 
  '''
  Check if any of the end game conditions have triggered
  '''
  def checkEndGame(self):
    if self.gameState.getUnreadable() >= 15 and self.gameState.getInfoCount() >= 1:
      return True
    elif self.gameState.getUnreadable() >= 15:
      return True
    elif self.gameState.getInfoCount() >= 15:
      return True
    elif self.gameState.getLie() >= 10:
      return True
    elif self.gameState.getRude() >= 15:
      return True
    elif self.gameState.getConvo() >= 20:
      return True
    else:
      return False

  '''
  Decide how the game ends. 
  states:
    hangUp
    callPolice - depending on how much info we have, 
  '''
  def endGame(self, state = "undecided"):
    ending_key = ""
    now = datetime.now()
    str_time = now.strftime("%d/%m/%Y %H:%M:%S")

    # print("Ending game")
    if state == "hangUp":
      if self.gameState.confused:
        print("\nThe caller hangs up. I wonder what that was about...")
        ending_key += "<SPECIAL ENDING: Bilingual>"
      elif self.gameState.getConvo() <= 5: #they hang out on rounds 3,4,5
        print("\nYou hang up. I wonder what that was about...")
        ending_key += "<ENDING 1: Safe And Sound>"
      else: #they hang up after round 5
        print("\nYou hang up. I wonder what that was about...")
        self.dotdotdot()
        self.newsStory("user")
        ending_key += "<ENDING 2: Don't Be Rude>"
    elif state == "callPolice":
      print("\nYou hang up and dial 911...")
      if self.gameState.getInfoCount() >= 10 and self.gameState.getInfoCount() <= 13:
        self.dotdotdot()
        print("You called the police just in time! They were able to identify the caller and stop them before they do any harm! Congratulations!")
        ending_key += "<ENDING 3: Town Hero>"
      elif self.gameState.getInfoCount() < 10:
        self.dotdotdot()
        print("You called the police, but you didn't have enough information for them to be able to identify the caller. That suspicious person is still out there...")
        ending_key += "<ENDING 4: Looming Danger>"
      else:
        print("You reach the police and tell them about your conversation, but you may have been too late.")
        self.dotdotdot()
        if self.gameState.getGoal() == "User":
          self.newsStory("user")
          ending_key += "<ENDING 5: Too Late-You>"
        else:
          self.newsStory("friend")
          ending_key += "<ENDING 6: Too Late-Friend>"
    else:
      your_truth = input("\nHave you, at any point in the game, lied? ")
      print()
      if "yes" in your_truth.lower():
        self.gameState.lieCount = 10

      #unreadableCount reaches 7 and we have some information about the user
      if self.gameState.getUnreadable() >= 10 and self.gameState.getInfoCount() >= 1:
        print("\nThe caller hangs up.")
        self.dotdotdot()
        print("You hear your front door open...")
        self.dotdotdot()
        self.newsStory("user")
        ending_key += "<ENDING 7: Friendly Caller>"
      elif self.gameState.getUnreadable() >= 12:
        print("Caller > You better watch yourself. I know other ways of finding information")
        print("\nThe caller hangs up.")
        self.dotdotdot()
        print("You hear your front door open...")
        self.dotdotdot()
        self.newsStory("user")
        ending_key += "<ENDING 8: Not Too Safe>"
      elif self.gameState.informationCount >= 15:
        if self.gameState.getGoal() == "User":
          print("\nThe caller hangs up")
          self.dotdotdot()
          print("You hear your front door open...")
          self.dotdotdot()
          self.newsStory("user")
          ending_key += "<ENDING 9: No Privacy-You>"
        else:
          print("\nThe caller hangs up")
          self.newsStory("friend")
          ending_key += "<ENDING 10: No Privacy-Friend>"
      elif self.gameState.getLie() >= 10:
        print("Caller > Thank you for your time and all of this helpful information!")
        print("\nThe caller hangs up")
        self.dotdotdot()
        self.newsStory("stranger")
        ending_key += "<ENDING 11: Killer Helper>"
      elif self.gameState.getRude() >= 9:
        print("Caller > No need to be so rude. I have other ways of finding information anyways.")
        print("\nThe caller hangs up")
        self.dotdotdot()
        self.newsStory("stranger")
        ending_key += "<ENDING 12: Angry Caller>"
      #just for testing:
      elif self.gameState.getConvo() >= 25:
        print("Caller > Thank you for your time!")
        print("\nThe caller hangs up")
        self.dotdotdot()
        self.newsStory("user")
        ending_key += "<ENDING 13: Long Phone Call>"
      else:
        ending_key += "<ENDING 14: Error>"

    with open(self.achievement_path, 'a') as file:
      file.write(str_time+' '+ending_key+'\n')
    
    time.sleep(2)
    print("\n\n\n\n\nCongratulations! You have unlocked "+ending_key+'.\n\n\n\n\n')
  
  def dotdotdot(self):
    print(".")
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")
    time.sleep(1)

  def newsStory(self, whoDied):
    death_options = [
      "an anvil struck a young person at great speed.",
      "a young person was shot in their home.",
      "a young person was poisoned with arsenic.",
      "a wild tiger was released into a young person's home."
    ]
    
    print("A few days later, a short article appeared in the paper:")
    print("==================================================")
    print("One Dead After Suspicious Attack")
    today = date.today()
    print("Date:", today)
    print("\nOne person is dead after a suspicious accident occcurred last week where " + random.choice(death_options)+'\n')
    name = ""
    # print(self.gameState.information)
    if whoDied == "user":
      if 'user_name' in self.gameState.information:
        name = self.gameState.information['user_name']
    elif whoDied == "friend":
      if 'friend_name' in self.gameState.information:
        name = self.gameState.information['friend_name']
    
    if name == "":
      print("They were ruthlessly killed by an unknown person. Please beware any person who calls you and asks for personal information about you or your friends. If you have any information regarding this incident, please contact your local police station.")
    else:
      print(name + " was ruthlessly killed by an unknown person. Please beware any person who calls you and asks for personal information about you or your friends. If you have any information regarding this incident, please contact your local police station.")

    print("==================================================")

  '''
  Run the game!
  Take turns between the caller saying somethign and the user responding
  After 3 turns, offer hanging up
  After 10 turns, offer calling police
  '''
  def runGame(self):
    print("The phone rings. *ring**ring*. You pick up.")
    self.dotdotdot()
    print("Caller > Hello!")
    userResp = input("You > ")
    self.gameState.lastUserResponse = userResp
    while not self.checkEndGame():
      time.sleep(2)
      # print("\n--------------------------------------------\n")
      # print("Info count", self.gameState.informationCount)
      responses = self.respond(userResp)
      if responses == []: #user avoided a question, yield turn
        userResp = input("You > ")
        self.gameState.lastUserResponse = userResp
      else:
        # responses = ["My name is Clyde", "I like potatoes"]
        botResponse = ""
        for resp in responses:
          print("Caller >", resp)
          botResponse += resp
          botResponse += ". "
          time.sleep(2)
        self.gameState.lastBotResponse = botResponse
        
        if self.gameState.goodbye:
          return self.endGame("hangUp")

        if self.gameState.confused:
          return self.endGame("hangUp")

        if self.gameState.convoCount >= len(self.story):
          print("")
        else:
          small_story = self.story[self.gameState.convoCount]
          if small_story == "":
            print("")
          else:
            print("\n" + small_story + "\n")
        #Offer other options 
        if self.gameState.getConvo() >= 10: 
          print("A. Continue Talking, B. Hang Up, C. Call Police")
          choice = input("Which option would you like to choose? ")
          while choice not in ["A", "A.", "a", "a.", "B", "B.", "b", "b.", "C", "C.", "c", "c."]:
            choice = input("Not a valid option. Which option do you like to choose? ")
          if choice in ["B", "B.", "b", "b."]:
            return self.endGame("hangUp")
          elif choice in ["C", "C.", "c", "c."]:
            return self.endGame("callPolice")
        elif self.gameState.getConvo() >= 5:
          print("A. Continue Talking, B. Hang Up")
          choice = input("Which option would you like to choose? ")
          while choice not in ["A", "A.", "a", "a.", "B", "B.", "b", "b."]:
            choice = input("Not a valid option. Which option do you like to choose? ")
          if choice in ["B", "B.", "b", "b."]:
            return self.endGame("hangUp")

        #Let user respond
        userResp = input("You > ")
        self.gameState.lastUserResponse = userResp
        self.gameState.incrConvo()
    return self.endGame()

def main():
  os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
  os.environ['TRANSFORMERS_VERBOSITY'] = 'critical'

  yeses = ["Yes answers", "Affirmative non-yes answers", "Acknowledge (Backchannel)"]
  nos = ["No answers", "Negative non-no answers"]

  start = True
  while start:
    manager = Manager()
    manager.runGame()
    #Where the magic happens. Where the game is run

    see_ach = input("Your achievement has been added to ./dialogueSystem/achievement.txt. Would you like to see your past achievements? ")
    
    ach_look = manager.model.predict_tag(see_ach)
    # print('ACH: ', ach_look)
    # print(type(ach_look))

    # if "yes" in see_ach.lower():
    if ach_look in yeses:
      a_file = open(manager.achievement_path, encoding="utf8")
      lines = a_file.read().splitlines()
      print()
      for line in lines:
        print(line)

    restart = input("\nWould you like to start a new game? ")

    restart_look = manager.model.predict_tag(restart)
    # print('NEW GAME: ', restart_look)
    
    # if "yes" in restart.lower():
    if restart_look in yeses:
      pass
    else:
      start = False
      e_file = open('./dialogueSystem/credits.txt', encoding="utf8")
      lines = e_file.read().splitlines()
      print("\nThank you for playing our game. We hope you enjoyed your experience with MYSTERIOUS CALLER v.1.0. Bye bye. The mysterious caller eagerly awaits your next phone call.\n\n\n\n\n")
      for line in lines:
        print(line)

main()
  
    