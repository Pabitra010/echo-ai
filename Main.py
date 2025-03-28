from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDireectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model_Test import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SepeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DeafultMessage = f'''{Username}: How are you ?
{Assistantname} : Welcome back {Username}. I am doing well. How may i help you  '''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as File:
            if len(File.read()) < 5:
                with open(TempDireectoryPath('Databasr.data'), 'w', encoding='utf-8') as file:
                    file.write("")
                with open(TempDireectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                    file.write(DeafultMessage)
    except Exception as e:
        print(f"Error in ShowDefaultChatIfNoChats: {e}")

def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except Exception as e:
        print(f"Error in ReadChatLogJson: {e}")
        return []

def ChatLogIntegration():
    try:
        json_data = ReadChatLogJson()
        formated_chatlog = ""
        for entry in json_data:
            if entry["role"] == "user":
                formated_chatlog += f"User: {entry['content']}\n"
            elif entry["role"] == "assistant":
                formated_chatlog += f"Assistant: {entry['content']}\n"
        formated_chatlog = formated_chatlog.replace("User", Username + " ")
        formated_chatlog = formated_chatlog.replace("Assistant", Assistantname + " ")

        with open(TempDireectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write(AnswerModifier(formated_chatlog))
    except Exception as e:
        print(f"Error in ChatLogIntegration: {e}")

def ShowChatsOnGUI():
    try:
        with open(TempDireectoryPath('Database.data'), 'r', encoding='utf-8') as File:
            Data = File.read()
            if len(str(Data)) > 0:
                lines = Data.split('\n')
                result = '\n'.join(lines)
                with open(TempDireectoryPath('Responses.data'), "w", encoding='utf-8') as File:
                    File.write(result)
    except Exception as e:
        print(f"Error in ShowChatsOnGUI: {e}")

def InitialExecution():
    try:
        SetMicrophoneStatus("False")
        ShowTextToScreen("")
        ShowDefaultChatIfNoChats()
        ChatLogIntegration()
        ShowChatsOnGUI()
    except Exception as e:
        print(f"Error in InitialExecution: {e}")

InitialExecution()

def MainExecution():
    try:
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""

        SetAssistantStatus("Listening....")
        Query = SepeechRecognition()
        ShowTextToScreen(f"{Username} : {Query}")
        SetAssistantStatus("Thinking....")
        Decision = FirstLayerDMM(Query)

        print("")
        print(f"Decision : {Decision}")
        print("")

        G = any([i for i in Decision if i.startswith("general")])
        R = any([i for i in Decision if i.startswith("realtime")])

        Mearged_query = " and ".join(
            [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
        )

        for queries in Decision:
            if "generate " in queries:
                ImageGenerationQuery = str(queries)
                ImageExecution = True

        for queries in Decision:
            if TaskExecution == False:
                if any(queries.startswith(func) for func in Functions):
                    run(Automation(list(Decision)))
                    TaskExecution = True

        if ImageExecution == True:
            with open(r"Frontend/Files/ImageGeneration.data", "w") as file:
                file.write(f"{ImageGenerationQuery},True")

            try:
                p1 = subprocess.Popen(['python', r'Backend/ImageGeneration.py'],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      stdin=subprocess.PIPE, shell=False)
                subprocesses.append(p1)
            except Exception as e:
                print(f"Error Starting ImageGeneration.py: {e}")

        if G and R or R:
            SetAssistantStatus("Searching...")
            Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True
        else:
            for Queries in Decision:
                if "general" in Queries:
                    SetAssistantStatus("Thinking...")
                    QueryFinal = Queries.replace("general ", "")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
                
                elif "realtime" in Queries:
                    SetAssistantStatus("Searching...")
                    QueryFinal = Queries.replace("realtime ", "")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
                
                elif "exit" in Queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    SetAssistantStatus("Answering...")
                    os._exit(1)
    except Exception as e:
        print(f"Error in MainExecution: {e}")

def FirstThread():
    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()

            if CurrentStatus == "True":
                MainExecution()
            else:
                AIStatus = GetAssistantStatus()

                if "Available..." in AIStatus:
                    sleep(0.1)
                else:
                    SetAssistantStatus("Available...")
        except Exception as e:
            print(f"Error in FirstThread: {e}")

def SecondThread():
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"Error in SecondThread: {e}")

if __name__ == "__main__":
    try:
        thread2 = threading.Thread(target=FirstThread, daemon=True)
        thread2.start()
        SecondThread()
    except Exception as e:
        print(f"Error in main: {e}")
