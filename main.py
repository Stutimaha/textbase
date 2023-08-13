import textbase
from textbase.message import Message
from textbase import models
import os
import pandas as pd
import ast
from typing import List
import openai


class MockCodingInterviewBot:
    def __init__(self):
        self.state = "initial"
        self.company_name = ""
        self.questions_data = pd.read_csv("leetcode_problems.csv")
        self.current_question_index = 0
        self.solution = ""
        
        self.openai_api_key = "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"  # Replace with your OpenAI API key
    
    def get_next_question(self):
        question = self.questions_data.iloc[self.current_question_index]
        self.current_question_index += 1
        return question['title'], question['description']
    
    def debug_solution(self, solution, question_title):
        prompt = f"Debug the following code for the '{question_title}' question:\n\n{solution}\n\nFeedback:"
        response = openai.Completion.create(
            api_key=self.openai_api_key,
            engine="davinci-codex",
            prompt=prompt
        )
        feedback = response.choices[0].text.strip()
        return feedback
    
    def on_message(self, message):
        if self.state == "initial":
            self.company_name = message.capitalize()
            self.state = "interview_started"
            return "You are chatting with a mock coding interview chatbot. Please provide the name of the company you're interested in for the interview experience."
        
        if self.state == "interview_started":
            self.state = "fetching_question"
            return "Great! Let's have a mock interview experience. Please wait a moment."
        
        if self.state == "fetching_question":
            self.state = "awaiting_solution"
            question_title, question_description = self.get_next_question()
            return f"Question {self.current_question_index} -> Title: {question_title}\n\nDescription: {question_description}"
        
        if self.state == "awaiting_solution":
            self.solution = message
            question_title = self.questions_data.iloc[self.current_question_index - 1]['title']
            self.state = "debugging_solution"
            feedback = self.debug_solution(self.solution, question_title)
            return f"Debugging the provided solution:\n{self.solution}\n\nFeedback: {feedback}\n\nReply with 'next' for the next question."
        
        if self.state == "debugging_solution":
            if message.lower() == "next":
                if self.current_question_index < len(self.questions_data):
                    question_title, question_description = self.get_next_question()
                    self.solution = ""
                    self.state = "awaiting_solution"
                    return f"Question {self.current_question_index} -> Title: {question_title}\n\nDescription: {question_description}"
                else:
                    self.state = "upgrade_ad"
                    return "Congratulations! You've completed the regular pack. Upgrade to our premium pack for more challenges and advanced features!"
        
        if self.state == "upgrade_ad":
            return "Upgrade to our premium pack for more advanced challenges and features."

# Your Textbase integration
@textbase.chatbot("interview-bot")
def on_message(message_history: List[Message], state: dict = None):
    if state is None:
        state = {}

    # Extract user message
    user_message = message_history[-1].content.strip().lower()

    # Create an instance of your MockCodingInterviewBot
    bot = MockCodingInterviewBot()

    # Get the bot's response based on the user message
    bot_response = bot.on_message(user_message)

    # Set the OpenAI API key for generating the GPT-3.5 Turbo response
    models.OpenAI.api_key = bot.openai_api_key  # Set the API key

    # Generate GPT-3.5 Turbo response
    gpt_response = models.OpenAI.generate(
        system_prompt=bot_response,
        message_history=message_history,
        model="gpt-3.5-turbo",
    )

    return gpt_response, state

if __name__ == "__main__":
    textbase.run("interview-bot")