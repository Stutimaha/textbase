# Load the dataset of questions
questions_data = pd.read_csv("leetcode_problems.csv")

# Global variables to store the company and question index
current_company = None
current_question_index = None

# Function to get a coding question related to the specified company
def get_question(company_name):
    company_questions = questions_data[questions_data['companies'].str.contains(company_name, case=False, na=False)]
    
    if not company_questions.empty:
        random_question = company_questions.sample(n=1)
        question_title = random_question['title'].iloc[0]
        question_description = random_question['description'].iloc[0]
        return f"Title: {question_title}\n\nDescription: {question_description}"
    else:
        return f"No questions found for {company_name}"

def debug_code(solution, question_title):
    try:
        # Use OpenAI API to provide feedback on the user's code
        prompt = f"Debug the following code for the '{question_title}' question:\n\n{solution}\n\nFeedback:"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=100
        )
        feedback = response.choices[0].text.strip()
        return feedback
    except Exception as e:
        return f"An error occurred while debugging: {e}"
    
    ################################

    if current_company is None:
        # Scenario: User is providing a company name
        bot_response = get_company(user_message)
    else:
        if user_message == "next":
            # Scenario: User wants to move to the next question
            state["counter"] = state.get("counter", 0) + 1
            current_question_index += 1
            bot_response = get_question()
        elif state.get("counter", 0) > 0:
            # Scenario: User is submitting a solution
            solution = user_message
            question_title = questions_data.iloc[current_question_index]['title']
            feedback = debug_code(solution, question_title)
            bot_response = "Here's the feedback on your solution:\n\n" + feedback + "\n\nIf you're ready for the next question, type 'next'."
        else:
            # Scenario: User's response doesn't match any specific condition
            bot_response = "I'm sorry, I couldn't understand your response. Please type 'next' to proceed or provide the company name."

    return bot_response, current_question_index, state

##################################

import textbase
from textbase.message import Message
from textbase import models
import os
import pandas as pd
import ast
from typing import List

# Load your OpenAI API key
models.OpenAI.api_key = "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"
# or from environment variable:
# models.OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# Prompt for GPT-3.5 Turbo
SYSTEM_PROMPT = """You are chatting with a mock coding interview chatbot. Please provide the name of the company you're interested in for the interview experience.
"""

# Load the dataset of questions
questions_data = pd.read_csv("leetcode_problems.csv")

# Global variables to store the company and question index
current_company = None
current_question_index = 0

def get_company(company_name):
    global current_company
    # Check if the provided company name exists in the dataset
    if company_name in questions_data['companies'].str.contains(company_name, case=False, na=False):
        current_company = company_name
        return f"Great! Let's have a mock interview experience with questions from {current_company}. Please wait a moment."
    else:
        return f"Sorry, we don't have questions tagged with {company_name} in our dataset."

def get_question():
    global current_question_index
    if current_question_index < len(questions_data):
        question_title = questions_data.iloc[current_question_index]['title']
        question_description = questions_data.iloc[current_question_index]['description']
        question_difficulty = questions_data.iloc[current_question_index]['difficulty']
        return f"Question {current_question_index + 1} ({question_difficulty}): {question_title}\n\n{question_description}\n\nPlease provide your solution in Python code. When you're ready, type 'next' for the next question."
    else:
        return "Congratulations! You've completed the mock interview. If you'd like to continue, consider trying out our premium features."

def debug_code(solution, question_title):
    try:
        # Check syntax errors
        parsed_code = ast.parse(solution)
        syntax_errors = compile(parsed_code, filename="<string>", mode="exec")
        # If there are no syntax errors, perform additional checks
        feedback = check_logic(parsed_code, question_title)
        return feedback
    except SyntaxError as e:
        return f"Syntax Error: {e}"
    except Exception as e:
        return f"An error occurred while debugging: {e}"

def check_logic(parsed_code, question_title):
    # Implement your logic checking here
    # For simplicity, let's assume we're providing a fixed feedback message
    feedback = f"Your solution for the '{question_title}' question looks good! Keep up the good work."
    return feedback

@textbase.chatbot("interview-bot")
def on_message(message_history: List[Message], state: dict = None):
    global current_company
    global current_question_index

    if state is None:
        state = {}

    # Extract user message
    user_message = message_history[-1].content.strip().lower()
    if current_company is None:
        # Scenario: User is providing a company name
        bot_response = get_company(user_message)
    else:
        if user_message == "next":
            # Scenario: User wants to move to the next question
            state["counter"] = state.get("counter", 0) + 1
            current_question_index += 1
            bot_response = get_question()
        elif state.get("counter", 0) > 0:
            # Scenario: User is submitting a solution
            solution = user_message
            question_title = questions_data.iloc[current_question_index]['title']
            feedback = debug_code(solution, question_title)
            bot_response = "Here's the feedback on your solution:\n\n" + feedback + "\n\nIf you're ready for the next question, type 'next'."
        else:
            # Scenario: User's response doesn't match any specific condition
            bot_response = "I'm sorry, I couldn't understand your response. Please type 'next' to proceed or provide the company name."
            
"""
    # Check if the user is providing the company name
    if user_message == "next":
            state["counter"] = state.get("counter", 0) + 1
            current_question_index += 1
            bot_response = get_question(current_company)
    elif user_message == 
    else:
        # Check if the user is submitting a solution
        if state.get("counter", 0) > 0:
            # Debug the user's code and provide feedback
            solution = user_message
            question_title = questions_data.iloc[current_question_index]['title']
            feedback = debug_code(solution, question_title)
            bot_response = "Here's the feedback on your solution:\n\n" + feedback + "\n\nIf you're ready for the next question, type 'next'."
        else:
            bot_response = "Please type 'next' to get the first coding question."
"""

    # Generate GPT-3.5 Turbo response
    gpt_response = models.OpenAI.generate(
        system_prompt=SYSTEM_PROMPT + bot_response,
        message_history=message_history,
        model="gpt-3.5-turbo",
    )

    return gpt_response, state

if __name__ == "__main__":
    textbase.run("interview-bot")



