import gradio as gr

def fix_code(language, broken_code):
    # PLACEHOLDER: replace this with a call to your trained model
    return f"# Model not connected yet.\n# Language: {language}\n\n{broken_code}"

demo = gr.Interface(
    fn=fix_code,
    inputs=[
        gr.Dropdown(["python", "java", "c", "cpp"], value="python", label="Language"),
        gr.Textbox(lines=15, label="Broken code"),
    ],
    outputs=gr.Textbox(lines=15, label="Fixed code"),
    title="Code Fixer",
)

demo.launch()