from selenium import webdriver  # Importing Selenium WebDriver to automate browser actions
from selenium.webdriver.common.by import By  # Importing 'By' to locate elements on a webpage
from selenium.webdriver.chrome.service import Service  # Importing 'Service' to manage ChromeDriver service
from selenium.webdriver.chrome.options import Options  # Importing 'Options' to set Chrome options
from webdriver_manager.chrome import ChromeDriverManager  # Automatically installs the correct ChromeDriver
from dotenv import dotenv_values  # Importing dotenv to read environment variables
import os  # Importing os to handle file operations and paths
import mtranslate as mt  # Importing mtranslate for text translation

# Loading environment variables from .env file
env_vars = dotenv_values(".env")

# Retrieving the input language setting from environment variables
InputLanguage = env_vars.get("InputLanguage")

# HTML code for a simple speech recognition webpage
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();  // Initializing speech recognition
            recognition.lang = '';
            recognition.continuous = true;  // Allow continuous speech recognition

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;  // Get the latest recognized text
                output.textContent += transcript;  // Append recognized text to output
            };

            recognition.onend = function() {
                recognition.start();  // Restart recognition when it stops
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();  // Stop speech recognition
            output.innerHTML = "";  // Clear the output text
        }
    </script>
</body>
</html>'''

# Setting the speech recognition language dynamically from environment variables
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Saving the HTML file in the 'Data' directory
with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)

# Getting the current working directory
current_dir = os.getcwd()

# Generating the file path for the saved HTML file
Link = f"file:///{current_dir.replace(os.sep, '/')}/Data/Voice.html"

# Configuring Chrome options for WebDriver
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"--user-agent={user_agent}")  # Setting custom user agent
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Simulating media permissions
chrome_options.add_argument("--use-fake-device-for-media-stream")  # Simulating microphone access
chrome_options.add_argument("--headless=new")  # Running Chrome in headless mode (no GUI)

# Setting up Chrome WebDriver service
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Defining the temporary directory path for storing status files
TempDirPath = rf"{current_dir}/Frounted/Files"

# Function to set the assistant's status
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)  # Writing the status to a file

# Function to modify and format the user query
def QueryModifier(Query):
    new_query = Query.lower().strip()  # Converting to lowercase and removing extra spaces
    question_words = ["how", "what", "where", "when", "why", "which", "who", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word in new_query.split() for word in question_words):
        new_query = new_query.rstrip(".?!") + "?"  # Ensuring questions end with '?'
    else:
        new_query = new_query.rstrip(".?!") + "."  # Ensuring statements end with '.'

    return new_query.capitalize()  # Capitalizing the first letter

# Function to translate text to English
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, to_language="en", from_language="auto")  # Auto-detect source language
    return english_translation.capitalize()  # Capitalizing the translated text

# Function to handle speech recognition
def SepeechRecognition():
    driver.get(Link)  # Opening the speech recognition webpage
    driver.find_element(By.ID, "start").click()  # Clicking the 'Start Recognition' button

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text  # Getting recognized text from webpage

            if Text:  # If text is detected
                driver.find_element(By.ID, "end").click()  # Clicking 'Stop Recognition' button
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)  # Return modified query if already in English
                else:
                    SetAssistantStatus("Translating...")  # Update status to 'Translating...'
                    return QueryModifier(UniversalTranslator(Text))  # Translate and return modified query
                    
        except Exception as e:
            pass  # Ignore exceptions and continue

# Main execution block
if __name__ == "__main__":
    while True:
        Text = SepeechRecognition()  # Continuously recognize speech
        print(Text)  # Print recognized text



