# from recursive_descent_parser import RecursiveDescentParser
from island_parser import IslandParser
from grammar_engine import GrammarEngine
import re
import string

name_grammar = './component5/name_grammar.txt'
# engine = GrammarEngine(name_grammar)

test_name0 = "Hi, my name is Allison. Who is this?"
test_name1 = "Um...who is this?"
test_name2 = "This is Allison."
test_name3 = "This is Allison Kim."
test_name4 = "My name is Allison."
test_name5 = "Allison"

# start = "name_act"

# recursive_parser = RecursiveDescentParser(engine, False)
'''
IP = IslandParser(name_grammar)
parse_tree0, tree_check0 = IP.parse(test_name0)
print("\nNAME0:", parse_tree0, tree_check0)
parse_tree1, tree_check1 = IP.parse(test_name1)
print("\nNAME1:", parse_tree1, tree_check1)
parse_tree2, tree_check2 = IP.parse(test_name2)
print("\nNAME2:", parse_tree2, tree_check2)
parse_tree3, tree_check3 = IP.parse(test_name3)
print("\nNAME3:", parse_tree3, tree_check3)
parse_tree4, tree_check4 = IP.parse(test_name4)
print("\nNAME4:", parse_tree4, tree_check4)
'''

# if tree_check is False, the caller cannot recognize the player's name (we can use name_act in combination with NER tags -- PERSON) -> caller anger level +1

# if tree_check is True, we know that the token that comes afterwards must be a name <name_act> NAME.
# 1) tokenize input string to get NAME
# 2) but first get the last token that is included in the parse tree_check

# names are NER-applicable and are relatively easy
# let's try another example:

bot_slots = {"friend":"Rie"}
print("Caller: What do you usually do with " + bot_slots["friend"])
# assuming you mentioned Rie and the mystertious caller is now trying secretly get more information about her from you (what she does/ where she usually is/ etc) -- so at least one slot in full

action_grammar = './component5/action_grammar.txt'

test_action0 = "We like to go get icecream."
test_action1 = "Why are you asking that?"
test_action2 = "Hm...I enjoy playing Animal Crossing with her."
test_action3 = "Usually we do NLP homework together...haha"
test_action4 = "Um? That's creepy, but we sometimes eat dinner together."

IP = IslandParser(action_grammar)
parse_tree0, tree_check0 = IP.parse(test_action0)
print("\nACTION0:", parse_tree0, tree_check0)
parse_tree1, tree_check1 = IP.parse(test_action1)
print("\nACTION1:", parse_tree1, tree_check1)
parse_tree2, tree_check2 = IP.parse(test_action2)
print("\nACTION2:", parse_tree2, tree_check2)
parse_tree3, tree_check3 = IP.parse(test_action3)
print("\nACTION3:", parse_tree3, tree_check3)
parse_tree4, tree_check4 = IP.parse(test_action4)
print("\nACTION4:", parse_tree4, tree_check4)

tokens0 = test_action0.split()
tree0 = re.findall('\(.*?\)', parse_tree0[0][0])[0]
indexes = [index for index, element in enumerate(tree0) if element == '(']
first_tree0 = tree0[indexes[len(indexes)-1]:]
# print(tokens0)
first_tokens0 = first_tree0.split()
first_token0 = first_tokens0[len(first_tokens0)-1][:-1]
action0 = tokens0[tokens0.index(first_token0)+1:]
string_action0 = " ".join(action0)
bot_slots["friend_action"] = string_action0
# .translate(string.punctuation)
IP.engine.set_variable("friend_action", bot_slots["friend_action"])