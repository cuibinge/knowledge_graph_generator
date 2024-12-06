import sys
from tkinter.tix import TEXT
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QListWidget, QStackedWidget,
                             QFileDialog, QLineEdit, QSizePolicy, QFormLayout,
                             QDialog,QTextEdit,QListWidgetItem)
from PyQt5.QtGui import QPalette, QBrush, QColor, QPixmap,QPainter
from PyQt5.QtCore import Qt,QThread, pyqtSignal,QCoreApplication
from PyQt5 import QtCore
from PyQt5 import uic
from QCandyUi.CandyWindow import colorful
from Dictionary import EN_to_CN, CN_to_EN  
from dotenv import load_dotenv
from knowledge_graph_builder import KnowledgeGraphBuilder, GroqClient, KGToNeo4j
from KGGenerate import define_ERontology,define_EAontology,export_to_directory
import pandas as pd
import os
# Load the configuration in the .env file
load_dotenv()


class ExtractionThread(QThread):
    log_signal = pyqtSignal(str)  

    def __init__(self, inputdir_path, save_path, erontology, eaontology, llm):
        super().__init__()
        self.inputdir_path = inputdir_path
        self.save_path = save_path
        self.erontology = erontology
        self.eaontology = eaontology
        self.llm = llm

    def run(self):
        self.log_signal.emit("Received user input file: Start extracting the Entity Relationship Knowledge Graph")
        QApplication.processEvents()  
        self.ERKGgenerate(self.inputdir_path)
        self.log_signal.emit("Received user input file: Start extracting Entity Attributes Knowledge Graph")
        QApplication.processEvents()  
        self.EAKGgenerate(self.inputdir_path)

    def ERKGgenerate(self, inputdir_path):
        ERKGBuilder = KnowledgeGraphBuilder(ontology=self.erontology, llm_client=self.llm)
        for filename in os.listdir(inputdir_path):
            if filename.endswith(".txt"):
                input_file = os.path.join(inputdir_path, filename)
                with open(input_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    user_text = ["\n" + line.strip() + "\n" for line in lines if line.strip()]
                docs = ERKGBuilder.create_docs(user_text)
                
                ERKnowledgeGraph = ERKGBuilder.documents_to_graph(list(docs), delay=0)
                for item in ERKnowledgeGraph:
                    self.log_signal.emit(str(item))
                    QApplication.processEvents()  
                if self.save_path:
                    export_to_directory(ERKnowledgeGraph, self.erontology, self.save_path)
                    self.log_signal.emit(f"Entity relationship triples have been extracted from {filename} to {self.save_path}")
                else:
                    self.log_signal.emit("The save path is not selected, please select the save path.")
                QApplication.processEvents()  
        self.log_signal.emit("All entity relationship triples have been extracted and successfully exported to the Excel file.")

    def EAKGgenerate(self, inputdir_path):
        EAKGBuilder = KnowledgeGraphBuilder(ontology=self.eaontology, llm_client=self.llm)
        for filename in os.listdir(inputdir_path):
            if filename.endswith(".txt"):
                input_file = os.path.join(inputdir_path, filename)
                with open(input_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    user_text = ["\n" + line.strip() + "\n" for line in lines if line.strip()]
                docs = EAKGBuilder.create_docs(user_text)
                
                EAKnowledgeGraph = EAKGBuilder.documents_to_graph(list(docs), delay=0)
                for item in EAKnowledgeGraph:
                    self.log_signal.emit(str(item))
                    QApplication.processEvents()  
                if self.save_path:
                    export_to_directory(EAKnowledgeGraph, self.eaontology, self.save_path)
                    self.log_signal.emit(f"Entity attributes triples have been extracted from {filename} to {self.save_path}")
                else:
                    self.log_signal.emit("The save path is not selected, please select the save path.")
                QApplication.processEvents()  
        self.log_signal.emit("All entity attributes triples have been extracted and successfully exported to the Excel file.")


class GenerateThread(QThread):
    log_signal = pyqtSignal(str)  

    def __init__(self, selected_inputdir_path, uri, username, password, erontology, eaontology):
        super().__init__()
        self.selected_inputdir_path = selected_inputdir_path
        self.uri = uri
        self.username = username
        self.password = password
        self.erontology = erontology
        self.eaontology = eaontology

    def run(self):
        self.log_signal.emit("Start passing user-supplied triples into the Neo4j database")
        QCoreApplication.processEvents()  
        self.start_generation(self.selected_inputdir_path)

    def start_generation(self, selected_inputdir_path):
        KGNeo4j = KGToNeo4j(self.uri, self.username, self.password)
        if selected_inputdir_path:  
            for filename in os.listdir(selected_inputdir_path):
                file_path = os.path.join(selected_inputdir_path, filename)
                if os.path.isfile(file_path) and filename.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_path)
                    if 'relationship' in df.columns[2]:  
                        KGNeo4j.graph_to_neo4j(self.erontology, file_path)
                        self.log_signal.emit(f"Successfully passed Entity relationship triples into the Neo4j database for file {filename}.")
                    elif 'attribute' in df.columns[2]:
                        KGNeo4j.graph_to_neo4j(self.eaontology, file_path)
                        self.log_signal.emit(f"Successfully passed Entity attribute triples into the Neo4j database for file {filename}.")
                    else:
                        self.log_signal.emit(f"Unknown ontology type for file {filename}.")
                else:
                    self.log_signal.emit(f"Skipped non-Excel file {filename}.")
            self.log_signal.emit("All files have been successfully imported into the Neo4j database, please check in Neo4j.")
        else:
            self.log_signal("No directory path selected.")
    

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Knowledge Graph Construction')
        self.setGeometry(100, 100, 800, 600)

        # Background image settings
        palette = QPalette()
        pixmap = QPixmap("ui-image/bg1.jpg")
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

        # Set Style Sheet
        self.setStyleSheet(self.get_style_sheet())
        # top layout
        title_layout = QHBoxLayout()
        title_label = QLabel('Welcome To Knowledge Graph Maker！', self)
        title_layout.addStretch(1)
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)

        # bottom layout
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        enter_button = QPushButton('Start', self)
        button_layout.addWidget(enter_button)

        # main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(title_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        enter_button.clicked.connect(self.show_second_window)

    def get_style_sheet(self):
        return """
                QLabel {
                    font-family: Times New Roman;
                    font-size: 24px;
                    color: white;
                }
                QPushButton {
                    font-family: Times New Roman;
                    font-size: 16px;
                    color: white;
                    background-color: #007BFF;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    letter-spacing: 1px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """

    def show_second_window(self):
        self.second_window = SecondWindow(self)
        self.second_window.show()


class SecondWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # The default language is English
        self.language = "en"  
        self.initUI()
        self.uri = "bolt://localhost:7687"
        self.model = "llama3-70b-8192"
        self.erontology = define_ERontology()
        self.eaontology = define_EAontology()
        self.LLM = GroqClient(model=self.model, temperature=0.1, top_p=0.5)
        self.selected_file_path = ""
        self.save_path=""
   
    def initUI(self):
        self.setWindowTitle('Knowledge Graph Construction - Operation Interface')
        self.setGeometry(100, 100, 800, 600)

        # main layout
        main_layout = QHBoxLayout()

        # Create a sidebar (QListWidget)
        sidebar = QListWidget()
        sidebar.setFixedWidth(150)
        sidebar.setStyleSheet("font-family: Times New Roman; background-color: darkgray; color: black; font-size: 18px; padding: 10px 0;")

        # Add an image to the top of the sidebar
        image_label = QLabel()
        pixmap = QPixmap('ui-image/ITRS.jpg')  
        pixmap = pixmap.scaled(150, 150, aspectRatioMode=1)  
        image_label.setPixmap(pixmap)

        # Create a QListWidgetItem and add an image to it
        image_item = QListWidgetItem()
        image_item.setSizeHint(image_label.sizeHint())  
        sidebar.addItem(image_item)  
        sidebar.setItemWidget(image_item, image_label) 

        # Add other list items
        sidebar_items = ["Home", "Extract Triples", "Generate Knowledge Graph", "Language Settings"]
        for item in sidebar_items:
            sidebar.addItem(item)
        
         # Connect the click signal of a list item to the slot function
        sidebar.currentRowChanged.connect(self.changePage)
        # stacker
        self.stacked_widget = QStackedWidget()

        # Add a sidebar to the main layout
        main_layout.addWidget(sidebar)

        # Set the main layout
        self.setLayout(main_layout)

        '''
        first interface
        '''
      
        home_page = QWidget()
        home_page.setStyleSheet("background-color: rgba(255, 255, 255, 0);")  
        home_layout = QVBoxLayout(home_page)

        use_method_label = QLabel(self.get_label_text("Usage Instructions"), home_page)
        use_method_label.setStyleSheet("font-family: Times New Roman; font-weight: bold;font-size: 28px; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);")

        web_view = QWebEngineView()
        web_view.setStyleSheet("background: transparent; border: none;")  
        web_view.setWindowOpacity(0)


        html_content = self.get_html_content()
        web_view.setHtml(html_content)

        # Create a container widget to place tabs and web views, and style them to place in the background
        container_widget = QWidget()
        container_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)  

        container_layout = QVBoxLayout(container_widget)
        container_layout.addWidget(use_method_label, alignment=Qt.AlignTop | Qt.AlignLeft)
        container_layout.addSpacing(15)
        container_layout.addWidget(web_view)
        container_widget.setLayout(container_layout)


        # Add container_widget to the main layout
        home_layout.addWidget(container_widget)
        container_widget.lower()  
        home_page.setLayout(home_layout)

        '''
        extract page
        '''
        extraction_page = QWidget()
        extraction_layout = QVBoxLayout()
        # top tab
        extraction_label = QLabel(
            "Please select the file to extract triples and the path to save the extracted triples.", extraction_page)
        extraction_label.setStyleSheet("font-family: Times New Roman; font-weight: bold;font-size: 24px; text-align: left; ")
        extraction_layout.addWidget(extraction_label, alignment=Qt.AlignTop | Qt.AlignLeft)

        
    
        # Extract triplet input path selection
        path_selection_layout = QHBoxLayout()
        self.inputdir_path_line = QLineEdit()
        self.inputdir_path_line.setPlaceholderText("InputDir Path...")
        
        #self.inputdir_path_line.setMinimumWidth(300)
        self.inputdir_path_line.setFixedWidth(600)  
        self.inputdir_path_line.setFixedHeight(40)  
        self.inputdir_path_line.setStyleSheet("QLineEdit { font-size: 18px; text-align: left; }")
        self.inputdir_path_line.setStyleSheet(self.text_style_sheet())
        # Select input path button
        choose_inputdir_button = QPushButton(self.get_label_text("Choose InputDir..."))  
        choose_inputdir_button.clicked.connect(self.choose_inputdir)
        choose_inputdir_button.setStyleSheet("font-size: 14px;")
        choose_inputdir_button.setFixedWidth(220) 
        choose_inputdir_button.setFixedHeight(40) 
        choose_inputdir_button.setStyleSheet(self.choosebutton_style_sheet())
        #path_selection_layout.addStretch()
        path_selection_layout.addWidget(self.inputdir_path_line)
        path_selection_layout.addSpacing(10)
        path_selection_layout.addWidget(choose_inputdir_button)
        path_selection_layout.addStretch()
        #extraction_layout.addLayout(path_selection_layout)  

        
        # Extract Triple Output Path Select Layout
        path_selection_layout2 = QHBoxLayout()
        self.save_path_line_edit = QLineEdit()  
        self.save_path_line_edit.setPlaceholderText("Save Path...")
        self.save_path_line_edit.setFixedWidth(600)  
        self.save_path_line_edit.setFixedHeight(40) 
        self.save_path_line_edit.setStyleSheet("QLineEdit { font-size: 18px; text-align: left; }")
        self.save_path_line_edit.setStyleSheet(self.text_style_sheet())
        # Select the Save Path button
        choose_save_path_button = QPushButton(self.get_label_text("Choose Save Path..."))  
        choose_save_path_button.clicked.connect(self.choose_save_path)
        choose_save_path_button.setStyleSheet("font-size: 14px;")
        choose_save_path_button.setFixedWidth(220)  
        choose_save_path_button.setFixedHeight(40)
        choose_save_path_button.setStyleSheet(self.choosebutton_style_sheet())
        #path_selection_layout2.addStretch()
        path_selection_layout2.addWidget(self.save_path_line_edit)
        path_selection_layout2.addSpacing(10)
        path_selection_layout2.addWidget(choose_save_path_button)
        path_selection_layout2.addStretch()
        
        path_selection_Vlayout = QVBoxLayout()
        path_selection_Vlayout.addStretch()
        path_selection_Vlayout.addLayout(path_selection_layout)
        path_selection_Vlayout.addSpacing(50)
        path_selection_Vlayout.addLayout(path_selection_layout2)
        path_selection_Vlayout.addStretch()

        extraction_layout.addLayout(path_selection_Vlayout)
        #extraction_layout.addLayout(path_selection_layout2)  

        

        # Bottom Start Extraction button centered
        start_extraction_button = QPushButton(self.get_label_text("Start Extraction"))
        start_extraction_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        start_extraction_button.clicked.connect(self.start_extraction)
        start_extraction_button.setStyleSheet(self.get_style_sheet())
        start_extraction_button.setFixedWidth(220)  
        start_extraction_button.setFixedHeight(40) 

        extraction_layout.addWidget(start_extraction_button, alignment=Qt.AlignBottom | Qt.AlignHCenter)

        # Set the main layout
        extraction_page.setLayout(extraction_layout)

        # Set background image
        self.background_pixmap = QPixmap("ui-image/bg2.jpg") 


       
        '''
        Generative Knowledge Graph page
        '''
       
        # Create a build page
        generation_page = QWidget()
        generation_layout = QVBoxLayout()

        # Generating Labels for Knowledge Graph
        generation_label_top = QLabel(self.get_label_text("Generate Knowledge Graph"), generation_page)
        generation_label_top.setStyleSheet("font-family: Times New Roman; font-weight: bold;font-size: 25px; text-align: left; ")
        generation_layout.addWidget(generation_label_top, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Select the label of the triple file
        select_triple_label = QLabel(self.get_label_text("Please choose your file to generate Knowledge Graph."), generation_page)
        select_triple_label.setStyleSheet("font-family: Times New Roman; font-size: 24px;")
        select_triple_label.setFixedWidth(600)
        select_triple_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        H_layout = QHBoxLayout()
        H_layout.addWidget(select_triple_label)
        H_layout.addStretch(1)

        # Create a vertical layout for placing labels and text boxes + buttons
        generate_Vlayout = QVBoxLayout()
        generate_Hlayout = QHBoxLayout()

        # Create file path box and select file button
        self.triple_directory_line_edit = QLineEdit()
        self.triple_directory_line_edit.setPlaceholderText("Triple’s Path....")  
        self.triple_directory_line_edit.setFixedWidth(600)  
        self.triple_directory_line_edit.setFixedHeight(40)  
        self.triple_directory_line_edit.setStyleSheet("QLineEdit { font-size: 18px}")
        self.triple_directory_line_edit.setStyleSheet(self.text_style_sheet())

        choose_generation_dir_button = QPushButton(self.get_label_text("Select Triple Path..."))
        choose_generation_dir_button.setFixedWidth(200)  
        choose_generation_dir_button.setFixedHeight(40)  
        choose_generation_dir_button.clicked.connect(self.choose_generation_dir)
        choose_generation_dir_button.setStyleSheet(self.choosebutton_style_sheet())
        
        generate_Hlayout.addWidget(self.triple_directory_line_edit)
        generate_Hlayout.addSpacing(10)
        generate_Hlayout.addWidget(choose_generation_dir_button)
        generate_Hlayout.addStretch()

        generate_Vlayout.addStretch()
        generate_Vlayout.addLayout(H_layout)
        generate_Vlayout.addSpacing(5)
        generate_Vlayout.addLayout(generate_Hlayout)
        generate_Vlayout.addStretch()

        generation_layout.addLayout(generate_Vlayout)
        generation_layout.addSpacing(50)

       # Add a tag for database information
        database_info_label = QLabel(self.get_label_text("Please enter your Neo4j database username and password."))
        database_info_label.setStyleSheet("font-family: Times New Roman; font-size: 24px;")
        database_info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        generation_layout.addWidget(database_info_label)

        # Use QFormLayout to align labels and text boxes
        auth_layout = QFormLayout()
        self.username_line_edit = QLineEdit()
        self.username_line_edit.setFixedWidth(700)  
        self.username_line_edit.setFixedHeight(40)  
        self.username_line_edit.setStyleSheet(self.text_style_sheet())

        self.password_line_edit = QLineEdit()
        self.password_line_edit.setFixedWidth(700) 
        self.password_line_edit.setFixedHeight(40)  
        self.password_line_edit.setStyleSheet(self.text_style_sheet())
        self.password_line_edit.setEchoMode(QLineEdit.Password)

        username_label = QLabel(self.get_label_text("Account:"))
        username_label.setStyleSheet("font-family: Times New Roman; font-weight: bold; font-size: 24px;")
        password_label = QLabel(self.get_label_text("Password:"))
        password_label.setStyleSheet("font-family: Times New Roman; font-weight: bold; font-size: 24px;")

        # Add labels and text boxes to the form layout and set label left alignment
        auth_layout.addRow(username_label, self.username_line_edit)
        auth_layout.addRow(password_label, self.password_line_edit)

        # Create and set auth_widget layout
        auth_widget = QWidget()
        V_auth_layout = QVBoxLayout()  
        V_auth_layout.addLayout(auth_layout)  

        # Set auth_widget layout
        auth_widget.setLayout(V_auth_layout) 

        # Add auth_widget to the build layout and set the alignment
        generation_layout.addWidget(auth_widget, alignment=Qt.AlignmentFlag.AlignLeft)

        # Add a button to start generating
        generate_button = QPushButton(self.get_label_text("Start Generating"))
        generate_button.setFixedWidth(220)  
        generate_button.setFixedHeight(40)  
        generate_button.setStyleSheet(self.get_style_sheet())
        generate_button.clicked.connect(self.start_generation)  

        # Add a button to the layout
        generation_layout.addWidget(generate_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the main layout of the generated page
        generation_page.setLayout(generation_layout)

        # Additional adjustments to reduce spacing between labels and text boxes
        auth_layout.setVerticalSpacing(30) 
        generation_layout.setSpacing(20)  
        '''
        language settings page
        '''
        language_page = QWidget()
        language_layout = QVBoxLayout()
        language_label = QLabel(self.get_label_text("Select Your Language"))
        language_label.setStyleSheet("font-family: Times New Roman; font-weight: bold;font-size: 25px;")
        language_layout.addWidget(language_label)

        english_button = QPushButton(self.get_label_text("English"))
        english_button.clicked.connect(lambda: self.set_language("en"))
        english_button.setFixedWidth(400) 
        english_button.setFixedHeight(40) 
        english_button.setStyleSheet(self.language_style_sheet())
        chinese_button = QPushButton(self.get_label_text("中文"))
        chinese_button.clicked.connect(lambda: self.set_language("zh"))
        chinese_button.setFixedWidth(400) 
        chinese_button.setFixedHeight(40)  
        chinese_button.setStyleSheet(self.language_style_sheet())
        en_layout = QHBoxLayout()
        en_layout.addStretch(1)
        en_layout.addWidget(english_button)
        en_layout.addStretch(1)
        zn_layout = QHBoxLayout()
        zn_layout.addStretch(1)
        zn_layout.addWidget(chinese_button)
        zn_layout.addStretch(1)
        #language_layout.addStretch(1)
        language_layout.addStretch(1)
        language_layout.addLayout(en_layout)
        language_layout.addSpacing(30)
        language_layout.addLayout(zn_layout)
        language_layout.addStretch(1)
        language_page.setLayout(language_layout)

        # Add all pages to the stacked widget
        self.stacked_widget.addWidget(home_page)
        self.stacked_widget.addWidget(extraction_page)
        self.stacked_widget.addWidget(generation_page)
        self.stacked_widget.addWidget(language_page)

        #main_layout.addWidget(sidebar)
        #main_layout.addWidget(self.stacked_widget)

        # Set the main layout
        self.setLayout(main_layout)
        back_button_layout = QHBoxLayout()
        back_button_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        back_button = QPushButton(self.get_label_text('Back to Home'), self)
        back_button.clicked.connect(self.go_back_to_main)
        back_button_layout.addWidget(back_button)
        back_button.setFixedWidth(150)  
        back_button.setFixedHeight(40) 
        back_button.setStyleSheet(self.back2_style_sheet())
        #main_layout.addLayout(back_button_layout)

        V_layout = QVBoxLayout()
        V_layout.setAlignment(Qt.AlignLeft)
        V_layout.addWidget(sidebar)
        V_layout.addLayout(back_button_layout)
        
        main_layout.addLayout(V_layout)
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw the background image and set the transparency
        painter.setOpacity(0.5) 
        painter.drawPixmap(self.rect(), self.background_pixmap)
    
    def changePage(self, index):
        # Since the image item occupies the first index, subtract 1. 1
        adjusted_index = index - 1
        self.stacked_widget.setCurrentIndex(adjusted_index)

            
   
    # The user selects the input path and prints the path to see if the input is successful.
    def choose_inputdir(self):
        inputdir_path = QFileDialog.getExistingDirectory(self, self.get_label_text("Select Directory"), "", QFileDialog.ShowDirsOnly)
        if inputdir_path:
            print(f"select input directory:{inputdir_path}")
            self.inputdir_path_line.setText(inputdir_path)
            self.inputdir_path = inputdir_path
            

    # The user selects the output directory and prints the path to see if the input is successful.
    def choose_save_path(self):
        save_path = QFileDialog.getExistingDirectory(self, self.get_label_text("Select Save Path"), "", QFileDialog.ShowDirsOnly)
        if save_path:
            print(f"select directory:{save_path}")
            self.save_path_line_edit.setText(save_path)
            self.save_path = save_path  
   
    # The user clicks the Start Extraction button to extract the entity relationship triplet and the entity attribute triplet in turn
    def start_extraction(self):
        inputdir_path = self.inputdir_path_line.text()
        if not inputdir_path:
            print("No input path selected, please select the input path first.")
            return

        # Show Extraction Progress dialog box
        self.progress_dialog = QDialog(self)
        self.progress_dialog.setWindowTitle("extraction progress")
        self.progress_dialog.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout()
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        layout.addWidget(self.log_text_edit)
        self.progress_dialog.setLayout(layout)
        self.progress_dialog.show()

        # Create a background thread and start it
        self.extraction_thread = ExtractionThread(inputdir_path, self.save_path_line_edit.text(), self.erontology, self.eaontology, self.LLM)
        self.extraction_thread.log_signal.connect(self.log_message)
        self.extraction_thread.start()

   
    def log_message(self, message):
        self.log_text_edit.append(message)
        QApplication.processEvents()  

    # Generate Knowledge Graph interface, user-supplied triple files
    def choose_generation_dir(self):
        selected_inputdir_path = QFileDialog.getExistingDirectory(self, self.get_label_text("Select Triple Path"), "", QFileDialog.ShowDirsOnly)
        if selected_inputdir_path:
            print(f"Selected input triple path: {selected_inputdir_path}")
            self.selected_inputdir_path = selected_inputdir_path  
            self.triple_directory_line_edit.setText(self.selected_inputdir_path) 

    def go_back_to_main(self):
        self.main_window.show()
        self.close()
    
    def show_next_generation_page(self):
        self.stacked_widget.setCurrentIndex(3)
    def return_to_first_page(self):
        self.stacked_widget.setCurrentIndex(2) 


    # Pass a user-supplied triplet file into Neo4j
    def start_generation(self):

        username = self.username_line_edit.text()
        password = self.password_line_edit.text()
        print(f"Username: {username}, Password: {password}")

        
        # Show Extraction Progress dialog box
        self.progress_dialog = QDialog(self)
        self.progress_dialog.setWindowTitle("extraction progress")
        self.progress_dialog.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout()
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        layout.addWidget(self.log_text_edit)
        self.progress_dialog.setLayout(layout)
        self.progress_dialog.show()

        # Create a background thread and start it
        self.extraction_thread = GenerateThread(self.selected_inputdir_path, self.uri, username, password, self.erontology, self.eaontology)
        self.extraction_thread.log_signal.connect(self.log_message) 
        self.extraction_thread.start()
        
        
       

    def set_language(self, language):
        self.language = language
        self.update_ui()

    def update_ui(self):
    # Set window title
        self.setWindowTitle(self.get_label_text("Knowledge Graph Construction - Operation Interface"))

        # Update the text of the homepage
        home_page = self.stacked_widget.widget(0)  
        home_page.findChild(QLabel).setText(self.get_label_text("Usage Instructions"))
        home_page.findChild(QWebEngineView).setHtml(self.get_html_content())
        # Update extraction page
        extraction_page = self.stacked_widget.widget(1)
        extraction_label = extraction_page.findChild(QLabel)
        extraction_label.setText(self.get_label_text("Please select the file to extract triples and the path to save the extracted triples."))
        
        # Update the control that extracts triples
        extraction_page.findChildren(QPushButton)[0].setText(self.get_label_text("Choose InputDir..."))
        extraction_page.findChildren(QPushButton)[1].setText(self.get_label_text("Choose Save Path..."))
        extraction_page.findChildren(QPushButton)[2].setText(self.get_label_text("Start Extraction"))

        # Update the Generated Knowledge Graph page
        generation_page = self.stacked_widget.widget(2)

        # Update page title
        generation_page.findChild(QLabel).setText(self.get_label_text("Generate Knowledge Graph"))

        # Update Select File Tab
        select_file_label = generation_page.findChildren(QLabel)[1]  
        select_file_label.setText(self.get_label_text("Please choose your file to generate Knowledge Graph."))

        # Update placeholder for file path box
        triple_line_edit = generation_page.findChild(QLineEdit)  
        triple_line_edit.setPlaceholderText("Triple’s Path....")

        # Update the text of the Select File button
        choose_generation_button = generation_page.findChildren(QPushButton)[0]  
        choose_generation_button.setText(self.get_label_text("Select Triple Path..."))

        # Update Start generating the text of the button
        start_generation_button = generation_page.findChildren(QPushButton)[1]  
        start_generation_button.setText(self.get_label_text("Start Generating"))

        # Update the database information section
        database_info_label = generation_page.findChildren(QLabel)[2]  
        database_info_label.setText(self.get_label_text("Please enter your Neo4j database username and password."))

        # Update username and password tags
        labels = generation_page.findChildren(QLabel)
        labels[3].setText(self.get_label_text("Account:"))  
        labels[4].setText(self.get_label_text("Password:"))  

        # Update homepage back button
        self.findChild(QPushButton).setText(self.get_label_text("Back to Home"))

        # Update the language settings interface
        language_page = self.stacked_widget.widget(3)
        language_page.findChild(QLabel).setText(self.get_label_text("Select Your Language"))
        
        language_buttons = language_page.findChildren(QPushButton)
        language_buttons[0].setText(self.get_label_text("English"))
        language_buttons[1].setText(self.get_label_text("中文"))

    def get_label_text(self, en_text):
        if self.language == "en":
            return en_text
        elif self.language == "zh":
            return EN_to_CN.get(en_text, en_text)
    
    def get_style_sheet(self):
        return """
                QPushButton {
                    font-family: Times New Roman;
                    background-color: lightskyblue;
                    color: black; 
                    border: 1px solid black;
                    border-radius: 10px; 
                    padding: 10px 30px; 
                    font-size: 16px; 
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); 
                    letter-spacing: 1px;
                    transition: all 0.3s ease; 
                }
                QPushButton:hover {
                    background-color: skyblue;
                    transform: scale(1.05); 
                }
                QPushButton:pressed {
                    background-color: deepskyblue; 
                    transform: scale(0.95); 
                }
            """

    def text_style_sheet(self):
        return """
            QLineEdit {
                font-family: Times New Roman;
                border-radius: 5px;
                border: 1px solid black;
                background-color: white;
                letter-spacing: 1px;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid lightskyblue;
            }
            QLineEdit:hover {
                border: 1px solid gray;
            }
            """

    def choosebutton_style_sheet(self):
        return """
                QPushButton {
                    font-family: Times New Roman;
                    background-color: lightyellow;
                    color: black; 
                    border: 1px solid black;
                    border-radius: 10px; 
                    padding: 10px 30px; 
                    font-size: 16px; 
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); 
                    letter-spacing: 1px;
                    transition: all 0.3s ease; 
                }
                QPushButton:hover {
                    background-color: lemonchiffon;
                    transform: scale(1.05); 
                }
                QPushButton:pressed {
                    background-color: ivory; 
                    transform: scale(0.95); 
                }
            """
            
    def back2_style_sheet(self):
        return """
                QPushButton {
                    font-family: Times New Roman;
                    background-color: peachpuff;
                    color: black; 
                    border: 1px solid black; 
                    border-radius: 10px; 
                    padding: 10px 30px; 
                    font-size: 14px; 
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); 
                    transition: all 0.3s ease; 
                }
                QPushButton:hover {
                    background-color: navajowhite;
                    transform: scale(1.05); 
                }
                QPushButton:pressed {
                    background-color: antiquewhite; 
                    transform: scale(0.95); 
                }
            """
    def language_style_sheet(self):
        return """
                QPushButton {
                    font-family: Times New Roman;
                    background-color: honeydew;
                    color: black; 
                    border: 1px solid black; 
                    border-radius: 10px; 
                    padding: 10px 30px; 
                    font-size: 16px; 
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); 
                    letter-spacing: 1px;
                    transition: all 0.3s ease; 
                }
                QPushButton:hover {
                    background-color: lightgreen;
                    transform: scale(1.05); 
                }
                QPushButton:pressed {
                    background-color: honeydew; 
                    transform: scale(0.95); 
                }
            """

    def get_html_content(self):
        if self.language == "en":
            return """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Knowledge Graph Construction Program</title>
                        <style>
                            body {
                                background-color: rgba(255,255,255, 0); 
                                margin: 0;
                                padding: 10x;
                                opacity:1;
                                
                            }
                            .welcome-message {
                                background-color: rgba(255,255,255, 0);
                                text-align: center;
                                font-size: 24px;
                                color: #444;
                                margin-top: 20px;
x                            }
                            .small-text {
                                background-color: rgba(255,255,255, 0); 
                                font-size: 18px;
                                color: #666;
                            }
                            p {
                                margin-bottom: 15px;
                                text-align: justify;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="welcome-message">
                            Welcome to use the knowledge graph construction program. You can do the following things with this program.
                        </div>
                        <hr style="border: 1px solid #ddd; margin: 15px 0;">
                        <p class="small-text">1. Easily extract key information from data and construct knowledge triples.</p>
                        <p style="text-indent: 2em;">You can select the document from which you want to extract triples on the triple extraction interface. After selection, click "Start Extraction" to generate a triple document for constructing your knowledge graph.</p>
                        <hr style="border: 1px solid #ddd; margin: 15px 0;">
                        <p class="small-text">2. Efficiently generate visualized knowledge graphs to facilitate knowledge insight and decision-making.</p>
                        <p style="text-indent: 2em;">You can use the generated triples to generate the corresponding visualized knowledge graph. You only need to select your triple file and click "Start Generation" to generate your knowledge graph!</p>
                    </body>
                    </html>
                    """
        else:
            return """
                    <!DOCTYPE html>
                    <html lang="zh">
                    <head>
                        <meta charset="UTF-8">
                        <title>知识图谱构建程序</title>
                        <style>
                            body {
                                background-color: transparent; /* 设置背景为透明 */
                                margin: 0;
                                padding: 0;
                            }
                            .welcome-message {
                                text-align: center;
                                font-size: 24px;
                                color: #444;
                                margin-top: 20px;
                            }
                            .small-text {
                                font-size: 18px;
                                color: #666;
                            }
                            p {
                                margin-bottom: 15px;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="welcome-message">
                            欢迎使用知识图谱构建程序。您可以用这个程序做以下事情。
                        </div>
                        <hr style="border: 1px solid #ddd; margin: 15px 0;">
                        <p class="small-text">1. 从数据中轻松提取关键信息并构建知识三元组。</p>
                        &nbsp;&nbsp;<p style="text-indent: 2em;">您可以在三元组提取界面选择您想要提取三元组的文档。选择后，点击“开始提取”以生成用于构建您的知识图谱的三元组文档。</p>
                        <hr style="border: 1px solid #ddd; margin: 15px 0;">
                        <p class="small-text">2. 高效生成可视化的知识图谱，以促进知识洞察和决策。</p>
                        &nbsp;&nbsp;<p style="text-indent: 2em;">您可以使用生成的三元组生成相应的可视化知识图谱。您只需要选择您的三元组文件，然后点击“开始生成”即可生成您的知识图谱！</p>
                    </body>
                    </html>
                """



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())