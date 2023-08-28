import openai
import os

openai.api_key ="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"


messages= [
    {"role": "system","content":"you are a kind assistant."},
]

while True:
    message = input("User :")
    if message:
        messages.append(
            {"role": "user","content":message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    messages.append({"role":"assistant", "content":reply})
        
        
        