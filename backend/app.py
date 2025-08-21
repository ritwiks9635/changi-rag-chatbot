import gradio as gr
from app.chatbot import answer_user_query

# ---------- CSS: Clean & Professional ---------- #
css_code = """
body {
    font-family: 'Segoe UI', sans-serif;
    background-color: #f4f4f9;
}
.gradio-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
}
.gr-chatbot {
    border: 1px solid #ddd !important;
    border-radius: 10px !important;
    background-color: #ffffff !important;
    min-height: 500px;
}
.gr-chatbot .message.user {
    background-color: #e6f0ff !important;
    color: #003366 !important;
    border-radius: 8px;
    font-weight: 500;
}
.gr-chatbot .message.bot {
    background-color: #f1f3f5 !important;
    color: #000000 !important;
    border-radius: 8px;
}
textarea {
    font-size: 16px !important;
    border-radius: 8px !important;
}
.gr-button {
    font-weight: 600;
    border-radius: 8px !important;
    background-color: #0052cc !important;
    color: white !important;
}
"""

# ---------- Chat Logic ---------- #
async def respond(message, history):
    response = await answer_user_query(message)  # ✅ Fixed: no await
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    return "", history

# ---------- Interface ---------- #
with gr.Blocks(css=css_code, title="Changi Airport Assistant") as demo:
    gr.Markdown("## 🛬 Changi Airport & Jewel Virtual Assistant")

    # ✅ Set welcome message here
    welcome = [{
        "role": "assistant",
        "content": "Welcome! How can I assist you today?\nFeel free to ask about terminals, shopping, directions, events, or anything at Changi Airport."
    }]

    chatbot = gr.Chatbot(label=None, height=500, type="messages", value=welcome)
    state = gr.State(welcome)

    with gr.Row():
        txt = gr.Textbox(
            placeholder="Ask anything about Changi Airport...",
            show_label=False,
            lines=2,
            scale=8
        )
        submit = gr.Button("Submit", scale=1)

    clear = gr.Button("Clear Chat")

    submit.click(respond, [txt, state], [txt, chatbot])
    txt.submit(respond, [txt, state], [txt, chatbot])

    clear.click(lambda: ("", welcome), None, [txt, chatbot, state])

    gr.Markdown("""
    <div style='text-align: center; font-size: 13px; margin-top: 20px; color: #888'>
        © 2025 Changi Assistant by Ritwik Sarkar • Powered by Groq + Pinecone + Gradio
    </div>
    """)

demo.launch()
