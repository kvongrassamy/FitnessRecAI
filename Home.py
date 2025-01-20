# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2024)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import streamlit as st
from components.chat import init_chat, show_chat
from parlant.client import ParlantClient
from agents import agent_home


def init_session_state():
    """Initialize session state variables"""
    # Initialize chat with home page agent
    
    init_chat(agent_home.id)

def main():
    st.title("AI Fitness Guide")
    st.write("Welcome to your AI Fitness Guide.  Your AI friend can help provide information on your first workout program")
    # Initialize session state
    init_session_state()
    
    # Show features
    st.subheader("Features")
    st.write("""
    - 📚 **Learning Fitness Guide**: Follow a structured learning path tailored to your goals
    - 📖 **Learning Resources**: Access curated resources to support your learning journey
    - 💬 **AI Chat Support**: Get help from our AI Gym Info anytime
    """)
    
    # Show chat interface
    show_chat("Hi! I'm your AI Fiteness Guide. How can I help you today?")

if __name__ == "__main__":
    main()