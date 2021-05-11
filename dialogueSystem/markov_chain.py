import re
import random
import operator
from collections import defaultdict
import statistics
import sys

'''
import spacy
# Load the standard English model suite
nlp = spacy.load("en_core_web_sm")
# Prepare a corpus
corpus = "Where is Schiller currently located?"
# Update the model suite to allow for a long corpus
nlp.max_length = len(corpus)
# POS-tag the corpus
with nlp.select_pipes(enable=["tok2vec", "tagger"]):
    tagged_tokens = nlp(corpus)
# Print out the tagged tokens
for token in tagged_tokens:
    print(f"{token}/{token.tag_}")
'''

class MarkovChain:
  token_list = [] # list of tokens
  frequency_dict = {} # keys are tuples of tokens, values are count of times the first token is followed by the second
  transitions = {} # keys are tokens, values are sets of probability tuples 
  # text_likelihood = 0
  
  test_mean = 0
  test_stdev = 0

  def __init__(self, corpus, level, order):
    self.level = level # character or word
    self.order = order # size of n-grams
    self.corpus = corpus # text used to train model

    try:
      f = open(self.corpus)
    except OSError:
      print("BAD")
      sys.exit()

    with f:
      self.token_list = self.tokenize(f.read())

    self.frequency_dict = self.gen_frequencies(self.token_list)
    self.transitions = self.train(self.frequency_dict)
    self.gen_estimator()
  
  '''
    This is our tokenizer. The tokenizer either tokenizes the textfile into word tokens or character tokens.
  '''
  def tokenize(self, lines):  
    return self.tokenize_text(lines)

  '''
    This is a helper method for our tokenizer. It tokenizes a LONG string.
  '''
  def tokenize_text(self, text):
    tokens = []
    if self.level == "word":
      tokens = re.findall(r'[\"\'\-\n\w]+|[.,!?;\"\'\-\n]+|\'', text)
      # print(re.split('\s|[.,!?;]', text))
      # print(re.findall(r'\w*\" | \"\w* | [.,!?;]*\"', text))
      # print("Test regex:")
      # print(re.findall(r'[\"\'\-\w]+|[.,!?;\"\'\-]+', text))

      # tokens = re.findall(r'[-\'\w | \"=\w]+|[.,!?; | ?+\"]|[\n\t]', text)
      # so punctuations (included '-'), \n, \t, and words ONLY (no "" space)
    elif self.level == "character":
      tokens = list(text)
      # so punctuations (including -), \n, (don't know about \t yet), "" space, and characters ONLY
    else:
      print("Sorry, that file doesn't exist.")
      sys.exit()
    return tokens

  def is_special_character(self, word):
    return re.match('[.,!?;\n]', word)

  '''
    This methods create n-gram keys based on the token value (whether punctuation or word).
  '''
  def create_n_gram(self, index, tokens):
    n_gram = ""
    for i in range(index, index+self.order):
      # add empty space if token 1) is a word, 2)is not a specical character, or 3) is not the first word
      if self.level=="word" and not self.is_special_character(tokens[i]) and len(n_gram) != 0:
        n_gram+=" "

      n_gram+=tokens[i]

    return n_gram

  '''
    This method computes frequencies of (n_gram, token) pairs.

    @return frequency_dict: a nested dictionary
     key: n_gram, 
     value: another dictionary {key: token, value: frequency}
     eg. {'ab' : {'c': 1, 'd': 2...}, 'bc': {'a':1 ...} ..}
  '''
  def gen_frequencies(self, tokens): 
    freq_count = {} 
    # for each possible pair of (n-gram, token):
    for i in range(0, len(tokens)-self.order):
      n_gram = self.create_n_gram(i, tokens) 
      token = tokens[i+self.order]
      # if the n_gram not exist in freq_count, create a new dict for this n_gram, add it to freq_count
      if n_gram not in freq_count:
        freq_count[n_gram] = {}
      # if the next n_gram not exist in dict, create a new dict
      if token not in freq_count[n_gram]:
        freq_count[n_gram][token] = 0
      # increment the frequency
      freq_count[n_gram][token]+=1
    return freq_count

  '''
    This method uses our freqency calculations to generate transitions within a Markov Chain (aka make the model).
  '''
  def train(self, frequencies):
    transitions = defaultdict(list)
    # tokens = self.token_list
    tokens = frequencies.keys()
    # print(frequencies)
    for t in tokens:
      values = []
      # get the dictionary of the following characters/words and frequencies
      freqT = frequencies[t]
      # sort the dictionary in descending order
      sorted_freqT = dict(sorted(freqT.items(), key=operator.itemgetter(1),reverse=True))
      # get the total number of the token to appear
      total = 0
      for value in sorted_freqT.values():
        total += value
      # calculate the probability and add it to the values list
      lower, upper = 0, 0
      for key, value in sorted_freqT.items():
        probability = value / total
        # probability = round((value / total), 2) #rounded version
        upper += probability
        values.append((key, (lower, upper)))
        lower = upper
      transitions[t] = values
    # self.transitions = transitions
    return transitions


  def newline(self):
    print("Hello!")
    newline_dict = self.transitions.get("\n")
    print(newline_dict)

  def generate(self, length, prompt=""):
    if prompt == "": #no prompt given
      prompt = random.choice(list(self.transitions.keys()))
    else: #prompt was provided
      prompt = self.screen_prompt(prompt)
      

    #TODO: else if the prompt is too short or too long 

    if self.level == "character":
      return self.generate_character(length, prompt)
    else:
      # print("Prompt", prompt)
      while len(self.init_lengths_list(prompt)) != self.order:
        # print(prompt)
        # print(self.init_lengths_list(prompt))
        # print("Our models is not able to accept that prompt. One will be chosen randomly")
        prompt = random.choice(list(self.transitions.keys()))
      return self.generate_word(length, prompt)

  def generate_character(self, length, prompt):
    generated = prompt
    prev = prompt
    tokens = self.order
    # print(self.transitions)
    #print(list(self.transitions.keys()))
    # print("START:", prompt)
    while tokens < length:
      chosen_token = ''
      if prev not in list(self.transitions.keys()): 
        #should only happen when the prev is the last ngram in the corpus, which was also unique. AKA very rarely
        # print("EDGE CASE:", prev)
        #make a new line, randomly choose a place to start, and continue
        chosen_token = '\n'
        new_prompt = random.choice(list(self.transitions.keys()))
        generated = generated + chosen_token + new_prompt
        prev = new_prompt
       
      else:
        possible_transitions = self.transitions.get(prev)
        chosen_token = self.probabilistically_chose(possible_transitions)
        #add to generated
        generated += chosen_token
        #update prev ngram 
        prev += chosen_token
        prev = prev[1:]

      tokens += 1

    return generated 

  def generate_word(self, length, prompt):
    generated = prompt
    prev = prompt
    prev_lengths_list = self.init_lengths_list(prompt)

    tokens = self.order
    # print("START:", prompt)
    # print(list(self.transitions.keys()))
    while tokens < length:
      chosen_token = ''
      if prev not in list(self.transitions.keys()): 
        #should only happen when the prev is the last ngram in the corpus, which was also unique. AKA very rarely
        # print("EDGE CASE:", prev)
        #make a new line, randomly choose a place to start, and continue
        chosen_token = '\n'
        new_prompt = random.choice(list(self.transitions.keys()))
        generated = generated + chosen_token + new_prompt
        prev = new_prompt
        prev_lengths_list = self.init_lengths_list(prev)
        # token_was_quote = False
      else: 
        possible_transitions = self.transitions.get(prev)
        chosen_token = self.probabilistically_chose(possible_transitions)

        if self.is_special_character(chosen_token):
          generated += chosen_token
          #update prev ngram
          prev += chosen_token
        # elif token_was_quote:
        #   generated += chosen_token
        #   #update prev ngram
        #   prev += chosen_token
        #   token_was_quote = False
        else: 
          #add to generated
          generated += " "
          generated += chosen_token
          #update prev ngram 
          prev += " "
          prev += chosen_token

        # print('generated2:', generated)

        #remove the oldest word
        oldest_length = prev_lengths_list[0]
        prev = prev[oldest_length:]

        #add the new token's length
        prev_lengths_list.append(len(chosen_token))
        #remove the oldest token's length
        prev_lengths_list = prev_lengths_list[1:]

        if prev[0] == " ": #if it was followed by a space, strip it. Otherwise, theres a punctuation there we do not want to remove
          prev = prev[1:]
        
        # if chosen_token == '"':
        #   token_was_quote = True
                
      tokens += 1

    return generated

  '''
      NOTES: given a list of the transition probabilities for a single n-gram, probabilistically chooses which should come next 
  '''
  def probabilistically_chose(self, probabilities):
    rand = random.uniform(0,1)
    chosen_token = ""
    for transition in probabilities:
        prob_range = transition[1]
        if rand >= prob_range[0] and rand < prob_range[1] :
            chosen_token = transition[0]

    if chosen_token == "":  
      #a rounding error occured, choose the last transition
      chosen_token = probabilities[-1][0]
      #print("Something went wrong when trying to chose something from " + str(probabilities) + " using " + str(rand)+ " but its okay we chose " + chosen_token)
    return chosen_token
      
  def init_lengths_list(self, prompt):
    prompt_list = prompt.split() #prervious ngram with punctuation separated out
    temp_list = []
    for ngram in prompt_list:
      if self.is_special_character(ngram[0]): #first character is punctuation
        temp_list.append(1)
      elif self.is_special_character(ngram[-1]):#last character is punctuation
        temp_list.append(len(ngram[:-1]))
        temp_list.append(1)
      else:
        temp_list.append(len(ngram))
    
    return temp_list    

  def screen_prompt(self, prompt):
    if self.level == "character":
      if len(prompt) < self.order: #prompt too short
        for key in list(self.transitions.keys()):
          if key[-len(prompt):] == prompt: #if the last n letters are the prompt
            print("The prompt you provided was too short, so our model added to it. \n")
            print("chosen prompt1", key)
            return key
        for key in list(self.transitions.keys()): 
          #if no key ended in the provided prompt, check if any key contains the provided prompt
          if prompt in key: #if the last n letters are the prompt
            print("The prompt you provided was too short, so our model added to it. \n")
            return key
        #if both those fail, choose randomly
        prompt = random.choice(list(self.transitions.keys()))
        print("The prompt you provided is not in the corpus, so our model chose a random prompt. \n")
      elif len(prompt) > self.order: #prompt too long
        prompt = prompt[-self.order:] 
        print("The prompt you provided was too long, so our model shortened it and only used the last " + str(self.order) + " characters. \n")
      elif len(prompt) == self.order and prompt not in list(self.transitions.keys()): #prompt right length but not in corpus
        prompt = random.choice(list(self.transitions.keys()))
        print("The prompt you provided is not in the corpus, so our model chose a random prompt. \n")
      else:
        print("prompt approved!")
    else: #level is word
      prompt_length_list = self.init_lengths_list(prompt)
      num_tokens = len(prompt_length_list)
      #print("num tokens", num_tokens)
      if num_tokens < self.order:
        #print("Too short")
        for key in list(self.transitions.keys()): 
          #if no key ended in the provided prompt, check if any key contains the provided prompt
          if prompt in key: 
            print("The prompt you provided was too short, so our model added to it. \n")
            return key
        #if both those fail, choose randomly
        prompt = random.choice(list(self.transitions.keys()))
        print("The prompt you provided is not in the corpus, so our model chose a random prompt. \n")
      elif num_tokens > self.order:
        for i in range(num_tokens):
          temp_lengths = self.init_lengths_list(prompt)
          if prompt in list(self.transitions.keys()): #it matches a key
            print("The prompt you provided was too long, so our model shortened it. \n")
            return prompt
          else:
            prompt = prompt[prompt_length_list[i] + 1:]
        prompt = random.choice(list(self.transitions.keys()))
        print("The prompt was too long and our model was not able to shorten it, so our model chose a random prompt. \n")
      elif num_tokens == self.order and prompt not in list(self.transitions.keys()): #prompt right length but not in corpus
        prompt = random.choice(list(self.transitions.keys()))
        print("The prompt you provided is not in the corpus, so our model chose a random prompt. \n")
      else:
        print("prompt approved!")
    return prompt

  '''
    This method calculates the likelihood for given set of tokens (text) and transitions. Z-scores are normalized using the number of tokens of input text.
  '''
  def gen_likelihood(self, text_tokens, transitions):
    text_likelihood = 0
    for i in range(self.order, len(text_tokens)):
      key = "" # the n-gram
      value = text_tokens[i]
      for j in range(0, self.order):
        key_token = text_tokens[i-(self.order-j)]
        if not self.is_special_character(key_token) and len(key) != 0:
          key += " "
        key += text_tokens[i-(self.order-j)]
      # print(key)
      if key in transitions and value in dict(transitions[key]):
        prob_range = dict(transitions[key])[value]
        # print('&' + key + '&')
        # CHECK THIS:
        text_likelihood += (prob_range[1]-prob_range[0])
      # else: # not happening = 0
    return text_likelihood/len(text_tokens)

  # def gen_text_likelihood(self, text):
  #   text_tokens = self.tokenize_text(text)
  #   text_likelihood = self.gen_likelihood(text_tokens, self.transitions)
  #   self.text_likelihood = text_likelihood    

  '''
    This method creates our estimator, which is composed of mean and standard deviation calculations of probabilities of sample sentences in a test set tested against a training set.
  '''
  def gen_estimator(self):
    # 1) training set (first half)
    train_tokens = self.token_list[:len(self.token_list)//2] # take half of token_list (already tokenized)
    frequencies = self.gen_frequencies(train_tokens) 
    transitions = self.train(frequencies)

    # 2) test set (the remaining half)
    test_tokens = self.token_list[len(self.token_list)//2:] # split into sentences of length n (length of text)
    # print(test_tokens)
    n = 75 #selected sentence length
    chunks = [test_tokens[i:i + n] for i in range(0, len(test_tokens), n)]
    # print(chunks)
    all_likelihood = [self.gen_likelihood(i, transitions) for i in chunks]
    # print(all_likelihood)

    # 3) get test values
    self.test_mean = sum(all_likelihood) / len(all_likelihood)
    self.test_stdev = statistics.stdev(all_likelihood)
    # z_score = abs((self.text_likelihood - mean) / stdev)
    # return z_score

  '''
    This method calculates the z-score of an input text against the model's estimator.
  '''
  def estimate(self, text):
    text_tokens = self.tokenize_text(text)
    text_likelihood = self.gen_likelihood(text_tokens, self.transitions)
    # print('text: ', text_likelihood, '\nmean: ', self.test_mean,'\nstdev: ', self.test_stdev)
    z_score = (text_likelihood - self.test_mean) / self.test_stdev
    return z_score