echo "This is a Bash repl, so don't use the Run button to execute your code. Instead, type in a command like 'python name_of_file_to_run.py' into the Bash console on the right (after the '>')."
pip3 install spacy
pip3 install profanity
pip3 install -U textblob
pip3 install langdetect
pip3 install pyenchant
python3 -m textblob.download_corpora
python3 -m spacy download en_core_web_sm