from dialog_tag import DialogTag
model = DialogTag('distilbert-base-uncased')

sentence = "I'll probably go to shopping today."
output = model.predict_tag(sentence)
print(output)
# output: 'Statement-non-opinion'

sentence = "Why are you asking me this question again and again?"
output = model.predict_tag(sentence)
print(output)
# output: 'Wh-Question'

# To complete this component, work through the list of acts with your team and identify cases of discourse obligations. Specifically, you should imagine a discourse obligation as a tuple of the form (prompt act, (set of acts that can follow that act)). Identify five such discourse obligations. You’ll be using these in your dialogue system later on. 

# (Yes-No-Question	(Yes answers, No answers, Affirmative non-yes answers, Negative non-no answers))

# (Declarative Yes-No-Question	(Yes answers, No answers, Affirmative non-yes answers, Negative non-no answers))

# (Statement-non-opinion	(Acknowledge (Backchannel)	, Statement-opinion, Appreciation,Conventional-closing	,Response Acknowledgement	,Summarize/reformulate, Backchannel in question form	))

# (Action-directive	 (Yes answers, No answers, Affirmative non-yes answers, Negative non-no answers, Agree/Accept, Maybe/Accept-part	))

# (Statement-opinion	(Acknowledge (Backchannel)	, Statement-opinion, Appreciation, Response Acknowledgement, Summarize/reformulate, Backchannel in question form))

# Additionally, for five other acts that are not already a first element in one of your obligations, write up a quick example of an utterance that a chatbot could produce as a valid response to nearly all utterances that would perform that act. Include the preceding in your project writeup.

# Conventional-closing	
# "Well, it's been nice talking to you." 
# example reponse: "greating chatting to you too!"

# Thanking	
# "Hey thanks a lot"
# example reponse: "you are welcome!"

# Apology	
# 'I am sorry."
# example reponse: "no worries"

# Conventional-opening	
# "How are you?", "hi", "good morning"
# example reponse: "hi i just finished my final and feels awesome! hbu"

# Quotation	
# "You can't be pregnant and have cats"
# example reponse: "wow the quote is interesting"