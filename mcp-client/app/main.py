import streamlit as st
from agent import initialize_supply_chain_agent

st.set_page_config(page_title = "MCP Supply Chain Agent", page_icon = "🏢", layout = "wide")
st.title("🏢 Autonomous Supply Chain Command Center")
st.caption("Powered by Model Context Protocol (MCP) & Odoo ERP Backend")

# Setup safe API key input field in the sidebar to prevent hardcoding keys
with st.sidebar:
    st.header("Configuration")
    groq_key = st.text_input("Enter Groq API Key:", type = "password")
    st.info("Get a free key from console.groq.com to initialize the remote LLM inference.")

if not groq_key:
    st.warning("Please provide a valid Groq API Key in the sidebar to wake up the agent.")
else:
    # Initialize agent executor session states
    if "agent_executor" not in st.session_state:
        st.session_state.agent_executor = initialize_supply_chain_agent(groq_key)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display historical conversation logs
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Accept incoming text stream from supply chain operators
    if user_prompt := st.chat_input("Ask about delayed orders, inventory levels, or issue routing updates..."):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing live ERP systems..."):
                try:
                    # Execute agent cycle against the MCP server tools
                    response = st.session_state.agent_executor.invoke({
                        "input": user_prompt,
                        "chat_history": [] # Expand with session variables if you need long state retention
                    })
                    output_text = response["output"]
                    st.markdown(output_text)
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
                except Exception as e:
                    st.error(f"Execution Error encountered: {e}")