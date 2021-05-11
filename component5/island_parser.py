from recursive_descent_parser import RecursiveDescentParser
from grammar_engine import GrammarEngine

import re


'''
(S 
  (NP 
    (PropN Joe)
  ) 
(VP (V said) (S (NP (PropN Buster)) (VP (V ghosted) (NP (PropN Schiller)))))
)

parameters: string = text you want to parse
            grammar = txt file that holds the grammar 
'''
class IslandParser:
  def __init__(self, grammar):
    self.string = ""
    self.words = []
    self.engine = GrammarEngine(grammar)
    self.RDP = RecursiveDescentParser(self.engine, False)

    self.nonterminals = self.engine.get_nonterminals(grammar)
    self.terminals = self.engine.get_terminals(grammar)


  '''
    Can be given a list of nonterminals (if not, uses default)
    Returns a tuple of island parses, each of which is a list of partial parses of the object's words. 

    Starting at the number of tokens, n, in the string it wants to parse and successively decreasing by 1, looks at all the n-length substrings of the string. Attempts to parse each one. If able, it adds it to a partial parse, then continues on. 
  '''
  def parse(self, string):
    # self.string = string + " "
    # string = string + " ENDS"
    puncts = [",", ".", "!"]
    # words = string.split(" ")
    self.words = re.findall(r"[\w']+|[.,!?;]", string)
  
    #False until it finds the largest thing it can parse
    biggest_parse = False
    #the partial parses - ends up being a list of lists. Each inner list is one partial parse
    partial_parses = []
    #the tokens that make up each partial parse - a list of lists
    partial_parses_tokens = []
    #the indices of the tokens that make up each partial parse - a list of lists
    partial_parses_indices = []

    symbols = self.nonterminals
    for i in range(len(self.words), 1, -1):
      # print(self.words)
      token_lists = self.substringsFilterNotInGrammar(self.words, i)
      # print(token_lists)
      biggest_parse_this_level = False
      for token_and_indices in token_lists:
        token = token_and_indices[0]
        # print("i", i)
        # print(token)
        indices = token_and_indices[1]
        for symbol in symbols:
          # print(symbol)
          parse = self.RDP.parse(token, symbol)
          # print(parse)
          if parse != None:
            if not biggest_parse:
              temp = [parse]
              partial_parses.append(temp)
              # partial_parses_tokens.append(token.split(" "))
              partial_parses_tokens.append(re.findall(r"[\w']+|[.,!?;]", token))
              partial_parses_indices.append(indices)
              biggest_parse_this_level = True
            else:
              # little_tokens = token.split(" ")
              little_tokens = re.findall(r"[\w']+|[.,!?;]", token)
              parse_num = 0
              for par in partial_parses_tokens:
                new_tokens = True
                for partial in par:
                  for index in indices:
                    if index in partial_parses_indices[parse_num]:
                      new_tokens = False
                if new_tokens:
                  # new_tokens_list = token.split(" ")
                  new_tokens_list = re.findall(r"[\w']+|[.,!?;]", token)
                  temp_parses = partial_parses[parse_num].copy()
                  temp_parses.append(parse)
                  temp_parses_tokens = partial_parses_tokens[parse_num].copy()
                  temp_parses_indices = partial_parses_indices[parse_num].copy()
                  for x in new_tokens_list:
                    temp_parses_tokens.append(x)
                  for index in indices:
                    temp_parses_indices.append(index)
                  partial_parses.append(temp_parses)
                  partial_parses_tokens.append(temp_parses_tokens)
                  partial_parses_indices.append(temp_parses_indices)
                parse_num = parse_num + 1
        
        #if all tokens have been parsed
        all_tokens_parses = []
        x = 0
        all_parsed = False
        for tokensList in partial_parses_tokens:
          if len(tokensList) == len(self.words):
            all_tokens_parses.append(partial_parses[x])
            all_parsed = True
          x += 1
        if all_parsed:
          final_parses = []
          x = 0
          minParses = min(len(parse) for parse in all_tokens_parses)
          for parse in all_tokens_parses:
            if len(parse) == minParses:
              final_parses.append(parse)
            x += 1
          # print("Done early")
          if len(final_parses) > 1:
            largest_length = -float('inf')
            largest_parse = []
            for final_parse in final_parses:
              if final_parse[0].count("(") > largest_length:
                largest_length = final_parse[0].count("(")
            for final_parse in final_parses:
              if final_parse[0].count("(") == largest_length:
                largest_parse.append(final_parse)
            return tuple(largest_parse), True
          return final_parses, True
            
        if biggest_parse_this_level:
          biggest_parse = True 
      


    if partial_parses == []:
      # print("There are no possible partial parses for the given string and grammar. Please ensure that there is white space around each token")
      return (), False
    #do something to choose which partial parses to return 
    #only consider parses with the most tokens parsed
    maxTokens = max(len(parse) for parse in partial_parses_tokens)
    # print("MAX TOKENS", maxTokens)
    parse_num = 0
    pre_final_parses = []
    for parse in partial_parses_tokens:
      if len(parse) == maxTokens:
        pre_final_parses.append(partial_parses[parse_num])
      parse_num += 1

    #only consider parses from the previous set that have the minimum islands
    final_parses = []
    parse_num = 0
    minParses = min(len(parse) for parse in pre_final_parses)
    for parse in pre_final_parses:
      if len(parse) == minParses:
        final_parses.append(pre_final_parses[parse_num])
      parse_num += 1

    if len(final_parses) > 1:
      largest_length = -float('inf')
      largest_parse = []
      for final_parse in final_parses:
        if final_parse[0].count("(") > largest_length:
          largest_length = final_parse[0].count("(")
      for final_parse in final_parses:
        if final_parse[0].count("(") == largest_length:
          largest_parse.append(final_parse)
      return tuple(largest_parse), True
    return tuple(final_parses), True


  #only returns strings of length substring_length that have words that are in the grammar's terminals
  #returns a list of tuples, where each tuple contains the token phrase and a list of indices of each token in the phrase ("phrase", [indices])
  def substringsFilterNotInGrammar(self, words, substring_length):
    terminals = []
    for terminal in self.terminals:
      for splitted_terminal in terminal.split(" "):
        if "<" not in splitted_terminal:
          terminals.append(splitted_terminal)
    # print(terminals)
    tokens_and_indices = []
    i = 0
    while i+substring_length <= len(words):
      temp = words[i:i+substring_length]
      add = True
      for word in temp:
        if word not in terminals:
          add = False
      if add:
        string = " ".join(temp)
        string = re.sub(r' ([^A-Za-z0-9])', r'\1', string)
        indices = []
        for x in range(i, i+substring_length):
          indices.append(x)
        tokens_and_indices.append((string, indices))
      i +=1
    # print(tokens_and_indices)
    return tokens_and_indices
