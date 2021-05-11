import random
import re
# import sys

'''
The grammar notation that will be expected by this grammar engine is a text file: 

start -> <sym1> | <sym2>
sym1 -> apple | banana
sym2 -> car | I like bike <sym3>
sym3 -> paths

*STRICT RULES: (pls check your grammar txt files)
1) -> should have a single space before and a single space after
2) | should have a single space before and a single space before
3) blank lines between grammar rules are not allowed (if you want them to be allowed, I can add that later)
4) there should be no blank space inside a symbol/ variable name
'''

'''
For the toy grammar example,

The Grammar Engine self.grammar instance variable is like this:
  {
    "start": NonterminalSymbol object for start,
    "sym1": NonterminalSymbol object for sym1,
    "sym2": NonterminalSymbol object for sym2,
    "sym3": NonterminalSymbol object for sym3,
  }
 
The NonterminalSymbol objects look like this:
  NonterminalSymbol object for start:
    rules = [ProductionRule object 1, ProductionRule object 2]

  NonterminalSymbol object for sym1:
    rules = [ProductionRule object 3, ProductionRule object 4]

  NonterminalSymbol object for sym2:
    rules = [ProductionRule object 5, ProductionRule object 6]

  NonterminalSymbol object for sym3:
    rules = [ProductionRule object 7]

The ProductionRule objects look like this:
  ProductionRule object 1:
    head = NonterminalSymbol object for start
    body = [NonterminalSymbol object for sym1]

  ProductionRule object 2:
    head = NonterminalSymbol object for start
    body = [NonterminalSymbol object for sym2]
  
  ProductionRule object 3:
    head = NonterminalSymbol object for sym1
    body = ["apple"]

  ProductionRule object 4:
    head = NonterminalSymbol object for sym1
    body = ["banana"]
  
  ProductionRule object 5:
    head = NonterminalSymbol object for sym2
    body = ["car"]
  
  ProductionRule object 6:
    head = NonterminalSymbol object for sym2
    body = ["I like bike", NonterminalSymbol object for sym3]
  
  ProductionRule object 7:
    head = NonterminalSymbol object for sym3
    body = ["paths"]
'''
class GrammarEngine():
  grammar = {}
  runtime_variables = {}
  terminals = []
  nonterminals = []
  ''' - Allison
  Take in a text file, create grammar 
  Ellie is assuming for generate that there is an instance variable, self.grammar, that is a dictionary where the keys are the nonterminal symbol strings (not objects) and the values are NonterminalSymbol objects.
  '''
  def __init__(self, path_to_file):
    raw_grammar = self.get_grammar(path_to_file)
    self.grammar = self.grammarfy(raw_grammar)

  '''
    This is a simple 'go get file and open it' method.
  '''
  def get_grammar(self, path_to_file):
    raw_grammar = ""
    f = open(path_to_file)
    with f:
      raw_grammar = f.readlines()
    return raw_grammar

  '''
    The final structure for 'self.grammar' is pretty complicated. See Ellie's example above. This method takes in lines of the input text file to make that. 

    General strat: grab all production rules with terminal symbols (new terminal symbol, production rules) -> if there is a production rule with a terminal symbol, replace its spot with a 'found' terminal symbol object (only replace and add new production rule if ALL terminal symbols within that rule have already been found)
  '''
  def grammarfy(self, raw_grammar):
    my_grammar = {}
    have_nonterms = {} # name : [[og string, [nonterms]]...]
    for raw_line in raw_grammar:
      sides = raw_line.split(' -> ')
      left_side = sides[0] # key
      if left_side not in my_grammar:
        # create all nonterminal symbols here
        # -> access through my_grammar and expand rules later on
        left_symbol = NonterminalSymbol(left_side) # value
        my_grammar[left_side] = left_symbol
      # now put production rules into left_symbol.rules
      
      right_side = sides[1]
      # weird newline stuff fixed here
      right_side = right_side.replace('\\n', '\n')
      right_nexts = right_side.split(' | ')
      # make different product rule objects
      product_rules = [x.strip() for x in right_nexts]
      for raw_rule in product_rules:
        
        if raw_rule not in self.terminals:
          self.terminals.append(raw_rule)
        nonterms = re.findall(r"\<([A-Za-z0-9_ ]+)\>", raw_rule)
        
        if len(nonterms) == 0: # string type
          new_rule = ProductionRule(left_symbol)
          body = []
          body.append(raw_rule)
          new_rule.body = body
          left_symbol.rules.append(new_rule)
        else: # there are non terminal symbols
          if left_side in have_nonterms:
            have_nonterms[left_side].append([raw_rule, nonterms])
          else:
            have_nonterms[left_side] = []
            have_nonterms[left_side].append([raw_rule, nonterms])
    # fill in missing rules (ones with nonterms)
    while len(have_nonterms.keys()) != 0:
      have_nonterms, my_grammar = self.fill_nonterms(have_nonterms, my_grammar)
    self.nonterminals = []
    for i in my_grammar:
      self.nonterminals.append(my_grammar[i].toString()) 
    return my_grammar
  
  '''
    This is a helpful print method to check what's going on in 'grammar' (dict). You can use it for testing.
  '''
  def check_grammar(self, my_grammar):
    for i in my_grammar:
      print(my_grammar[i].toString()) 
      # j is a nonterminal symbol
      for j in my_grammar[i].getRules():
        # rules
        print(j.body)

  '''
    The production rules are built bottom-up: string terminal symbols first -> nonterminal ones. So, rules with terminal symbols in them will be filled out later. This method does that iff all nonterminal symbols within the rule have been found.
  '''
  def fill_nonterms(self, have_nonterms, my_grammar, check=False):
      if check: # testing
        self.check_grammar(my_grammar)
      temp_nonterms = {}
      for left_side in have_nonterms:
        to_keep = []
        for i in range(0, len(have_nonterms[left_side])):
          missing = have_nonterms[left_side][i]
          raw_rule = missing[0]
          nonterms = missing[1]
          if all(x in my_grammar for x in nonterms):
            new_rule = ProductionRule(left_side)
            # all nonterms have been found, so we can fill in everything yay
            raw_splits = re.split('<|>', raw_rule)
            splits = list(filter(None, raw_splits))
            temp_splits = splits.copy()
            for j in range(0, len(splits)):
              some_split = splits[j]
              if some_split in nonterms:
                temp_splits[j] = my_grammar[some_split]
            new_rule.body = temp_splits
            # update grammar dict
            my_grammar[left_side].rules.append(new_rule)
          else:
            to_keep.append(have_nonterms[left_side][i])
        if len(to_keep) != 0: # leave only unfound nonterms by returning updated version
          temp_nonterms[left_side] = to_keep
      # if there is a rule missing in the text file, we will end up going in an infinite loop. To prevent that, we want to make sure have_nonterms has actually been updated! -> (()) strat
      if have_nonterms == temp_nonterms:
        my_grammar = self.fill_norule(have_nonterms, my_grammar)
        temp_nonterms = {}
        # sys.exit("*BIG SIGH* you're missing a rule in your txt file")
      return temp_nonterms, my_grammar

  '''
    We aren't perfect, so we'll make mistakes sometimes. If we forget to write a rule for a nonterminal symbol, the symbol is replaced with a ((symbol_name)).
  '''
  def fill_norule(self, have_nonterms, my_grammar):
    for left_side in have_nonterms:
      for i in range(0, len(have_nonterms[left_side])):
        missing = have_nonterms[left_side][0]
        raw_rule = missing[0]
        nonterms = missing[1]

        new_rule = ProductionRule(left_side)
        # not all nonterms have been found, but we will just replace with sample string in (()) format
        raw_splits = re.split('<|>', raw_rule)
        splits = list(filter(None, raw_splits))
        temp_splits = splits.copy()
        for j in range(0, len(splits)):
          some_split = splits[j]
          if some_split in nonterms and some_split in my_grammar:
            temp_splits[j] = my_grammar[some_split]
          elif some_split in nonterms:
            temp_splits[j] = '(('+some_split+'))'
        new_rule.body = temp_splits
        my_grammar[left_side].rules.append(new_rule)
    return my_grammar


  def get_nonterminals(self, path_to_file):
    raw_grammar = self.get_grammar(path_to_file) 
    self.grammarfy(raw_grammar)
    return self.nonterminals

  def get_terminals(self, path_to_file):
    raw_grammar = self.get_grammar(path_to_file) 
    self.grammarfy(raw_grammar)
    return self.terminals

  ''' - Ellie
  Algorithm:
  while there is at least one nonterminal symbol in the intermediate output, rewrite the leftmost nonterminal symbol in that intermediate output; once you have only terminal symbols (strings), concatenate them to form your final output. There’s many ways that one could implement this algorithm, but I personally recommend a recursive procedure.
  '''
  def generate(self, start_symbol):
    generated_text = ""
    result = self.generate_helper(start_symbol, generated_text, False)
    if result[0] ==" ":
      return result[1:]
    return result

  def generate_helper(self, start_symbol, generated_text, prequote):
    symbol = self.grammar[start_symbol]
    production_rules = symbol.getRules()
    chosen_rule = random.choice(production_rules)
    rule_body = chosen_rule.getBody()
    for item in rule_body:
      # print("Currently, prequote is:", prequote)
      # print("New Item:", item)
      
      if type(item) == str:

        #I'm not sure why the Prequote mechanism doesn't always work, but here is an edge case we have to take care of
        if len(item)>1 and item[0] == '"' and item[1] == " " and generated_text[-1] == " ":
          generated_text = generated_text[0:-1]

        if '%' in item:
          updated = ""
          words = item.split()
          #if the first character in words is a punctuation or if the last character in generated text was a quotation, do not add a space to start 
          if not self.isPunc(words[0]) and not prequote:
            updated = " "
          for word in words:
            if word[0] == '%' and word[-1] == '%':
              var_name = word[1:-1]
              if var_name in list(self.runtime_variables.keys()):
                updated += self.runtime_variables[var_name]
                if updated[-1] != '"':
                  updated +=" "
              else: #that runtime variable hasnt been called yet
                updated += "[[" + var_name + "]]"
                updated +=" "
            elif word[0] == '%' and word[-2] == '%':
              var_name = word[1:-2]
              if var_name in list(self.runtime_variables.keys()):
                updated += self.runtime_variables[var_name]
                updated += word[-1]
                if updated[-1] != '"':
                  updated +=" "
              else: #that runtime variable hasnt been called yet
                updated += "((" + var_name + "))" 
                updated += word[-1]
                updated +=" "
            else:
              updated += word
              if updated[-1] != '"':
                updated +=" "
          
          generated_text = generated_text + updated
          if item[-1] == '"':
            prequote = True
          else:
            prequote = False
        else:
          generated_text += item
          if item[-1] == '"':
            prequote = True
          else:
            prequote = False
      else: #if type(item) == NonterminalSymbol
        # print("RECurse!,", prequote)
        generated_text = self.generate_helper(item.name, generated_text, prequote)
    return generated_text

  def isPunc(self, word):
    # !"#$%&'()*+, -./:;<=>?@[\]^_`{|}~
    if word == "." or word == "!" or word == "?" or word == "," or word == '"' or word == "'" or word == "-":
      return True
    else:
      return False

  def find(self, symbol_name):
    return self.grammar[symbol_name]

  '''
  To allow for the setting of runtime variables, create a method of your grammar engine called set_variable(), which accepts a key and a value.
  '''
  def set_variable(self, key, value):
    self.runtime_variables[key] = value
    return ""

''' - Rie
Each NonterminalSymbol object will have a rules instance variable, which stores a list of ProductionRule objects associated with the nonterminal symbol.
'''
class NonterminalSymbol():
  def __init__(self, name):
    self.name = name
    self.rules = []

  # def rewrite(self):
  #   production_rule = random.choice(self.rules)
  #   return production_rule.body

  def getRules(self):
    return self.rules

  def toString(self):
    return self.name


''' - Starr
Each ProductionRule object will have a head instance variable, which stores the NonterminalSymbol object associated with the symbol on the left-hand side of the rule, and a body instance variable, which stores the body of the rule (i.e., the right-hand side of the rule); the body should be represented as a list of NonterminalSymbol objects and strings (the latter being the terminal symbols).
eg."<food1>": ["salads", "vegetable", <meat>] 
   "<meat>" : ["chicken", "beef"]   
head = food1
body = ["salads", "vegetable", meat]
'''
class ProductionRule():

  def __init__(self, head):
    self.head = head
    self.body = []

  def getBody(self):
    return self.body
