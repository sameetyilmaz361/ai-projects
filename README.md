# ai-projects
AI experiments: Gemini-based persona simulator and local LLaMA quiz generator
# AI Projects

A collection of small AI-based tools exploring conversational simulation and local LLM applications.

## 1. Social Relationship Simulator (`persona_simulator.py`)

A Streamlit web app that lets users practice difficult real-life conversations with an AI-simulated persona.

- User defines a character (name, relationship, key traits)
- The AI conducts a short profiling interview to refine the persona
- User then chats live with the simulated character
- The system automatically detects and remembers important information shared during the conversation (e.g. confessions, decisions, critical facts) for long-term consistency

**Tech stack:** Python, Streamlit, Google Gemini API

**Setup:**
```bash
pip install streamlit requests
streamlit run persona_simulator.py
```
You'll need a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) — enter it in the sidebar when the app launches.

> Note: Google updates available Gemini model names periodically. If you get an HTTP 404 error, check the current model list and update the model name in the code.

## 2. LLaMA Quiz Generator (`llama_quiz.py`)

A command-line quiz application powered by a local LLaMA model (via `llama-cpp-python`). The user enters a topic, the model generates multiple-choice questions on the fly, and the script scores the user's answers at the end.

- Generates 3 multiple-choice questions (A/B/C/D) on a user-chosen topic
- Tracks correct answers and prints a final score with feedback

**Tech stack:** Python, llama-cpp-python

**Setup:**
```bash
pip install llama-cpp-python
```
Download a compatible `.gguf` model file and place it in the same folder as the script (the code looks for `slm.gguf` by default — rename your model file or update `model_path` in the code).

```bash
python llama_quiz.py
```

## Notes

These are learning projects built to explore prompt design, conversational state management, and working with both cloud-based and local LLMs. Not production-hardened, but functional and actively improved.
