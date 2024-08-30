import os
import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "save_details",
            "description": "This tool is used to submit the person details with the appropriate attributes after the on-boarding.",
            "parameters": {
                "type": "object",
                "properties": {
                    "full_name": {
                        "type": "string",
                        "description": "The full name of the person.",
                    },
                    "previous_experience_as_mentee": {
                        "type": "string",
                        "description": "The experience of the person as a mentee"
                    },
                    "knowledge_of_mentoring": {
                        "type": "string",
                        "description": "The knowledge of the person about mentoring"
                    },
                    "previous_experience_as_mentor": {
                        "type": "string",
                        "description": "The experience of the person as a mentor"
                    },
                    "intention": {
                        "type": "string",
                        "description": "The intention of the person to work with the platform"
                    },
                    "motivation_and_clarity": {
                        "type": "string",
                        "description": "The motivation and clarity of the person about the platform."
                    },
                },
                "required": ["full_name", 'previous_experience_as_mentee', 'knowledge_of_mentoring', 'previous_experience_as_mentor', 'intention', 'motivation_and_clarity'],
            },
        }
    },
]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            'role': 'system',
            'content': open('prompt.txt', 'r').read()
        }
    ]

for message in st.session_state.messages:
    if message['role'] != 'system' and message['content'] != 'Hey!':
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            temperature=1.0,
            top_p=1.0,
            model='gpt-4o-mini',
            messages=st.session_state.messages,
            tools=tools
        )

        if response.choices[0].message.tool_calls:
            st.session_state.messages.append(response.choices[0].message)
            for tool_call in response.choices[0].message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = tool_call.function.arguments

                with open(f"interview_conv-{fn_name}.txt", 'w') as f:
                    f.write(str(json.loads(fn_args)))
                st.write(json.loads(fn_args))
            
                tool_inp = "Successfully executed, please proceed to the further sections."
                st.session_state.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": fn_name,
                        "content": tool_inp,
                    }
                )

            response = client.chat.completions.create(
                temperature=1.0,
                top_p=1.0,
                model='gpt-4o-mini',
                messages=st.session_state.messages,
                tools=tools
            )

        st.markdown(response.choices[0].message.content)

    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})