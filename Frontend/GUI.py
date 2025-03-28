from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QVBoxLayout, QGridLayout, QPushButton, QFrame, QLabel, QSizePolicy,QHBoxLayout
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

evn_vars = dotenv_values(".env")
Assistantname = evn_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "where", "when", "why", "which", "who", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data',"w",encoding="utf-8") as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data',"r",encoding="utf-8") as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data',"w",encoding="utf-8") as file:
        file.write(Status)
        
def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data',"r",encoding="utf-8") as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    path = rf'{GraphicsDirPath}\{Filename}'
    return path

def TempDireectoryPath(Filename):
    path =rf'{TempDirPath}\{Filename}'
    return path

# def ShowTextToScreen(Text):
#     with open(rf'{TempDirPath}\Responses.data',"w",encoding='utf-8') as file:
#         file.write(Text)

def ShowTextToScreen(Text):
    try:
        with open(TempDireectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(Text)
    except Exception as e:
        print(f"Error writing to Responses.data: {e}")

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-20, 40, 40, 100)
        layout.setSpacing(-100)
        
        # Chat Text Edit
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        
        # Set background color
        self.setStyleSheet("background-color: black;")
        
        # Layout constraints
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        
        # Text color for chat
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        
        # GIF Label (Bottom-Right Corner)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('AI.gif'))
        
        # Make the GIF square-shaped
        max_gif_size = 200  # Square size
        movie.setScaledSize(QSize(max_gif_size, max_gif_size))
        
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)
        
        # Status Label
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        
        # Adjust spacing
        layout.setSpacing(-10)
        
        # Set font for chat text
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        
        # Timer for loading messages and speech recognition
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
        
        # Event filter for chat text edit
        self.chat_text_edit.viewport().installEventFilter(self)
        
        # Custom scrollbar styling
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
                             
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
                             
            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
            }
                             
            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
            }
                             
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }
                             
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Mic icon toggle functionality
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(60, 60)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()  # Initialize the icon
        layout.addWidget(self.icon_label)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDireectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()

            # Only update if the message has changed
                if messages and messages != old_chat_message:
                    self.addMessage(message=messages, color='White')
                    old_chat_message = messages
        except Exception as e:
            print(f"Error loading messages: {e}")
    
    def SpeechRecogText(self):
        try:
            with open(TempDireectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except Exception as e:
            print(f"Error loading speech recognition text: {e}")
    
    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        
        # Apply the text format
        cursor.setCharFormat(format)
        
        # Insert the message
        cursor.insertText(message + "\n")
        
        # Scroll to the bottom
        self.chat_text_edit.setTextCursor(cursor)
        self.chat_text_edit.ensureCursorVisible()
    
    def load_icon(self, path, width=60, height=60):
        try:
            pixmap = QPixmap(path)
            if pixmap.isNull():
                print(f"Error: Failed to load icon from {path}")
                return
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)
        except Exception as e:
            print(f"Error loading icon: {e}")
    
    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # GIF Label (Centered)
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('AI.gif'))
        
        # Make the GIF square-shaped
        max_gif_size = int(min(screen_width, screen_height) * 0.6) 
        movie.setScaledSize(QSize(max_gif_size, max_gif_size))
        
        gif_label.setMovie(movie)
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        
        # Mic Icon Label
        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('Mic_on.png'))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(250, 250)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        
        # Status Label
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        # Set layout
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        
        # Timer for speech recognition
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
    
    def SpeechRecogText(self):
        with open(TempDireectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)
    
    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)
    
    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        
        # Chat Section
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        
        # Set layout
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()
    
    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)  # Use QHBoxLayout for horizontal alignment
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)  # Add spacing between buttons
        
        # Title Label
        title_label = QLabel(f"{str(Assistantname).capitalize()} AI    ")
        title_label.setStyleSheet("color: black; font-size: 18px; background: white; padding: 5px;")
        layout.addWidget(title_label)
        
        # Add stretch to center buttons
        layout.addStretch(1)
        
        # Home Button
        home_button = QPushButton("Home")
        home_button.setIcon(QIcon(GraphicsDirectoryPath('Home.png')))
        home_button.setStyleSheet("""
            QPushButton {
                height: 40px;
                line-height: 40px;
                background-color: white;
                color: black;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(home_button)
        
        # Chat Button
        chat_button = QPushButton("Chat")
        chat_button.setIcon(QIcon(GraphicsDirectoryPath('Chats.png')))
        chat_button.setStyleSheet("""
            QPushButton {
                height: 40px;
                line-height: 40px;
                background-color: white;
                color: black;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        chat_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(chat_button)
        
        # Add stretch to center buttons
        layout.addStretch(1)
        
        # Minimize Button
        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(GraphicsDirectoryPath('Minimize2.png')))
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        minimize_button.clicked.connect(self.parent().showMinimized)
        layout.addWidget(minimize_button)
        
        # Maximize Button
        self.maximize_button = QPushButton()
        self.maximize_button.setIcon(QIcon(GraphicsDirectoryPath('Maximize.png')))
        self.maximize_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.maximize_button.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.maximize_button)
        
        # Close Button
        close_button = QPushButton()
        close_button.setIcon(QIcon(GraphicsDirectoryPath('Close.png')))
        close_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        close_button.clicked.connect(self.parent().close)
        layout.addWidget(close_button)
        
        # Draggable window functionality
        self.draggable = True
        self.offset = None
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)
    
    def toggle_maximize(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(QIcon(GraphicsDirectoryPath('Maximize.png')))
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(QIcon(GraphicsDirectoryPath('minimize.png')))
    
    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()
    
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Stacked Widget for Home and Chat Screens
        self.stacked_widget = QStackedWidget(self)
        
        # Home Screen
        self.initial_screen = InitialScreen()
        self.stacked_widget.addWidget(self.initial_screen)
        
        # Chat Screen
        self.message_screen = MessageScreen()
        self.stacked_widget.addWidget(self.message_screen)
        
        # Top Bar
        self.top_bar = CustomTopBar(self, self.stacked_widget)
        
        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_layout.addWidget(self.top_bar)
        main_layout.addWidget(self.stacked_widget)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()
