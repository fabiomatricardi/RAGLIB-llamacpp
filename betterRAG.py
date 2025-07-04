import warnings
warnings.filterwarnings(action='ignore')
import requests
import sys
import json
import pypdf
import tiktoken
from easygui import fileopenbox
from datetime import datetime

# --- Configuration ---
LLAMA_CPP_SERVER_URL = "http://127.0.0.1:8080"
MODEL_NAME = "Qwen2.5-1.5B-instruct" 
NCTX = 8192  # Example context length, adjust as needed for your model/setup
COUNTERLIMITS = 16 # Reset history after this many turns
# Define stop sequences relevant to your model to prevent run-on responses
STOPS = ['<|im_end|>']

# --- Initialize Requests Session ---
session = requests.Session()
session.headers.update({
    "Content-Type": "application/json",
    # If your Llama.cpp server is configured to require an API key (even a dummy one):
    # "Authorization": "Bearer not-needed"
})


def countTokens(text):
    if text is None: return 0
    encoding = tiktoken.get_encoding("cl100k_base")
    numoftokens = len(encoding.encode(str(text)))
    return numoftokens

def PDFtoText(pdffile):
    # try to read the PDF and write it into a txt file, same name but .txt extension
    # returns the text and the number of tokens
    try:
        reader = pypdf.PdfReader(pdffile)
        text = ""
        page_count = len(reader.pages)
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text: text += page_text + "\n"
        a = text.strip()
        textfile = a.replace('\n\n','')
        print('✅ Creating text file...')
        print('✅ Counting tokens...')
        num_of_tokens = countTokens(textfile)
        print(f"✅ Parsed from PDF {page_count} pages of text\nA total context of {num_of_tokens} tokens ")
        return textfile, num_of_tokens
    except Exception as e:
        print(f"⚠️ Error reading PDF {pdffile}: {e}")
        

def bot(messages):
    import requests
    import json
    BASE_URL = "http://localhost:8080/v1"
    MODEL_NAME = "Qwen2.5-1.5B-instruct" 
    STOPS = ['<|im_end|>']
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.3,
        "frequency_penalty": 1.6,
        "max_tokens": 1600, # Adjust as needed
        "stream": True,
        "stop": STOPS
        # Add other parameters your Llama.cpp server supports, e.g.:
        # "n_predict": 1000, # llama.cpp specific equivalent to max_tokens
        # "top_k": 40,
        # "top_p": 0.9,
        # "repeat_penalty": 1.1
    }
    #message in case of error
    servererror = {"role": "assistant", "content": "Your AI is not responding..."}
    try:
        response = session.post(
            f"{BASE_URL}/chat/completions",
            json=payload,
            stream=True  # Crucial for streaming
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses (4XX or 5XX)
        assistant_response_content = ""        
        for line_bytes in response.iter_lines():
            if line_bytes:
                decoded_line = line_bytes.decode('utf-8')
                if decoded_line.startswith("data: "):
                    json_data_str = decoded_line[len("data: "):].strip()
                    if json_data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(json_data_str)
                        if chunk.get("choices") and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            content_piece = delta.get("content")
                            if content_piece:
                                print(content_piece, end="", flush=True)
                                assistant_response_content += content_piece
                    except json.JSONDecodeError:
                        # This might happen if the server sends a non-JSON line or an incomplete JSON
                        # print(f"\n[SYSTEM DEBUG] Non-JSON or malformed data line: {json_data_str}", file=sys.stderr)
                        pass # Ignoring malformed lines for now, can be logged
        
        print() # Add a newline after the assistant's full response is printed

        if assistant_response_content: # Only add to history if content was received
            history = {"role": "assistant", "content": assistant_response_content}
        return history
    except requests.exceptions.ConnectionError as e:
        print(f"\033[0;31m\n[ERROR] Could not connect to Llama.cpp server at {BASE_URL}.")
        print(f"Details: {e}\033[0m")
        print("Please ensure the server is running and accessible.")
        return servererror
    except requests.exceptions.HTTPError as e:
        print(f"\033[0;31m\n[ERROR] HTTP error occurred: {e.response.status_code} {e.response.reason}")
        print(f"Response: {e.response.text}\033[0m")
        # Depending on the error, you might want to break or allow retry
        return servererror
    except requests.exceptions.RequestException as e:
        print(f"\033[0;31m\n[ERROR] An unexpected error occurred with the request: {e}\033[0m")
        return servererror
    except Exception as e: # Catch any other unexpected errors
        print(f"\033[0;31m\n[CRITICAL ERROR] An unexpected error occurred: {e}\033[0m")
        import traceback
        traceback.print_exc()
        return servererror
        
# LOAD PDF and convert to TEXT - RETRIEVAL        
pdffile = fileopenbox(msg='Pick your PDF', default='*.pdf')     
context, numtokens = PDFtoText(pdffile)   

# Feed the TEXT the the LLM prompt - AUGMENTED  
prompt = f"""Read the provided passage, and when you finished say "I am ready".
<passage>
{context}
</passage>

"""
history = [{"role": "user","content": prompt}]

# Call the API to have the LLM understand your text - GENERATION  
start = datetime.now()
response = bot(history)
history.append(response)
delta = datetime.now() - start
print(f"execution time: {delta.total_seconds()} seconds")

# create summary
history.append({"role": "user","content": "Write a short summary of the provided passage"})
start = datetime.now()
response = bot(history)
history.append(response)
delta = datetime.now() - start
print(f"execution time: {delta.total_seconds()} seconds")

# create TAble of contents
history.append({"role": "user","content": "Write the five main topics of provided passage"})
start = datetime.now()
response = bot(history)
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
    response = bot(history)
    history.append(response)
    delta = datetime.now() - start
    print("\033[0m")  # Reset all colors
    print(f"execution time: {delta.total_seconds()} seconds\n\n")