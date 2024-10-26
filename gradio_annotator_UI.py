"""
Following changes are required:
Bring the image in center
change the color of previous and next question
add the question number / progress bar
previous question if on first image, then it should not go back
next question if on last image, then it should not go ahead
Hide the enter a user name and select option button
set the submit button on the same line

NEXT STEPS:
fix the multiple times update of same user/multiple user
maybe add a timestamp or something
"""

import gradio as gr
import os
import json
from datetime import datetime

# Path to the data directory and image directory
data_dir = "Translated_Llava_Data"
images_dir = "Data/llava_bench_wild/images"
english_data_file = "Data/llava_bench_wild/english/Bench_English.json"

# Define the list of languages (excluding English)
languages = ["Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Azerbaijani", "Basque", "Belarusian", "Bengali", "Bosnian", "Bulgarian", "Catalan", "Cebuano", "Chichewa", "Chinese (Simplified)", "Chinese (Traditional)", "Corsican", "Croatian", "Czech", "Danish", "Dutch", "Esperanto", "Estonian", "Filipino", "Finnish", "French", "Frisian", "Galician", "Georgian", "German", "Greek", "Gujarati", "Haitian Creole", "Hausa", "Hawaiian", "Hebrew", "Hindi", "Hmong", "Hungarian", "Icelandic", "Igbo", "Indonesian", "Irish", "Italian", "Japanese", "Javanese", "Kannada", "Kazakh", "Khmer", "Kinyarwanda", "Korean", "Kurdish", "Kyrgyz", "Lao", "Latin", "Latvian", "Lithuanian", "Luxembourgish", "Macedonian", "Malagasy", "Malay", "Malayalam", "Maltese", "Maori", "Marathi", "Mongolian", "Myanmar (Burmese)", "Nepali", "Norwegian", "Odia (Oriya)", "Pashto", "Persian", "Polish", "Portuguese", "Punjabi", "Romanian", "Russian", "Samoan", "Scots Gaelic", "Serbian", "Sesotho", "Shona", "Sindhi", "Sinhala", "Slovak", "Slovenian", "Somali", "Spanish", "Sundanese", "Swahili", "Swedish", "Tajik", "Tamil", "Tatar", "Telugu", "Thai", "Turkish", "Turkmen", "Ukrainian", "Urdu", "Uyghur", "Uzbek", "Vietnamese", "Welsh", "Xhosa", "Yiddish", "Yoruba", "Zulu"]

# Define a dictionary to store user sessions
user_sessions = {}

# Function to load data from a JSON file
def load_data(language):
    data_file = os.path.join(data_dir, f"Bench_{language}.json")
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# Function to load English data
def load_english_data():
    with open(english_data_file, "r", encoding="utf-8") as f:
        english_data = json.load(f)
    return english_data

# Function to handle the language selection and load data
def select_language(language, user_id):
    if not user_id or not language:
        return gr.update(value="<span style='color: red;'>Validator's Name or the Language is not selected. Please select both to continue.</span>", visible=True), gr.update(visible=False), None, "", "", "", "", "", "", "", "", gr.update(visible=False), gr.update(visible=False)

    data = load_data(language)
    english_data = load_english_data()
    user_sessions[user_id] = {
        "language": language,
        "data": data,
        "english_data": english_data,
        "current_question_index": 0
    }

    return gr.update(value="", visible=False), gr.update(visible=True), *show_question(user_id, 0), gr.update(value="", visible=False), gr.update(visible=False), gr.update(visible=False)

# Function to display the question and answer
def show_question(user_id, question_index):
    if user_id in user_sessions:
        session_data = user_sessions[user_id]
        data = session_data["data"]
        english_data = session_data["english_data"]

        if 0 <= question_index < len(data):
            entry = data[question_index]
            english_entry = english_data[question_index]
            image_path = os.path.join(images_dir, entry["image"])
            
            context = entry["context"]
            question = entry["question"]
            answer = entry["answer"]
            
            english_context = english_entry["context"]
            english_question = english_entry["question"]
            english_answer = english_entry["answer"]
            
            session_data["current_question_index"] = question_index
            
            return (image_path, english_context, context, english_question, question, english_answer, answer, session_data['current_question_index'] + 1, "", "", "")
        else:
            return None, "No more questions.", "", "", "", "", "", "Question Number: ", "", "", ""
    else:
        return None, "Please select a language first.", "", "", "", "", "", "Question Number: ", "", "", ""

# Function to handle feedback (yes or no)
def handle_feedback(user_id, feedback, mistake_type=None, updated_question=None, updated_answer=None):
    if user_id in user_sessions:
        session_data = user_sessions[user_id]
        current_index = session_data["current_question_index"]
        data = session_data["data"]
        language = session_data["language"]
        
        if 0 <= current_index < len(data):
            entry = data[current_index]
            entry["feedback"] = feedback
            if feedback == "No":
                entry["updated_question"] = updated_question
                entry["updated_answer"] = updated_answer
                entry["mistake_type"] = mistake_type  # Save mistake type in feedback
                save_updated_feedback(user_id, language, current_index, updated_question, updated_answer, mistake_type)
            
            return gr.update(value="Your entry is saved. Please press 'Next Question' to continue.", visible=True, elem_id="submit_confirm_button")
        
def save_updated_feedback(user_id, language, question_index, updated_question, updated_answer, mistake_type):
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{language}_{user_id}.json")
    
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            feedback_data = json.load(f)
    else:
        feedback_data = []

    # Check if the question number already exists in the feedback data
    question_found = False
    for feedback in feedback_data:
        if feedback["question_number"] == question_index:
            feedback["updated_question"] = updated_question
            feedback["updated_answer"] = updated_answer
            feedback["mistake_type"] = mistake_type
            feedback["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Add timestamp
            question_found = True
            break

    # If the question number doesn't exist, append the new feedback
    if not question_found:
        new_feedback = {
            "question_number": question_index,
            "updated_question": updated_question,
            "updated_answer": updated_answer,
            "mistake_type": mistake_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Add timestamp
        }
        feedback_data.append(new_feedback)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(feedback_data, f, ensure_ascii=False, indent=4)

# Function to toggle visibility of updated question/answer inputs based on feedback
def toggle_updated_inputs(feedback):
    if feedback == "No":
        return gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)  # Ensure three outputs
    else:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)  # Ensure three outputs


# Create the Gradio interface
css = """
#dropdown {
    margin-top: 10px;
}
#submit_button {
    background-color: orange;
}
#submit_confirm_button {
    color: red;
    font-family: 'Times New Roman';
    font-weight: bold;
    font-size: 1.5em; /* Increase text size */
    text-align: center; /* Center the text */
    background-color: #f8d7da; /* Light red background for prompt box */
    border: 1px solid #f5c6cb; /* Border to define the box */
    border-radius: 5px; /* Rounded corners */
    padding: 10px; /* Padding inside the box */
    margin: 10px auto; /* Center the box with auto margins */
    max-width: 1500px; /* Maximum width of the prompt box */
}
#previous_button {
    margin-top: 20px;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 5px;
    padding: 10px;
}
#next_button {
    margin-top: 20px;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 5px;
    padding: 10px;
}
"""
with gr.Blocks(css=css, theme=gr.themes.Base()) as iface:
    gr.Markdown("## Multilingual Translation Annotation Interface!")

    markdown_content = """
        <div style="color: red; font-family: 'Times New Roman'; font-weight: bold; font-size: 1em; text-align: justify; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 10px; margin: 10px auto; max-width: 1500px;">
            <b>Hello Annotator.</b> Thank you for taking the time to proofread our translations. We really appreciate your time and efforts. For your reference, please follow the below instructions for the smooth experience:<br><br>
            GENERAL POINTERS:
            <ol style="font-size: 1em;">
                <li> We apologize for the UI flaws, we are not professionals, it's just an attempt to make a basic interface.</li>
                <li> For each language, 60 Question-Answer pairs need to be proofread. There will be a "Question Number" bar to show the current progress.</li>
                <li> We really request you to attempt this in one go. This may take up to 60 minutes. If you don't have time now, we really request you to come back later and complete this work.</li>
                <li> Please enter your 'Full Name', then 'Select the Language' from the dropdown, and finally click 'Submit' to begin.</li>
            </ol>
            <br>
            ANNOTATION INSTRUCTIONS:
            <ol style="font-size: 1em;">
                <li> For each question, you'll see an image, its corresponding English Question/Answer pair, and the translated Question/Answer pair in your selected language.</li>
                <li> Please read the translated question/answer pair carefully. If the translation seems correct, select 'Yes' to the question below, or select 'No' if the translation is not correct.</li>
                <li> When selecting 'No', it will ask you to write correct translation of Question and Answer, and the Type of Mistake that currently exists. A short description for the Mistakes are as below: </li>
                    <ol style="font-size: 1em;">
                        <li>Semantic error (meaning completely ruined in the translation)</li>
                        <li>Cultural error (use of unusual words not used by locals in day-to-day language)</li>
                        <li>Contextual error (words that doesn’t match context, ex: The statue is living in Hawaii instead of The statue is located in Hawaii)</li>
                        <li>Language error (when translation is given in characters of a different alphabet)</li>
                        <li>Grammatical error (meaning is correct but just some grammar-related errors are present, if the true meaning of the sentence is not grasped in the translation along with grammar errors, please refer it as "Semantic error")</li>
                    </ol>
                <li> Even if either the question or answer is wrong (not both), we urge you to copy-paste the correct text as well along with the newly entered updated text.</li>
                <li> Please click the 'SUBMIT' button after you've verified that you have completed the question. The SUBMIT button only stores the record if you've updated any translation otherwise the original language record will be accessed.</li>
                <li> You may navigate to the Previous or Next Question. Please note that it will not automatically show your recently written response, it will be saved in our system. Reselect the Yes/No button and repeat the step (3) again. </li>
                <li> Only the most recent update will be stored and the previous question's entry will be over-written.</li>
            </ol>
        </div>
    """

    gr.Markdown(markdown_content)




    with gr.Column():
        user_id = gr.Textbox(label="Annotator's Name:", placeholder="Enter a Validator's Name")
        language_dropdown = gr.Dropdown(choices=languages, label="Select Language")
        language_button = gr.Button("Submit")
        warning_message = gr.HTML(value="", visible=False)

    chat_section = gr.Group(visible=False)
    with chat_section:
        question_counter = gr.Textbox(label="Question Number (Total 60)", interactive=False)
        image_output = gr.Image(width=400, height=300, elem_id="")
        with gr.Row():
            with gr.Column():
                english_context_output = gr.Textbox(label="English Context", lines=2, interactive=False)
                english_question_output = gr.Textbox(label="English Question", lines=2, interactive=False)
                english_answer_output = gr.Textbox(label="English Answer", lines=2, interactive=False)
            with gr.Column():
                context_output = gr.Textbox(label="Context", lines=2, interactive=False)
                question_output = gr.Textbox(label="Question", lines=2, interactive=False, elem_id="question")
                answer_output = gr.Textbox(label="Answer", lines=2, interactive=False)

    feedback_value = gr.Textbox(value="", visible=False)

    with chat_section:
        with gr.Column():
            options = ["Yes", "No"]
            translation_correct = gr.Dropdown(choices=options, label="Is the above Translated question/answer a correct translation for the English question/answer?", elem_id="dropdown")
            updated_question = gr.Textbox(label="Updated Question", lines=1, visible=False, placeholder="Please write the correct Question")
            updated_answer = gr.Textbox(label="Updated Answer", lines=1, visible=False, placeholder="Please write the correct Answer")
            
            # mistakes_choices = [
            #     "Answer given in a different alphabet (LANGUAGE ERROR)",
            #     "Sentence meaning completely ruined (SEMANTIC ERROR)",
            #     "Word placement or grammartical error (GRAMMATICAL ERROR)",
            #     "Use of unusual/not day-to-day words (CULTURAL ERROR)",
            #     "Name of a translated 'Place' is not correct (CONTEXTUAL ERROR)"
            # ]

            mistakes_choices = ["Semantic error (meaning ruined)",
                "Cultural error (use of unusual words)",
                "Contextual error (words that doesn’t match context)",
                "Language error (translation given in a different alphabet)",
                "Grammatical error (meaning is correct but grammar errors present)"
            ]

            mistake_type = gr.Dropdown(choices=mistakes_choices, label="Mark the type of mistake in the translated sentence", visible=False)
            translation_button = gr.Button("Submit", elem_id="submit_button")
            confirmation_message = gr.HTML(value="", visible=False)

        with gr.Row():
            prev_button = gr.Button("Previous Question", elem_id="previous_button")
            next_button = gr.Button("Next Question", elem_id="next_button")

    # Handle language selection
    language_button.click(select_language, inputs=[language_dropdown, user_id], outputs=[warning_message, chat_section, image_output, english_context_output, context_output, english_question_output, question_output, english_answer_output, answer_output, question_counter, updated_question, updated_answer])

    # Handle feedback change
    translation_correct.change(toggle_updated_inputs, inputs=[translation_correct], outputs=[updated_question, updated_answer, mistake_type])

    # Handle feedback submission
    translation_button.click(handle_feedback, inputs=[user_id, translation_correct, mistake_type, updated_question, updated_answer], outputs=[confirmation_message])

    # Handle question navigation
    next_button.click(
        lambda user_id: (*show_question(user_id, user_sessions[user_id]["current_question_index"] + 1), gr.update(value=""), "", gr.update(value="", visible=False)) if user_id in user_sessions else (None, "", "", "", "", "", "", "Question Number: ", "", "", "", gr.update(value="", visible=False)),
        inputs=[user_id],
        outputs=[image_output, english_context_output, context_output, english_question_output, question_output, english_answer_output, answer_output, question_counter, translation_correct, updated_question, updated_answer, confirmation_message]
    )
    prev_button.click(
        lambda user_id: (*show_question(user_id, user_sessions[user_id]["current_question_index"] - 1), gr.update(value=""), "", gr.update(value="", visible=False)) if user_id in user_sessions and user_sessions[user_id]["current_question_index"] > 0 else (None, "", "", "", "", "", "", "Invalid Question Number", "", "", "", gr.update(value="", visible=False)),
        inputs=[user_id],
        outputs=[image_output, english_context_output, context_output, english_question_output, question_output, english_answer_output, answer_output, question_counter, translation_correct, updated_question, updated_answer, confirmation_message]
    )

# Launch the interface
iface.launch(share=True)
