import warnings
warnings.filterwarnings(action='ignore')
import requests
import sys
import json
import pypdf
import tiktoken
from easygui import fileopenbox
from datetime import datetime
import RAGLIB as rag
# rag.countTokens(text)  rag.PDFtoText(pdffile)  rag.bot(messages)

# --- Configuration ---
LLAMA_CPP_SERVER_URL = "http://127.0.0.1:8080"
MODEL_NAME = "Qwen2.5-1.5B-instruct" 
NCTX = 8192  # Example context length, adjust as needed for your model/setup
COUNTERLIMITS = 16 # Reset history after this many turns
# Define stop sequences relevant to your model to prevent run-on responses
STOPS = ['<|im_end|>']




# LOAD PDF and convert to TEXT - RETRIEVAL        
pdffile = fileopenbox(msg='Pick your PDF', default='*.pdf')     
context, numtokens = rag.PDFtoText(pdffile)   

# Feed the TEXT the the LLM prompt - AUGMENTED  
prompt = f"""Read the provided passage, and when you finished say "I am ready".
<passage>
{context}
</passage>

"""
history = [{"role": "user","content": prompt}]

# Call the API to have the LLM understand your text - GENERATION  
start = datetime.now()
response = rag.bot(history)
history.append(response)
delta = datetime.now() - start
print(f"execution time: {delta.total_seconds()} seconds")

# create summary
history.append({"role": "user","content": "Write a short summary of the provided passage"})
start = datetime.now()
response = rag.bot(history)
history.append(response)
delta = datetime.now() - start
print(f"execution time: {delta.total_seconds()} seconds")

# create TAble of contents
history.append({"role": "user","content": "Write the five main topics and why they are relevant"})
start = datetime.now()
response = rag.bot(history)
history.append(response)
delta = datetime.now() - start
print(f"execution time: {delta.total_seconds()} seconds")


while True:
    userinput = ""
    print("\033[1;30m")  #dark grey
    print("Enter your text (end input with Ctrl+D on Unix or Ctrl+Z on Windows) - type quit! to exit the chatroom:")
    print("\033[91;1m")  #red
    lines = sys.stdin.readlines()
    for line in lines:
        userinput += line + "\n"
    if "quit!" in lines[0].lower():
        print("\033[0mBYE BYE!")
        break
    print("\033[92;1m")
    history.append({"role": "user","content": userinput})
    start = datetime.now()
    response = rag.bot(history)
    history.append(response)
    delta = datetime.now() - start
    print("\033[0m")  # Reset all colors
    print(f"execution time: {delta.total_seconds()} seconds\n\n")