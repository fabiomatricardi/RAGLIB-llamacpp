# RAGLIB-llamacpp
a collection of tools to learn RAG strategies only with llama.cpp


use a full context RAG: it is the easiest one, straight forward and works good with the latest generation of Decoder only models. With some limitations. We will

- open a pdf
- transform it into text
- pass it in the chat history
- use the conversation history as short memory context

### Requirements
```bash
pip install requests rich langchain-text-splitters tiktoken pypdf easygui
```
Then we need
- [llama.cpp binaries (version b5686)](https://github.com/ggml-org/llama.cpp/releases/download/b5686/llama-b5686-bin-win-cpu-x64.zip), to download and extract the ZIP file in your project directory (mine is called BETTER_RAG)
- [Qwen2.5-1.5B-instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q6_k.gguf?download=true): a good small LLM with great context window and amazing performance. Download it in the same project folder.
- a PDF document as example: download it in the same directory (from this repo, called AIgentsFail.pdf)

### Run the llama.cpp server
First thing, let’s make sure our LocalGPT engine is running. Open one terminal window in the BETTER_RAG folder and execute:
```bash
llama-server.exe -m .\qwen2.5-1.5b-instruct-q6_k.gguf -c 8192
```
This will start the server and listen the API endpoints at  http://127.0.0.1:8080 with a context window of 8k tokens.

Run from the terminal `python betterRAG.py` and start your chat



