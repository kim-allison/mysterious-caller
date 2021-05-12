import random 

class GameState:

  def __init__(self):
    self.information = {}
    self.unreadableCount = 0
    self.informationCount = 0
    self.lieCount = 0
    self.rudeCount = 0
    self.convoCount = 0
    self.goodbye = False
    self.confused = False
    self.goal = random.choice(["User", "Friend", "Friend"]) 
    # oh lol

    # whether the bot just asked a question
    self.askedQuestion = False
    self.newInfo = ""
    self.avoidedQuestion = 0

    # type of DialogueAct question
    self.questionActType = ""

    '''
    The actual text 
    '''
    lastBotResponse = ""
    lastUserResponse = ""
  
  def getGoal(self):
    return self.goal

  def new_information(self, info_type, info):
    self.information[info_type] = info
    self.informationCount += 1

  def getInfoCount(self):
    return self.informationCount

  def getUnreadable(self):
    return self.unreadableCount
  
  def incrUnreadable(self):
    self.unreadableCount += 1

  def incrLie(self):
    self.lieCount += 1

  def getLie(self):
    return self.lieCount

  def incrRude(self):
    self.rudeCount += 1

  def getRude(self):
    return self.rudeCount
  
  def incrConvo(self):
    self.convoCount += 1

  def getConvo(self):
    return self.convoCount

  def botResponse(self, newResp, tag):
    self.lastBotResponse = newResp
    self.lastBotResponseTag = tag

  def userResponse(self, newResp, tag):
    self.lastUserResponse = newResp
    self.lastUserResponseTag = tag
