import streamlit as st
import requests
import json

st.set_page_config(page_title="Social Relationship Simulator", page_icon="🧠", layout="centered")

class WebSocialSimulator:
    def __init__(self, api_key: str):
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"

    def _query_gemini(self, system_instruction: str, user_message: str) -> str:
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": user_message}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        except requests.exceptions.Timeout:
            return "⚠️ Request timed out. The API took too long to respond — please try again."
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            if status == 400:
                return "⚠️ Invalid request. Your API key may be malformed."
            elif status == 403:
                return "⚠️ API key rejected. Please check that your Gemini API key is valid and active."
            elif status == 429:
                return "⚠️ Rate limit reached. Please wait a moment before sending another message."
            else:
                return f"⚠️ API returned an error (HTTP {status}). Please try again."
        except requests.exceptions.ConnectionError:
            return "⚠️ Could not connect to the API. Please check your internet connection."
        except (KeyError, IndexError):
            return "⚠️ Unexpected response format from the API. The model may have returned no content (possibly blocked by safety filters)."
        except Exception as e:
            return f"⚠️ Unexpected error: {e}"

    def check_importance(self, message: str) -> bool:
        hard_keywords = ["resignation", "promotion", "marriage", "breakup", "debt", "money", "lie", "move", "quit"]
        if any(word in message.lower() for word in hard_keywords):
            return True

        analyst_prompt = (
            f"Analyze the following sentence:\n\"{message}\"\n"
            "If this sentence contains a turning point, secret confession, critical decision, "
            "or crucial information that the character must remember, reply with 'YES' only. "
            "If it is ordinary small talk, reply with 'NO' only. Do not write anything else."
        )
        return "YES" in self._query_gemini("Answer in a single word only.", analyst_prompt).upper()

if "phase" not in st.session_state:
    st.session_state.phase = 1
    st.session_state.chat_history = []
    st.session_state.critical_facts = []
    st.session_state.interview_count = 0

st.title("🧠 AI-Based Social Relationship Simulator")
st.write("Simulate and test challenging real-life interpersonal dynamics in a safe AI-driven environment.")

with st.sidebar:
    st.header("🔑 Connection Settings")
    api_key = st.text_input("Google Gemini API Key", type="password", help="Get your free key from aistudio.google.com")
    st.markdown("---")
    if st.session_state.phase > 1:
        st.subheader("📊 Character Card")
        st.info(f"**Name:** {st.session_state.c_name}\n\n**Relationship:** {st.session_state.c_rel}")
        if st.session_state.critical_facts:
            st.warning("🔒 Long-Term Memory:\n\n" + "\n\n".join([f"- {f}" for f in st.session_state.critical_facts]))

if not api_key:
    st.warning("Please enter your Gemini API Key in the left sidebar to proceed.")
else:
    engine = WebSocialSimulator(api_key)

    if st.session_state.phase == 1:
        st.subheader("👤 Design Your Character")
        c_name = st.text_input("Name/Title of the person to simulate:", placeholder="e.g., Mr. Yılmaz, Landlord")
        c_rel = st.text_input("What is your relationship with this person?", placeholder="e.g., Manager, Client")
        c_info = st.text_area("Basic traits and behaviors of this person:", placeholder="e.g., Very short-tempered, rejects raise requests claiming budget cuts...")

        if st.button("Create Character & Start Interview"):
            if c_name and c_rel and c_info:
                st.session_state.c_name = c_name
                st.session_state.c_rel = c_rel
                st.session_state.c_info = c_info
                st.session_state.phase = 2
                st.rerun()
            else:
                st.error("Please fill in all fields!")

    elif st.session_state.phase == 2:
        st.subheader("🤖 AI Profiling Interview")
        st.write(f"The AI analyst is asking questions to perfect the profile for **{st.session_state.c_name}**.")

        if st.session_state.interview_count < 3:
            facts_str = " ".join(st.session_state.critical_facts)
            interview_prompt = (
                f"The user provided this info about {st.session_state.c_name} ({st.session_state.c_rel}): {st.session_state.c_info}. "
                f"Additional facts known: {facts_str}. Ask EXACTLY ONE clear question in English about missing traits, red lines, or speech style to simulate this person accurately."
            )

            if "current_question" not in st.session_state:
                st.session_state.current_question = engine._query_gemini("You are a professional character analyst.", interview_prompt)

            st.markdown(f"**Analyst:** {st.session_state.current_question}")

            with st.form(key="interview_form", clear_on_submit=True):
                user_answer = st.text_input("Your Answer:")
                submit_answer = st.form_submit_button("Submit Answer")

                if submit_answer and user_answer:
                    st.session_state.critical_facts.append(user_answer)
                    st.session_state.interview_count += 1
                    del st.session_state.current_question
                    st.rerun()
        else:
            facts_summary = " ".join(st.session_state.critical_facts)
            st.session_state.system_prompt = (
                f"Your name is {st.session_state.c_name}. Relationship to user: {st.session_state.c_rel}.\n"
                f"Core Character Description: {st.session_state.c_info}.\n"
                f"Additional Facts Learned: {facts_summary}.\n"
                f"Task: Never break character. Fully embody this persona and respond realistically in English."
            )
            st.session_state.phase = 3
            st.success("🎉 Character modeled successfully! Live simulation room is ready.")
            if st.button("Enter Simulation Room"):
                st.rerun()

    elif st.session_state.phase == 3:
        st.subheader(f"🎬 Live Simulation with {st.session_state.c_name}")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if user_msg := st.chat_input("Type your message..."):
            with st.chat_message("user"):
                st.write(user_msg)
            st.session_state.chat_history.append({"role": "user", "content": user_msg})

            if engine.check_importance(user_msg):
                st.session_state.critical_facts.append(user_msg)
                st.toast(f"💡 {st.session_state.c_name} saved this to long-term memory!", icon="🧠")

            if len(st.session_state.chat_history) > 10:
                context_history = st.session_state.chat_history[-10:]
            else:
                context_history = st.session_state.chat_history

            history_context_str = "\n".join([f"{m['role']}: {m['content']}" for m in context_history])

            with st.spinner(f"{st.session_state.c_name} is thinking..."):
                ai_reply = engine._query_gemini(st.session_state.system_prompt, history_context_str)

            with st.chat_message("assistant"):
                st.write(ai_reply)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            st.rerun()

        if st.button("Reset Simulation & Create New Character"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
