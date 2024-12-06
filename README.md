#   Knowledge Graph Generator
## Project Introduction
**Knowledge Graph Generator** can assist us in efficiently generating entity-relationship triplets and entity-attribute triplets for building knowledge graphs by utilizing **LLM**. Additionally, it enables us to establish a connection with the **Neo4j** database and write the generated triplets into it, thereby facilitating the rapid generation of knowledge graphs.**In addition, we have developed a UI tool to facilitate users in completing the aforementioned tasks.**

## Software Environmental Requirement
 - **Operating System**：Windows、Macos、Linux
 - **Programming language**：python
 - **Libraries and frameworks**：Pandas、PyQt5、Neo4j......  

## Source Code Structure

### 1 .env

`.env` often used to store environment variables.

Here, we store the API of LLM CLient and the account and password of Neo4j.

### 2. knowledge_graph_generator.ipynb

This is a Python notebook that demonstrates how to extract entity relationship and entity attribute knowledge graphs from multiple files passed in by users, as well as how to import the extracted entity relationship triples and entity attribute triples into Neo4j. **The specific operation process can be viewed in <u>Operating Procedure</u>.**

### 3.KGGenerate.py

In this Python code file, function methods called by **ui.py** are defined, including the entity relationship ontology definition function, the entity attribute ontology definition function, and the function to export triples to a specified directory.

### 4.Dictionary.py

In this Python code, the English-to-Chinese dictionary and the Chinese-to-English dictionary used by the ui.py are stored.

### 5.ui.py

This Python code file is where we developed a **UI tool** to facilitate users in completing the above tasks. **The specific operation process of the UI interface can be viewed in <u>UI Operating Procedure</u>.**

##  Operating Procedure

### 1. Project installation

You can install the **Knowledge Graph Builder** library as follows

``````shell
$ pip install knowledge-graph-builder
``````

### 2.Define Ontology

The ontology is a pydantic model in the library, with a specific structure. By defining entities, important relationships between entities, and attributes owned by entities, the large language model is guided to extract corresponding information, but it cannot guarantee that only the set relationships are extracted. Different models behave differently.

#### （1）Define Entity Relationship Ontology

The following code is only a simple example of entity relationship ontology. For a more detailed definition of the entity relationship ontology, it can be queried in the running code.

```python
# Define Entity Relationship Ontology
def define_ERontology():
    return EROntology(
        entities=[
            {"plant": "Mangrove, reed, Spartina alterniflora, Suaeda salsa"},
            {"Water Body": "Sea water, trenches, ponds"},
            {"Family": "Compositae, Alismaceae, Amaranaceae, Leguminaceae"},
            {"Community": "Meadow, mangrove community, cattail community"},
        ],
        relationships=[
            "Proximity",
			"Growth",
			"Section",
			"Alias",
			"Dominant species",
        ]
)
```

#### （2）Define Entity Attribute Ontology

The following code is only a simple example of entity attribute ontology. For a more detailed definition of the entity attribute ontology, it can be queried in the running code.

```python
# Define Entity Attribute Ontology
def define_EAontology():
    return EAOntology(
        entities=[
            {"plant": "Mangrove, reed, Spartina alterniflora, Suaeda salsa"},
            {"Water Body": "Sea water, trenches, ponds"},
            {"Community": "Meadow, mangrove community, cattail community"},
        ],
        attributes=[
            {"Lifestyle": "Herbs perennial, annual, annual or biennial"},
			{"Height": "45-100 cm"},
			{"Color": "dark blue, green, pink"},
			{"Scientific name": "yrrhiza uralensis Fisch."},
        ]
    )
```

### 3.Select an LLM Client

In this project, we will choose the Groq client. First, you need to apply for your own API on the Groq official website, and then copy the applied API into `.env`

[Groq]: https://groq.com/

```python
# Groq models
model = "llama3-70b-8192"

# Open AI models
oai_model="gpt-3.5-turbo"

# Use Groq
LLM = GroqClient(model=model, temperature=0.1, top_p=0.5)
# OR Use OpenAI
# llm = OpenAIClient(model=oai_model, temperature=0.1, top_p=0.5)
```

You can also define your own LLM client and pass it on to the KGBuilder.

### 4.Split the user text into chunks.

Since the context window of the current large language model is limited. So we need to properly chunk the text and process one block at a time to create the graph. The block size we should use depends on the context window of the model. According to the project practice test, 800 to 1200 labeled blocks are very suitable.

Users can store multiple files that need to create a knowledge graph in **TXT format** in a directory. The model accepts the directory passed in by the user as input and automatically divides the document passed in by the user into text blocks of appropriate size.

#### User Input Sample Directory：.\example-data\example-input

```python
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        input_file = os.path.join(input_dir, filename)
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            user_text = ["\n" + line.strip() + "\n" for line in lines if line.strip()]
```

### 5.Convert these chunks into Documents.

In a project, documents are defined by the following Pydantic model with a specific structure:

```python
class Document(BaseModel):
    text: str
    metadata: dict
```

The metadata added to the document will be associated with each relationship and attribute extracted from the document. This helps us better sort out and understand the situational background information of multiple relationships between nodes in multiple documents.

It can be realized by calling the **create_docs** method of the KnowledgeGraphBuilder class in the **knowledge_graph_builder** project.

```python
from knowledge_graph_builder import KnowledgeGraphBuilder
Ontology_ER = define_ERontology()
KGBuilder = KnowledgeGraphBuilder(ontology=Ontology_ER, llm_client=LLM)
# Convert these chunks into Documents.
docs = KGBuilder.create_docs(user_text)
```

### 6.Run knowledge_graph_generator

The Knowledge Graph Builder directly takes the list of documents and iterates through each document to create a subgraph for each document. The final output is a complete graph of all documents.It can be realized by calling the **documents_to_graph** method of the KnowledgeGraphBuilder class in the **knowledge_graph_builder** project.

Here is the example code for generating the Entity Relationship Knowledge Graph:

```python
from knowledge_graph_builder import KnowledgeGraphBuilder,EROntology,GroqClient,Document
# Create an entity relationship KGBuilder instance
Ontology_ER = define_ERontology()
ERKGBuilder = KnowledgeGraphBuilder(ontology=Ontology_ER, llm_client=LLM)
# Convert these chunks into Documents.
docs = ERKGBuilder.create_docs(user_text)
# Building Entity Relationship Knowledge Graph
ERKnowledgeGraph = ERKGBuilder.documents_to_graph(list(docs), delay=0)
```

The Entity Relationship Knowledge Graph output is the final graph as a list of edges, where each edge is a pydical model.

```python
# Entity Relationship Node
class ERNode(BaseModel):
    entity: str
    name: str
# Entity Relationship Edge
class EREdge(BaseModel):
    node_1: ERNode
    node_2: ERNode
    relationship: str
    metadata: dict = {}
    sequence: Union[int, None] = None
```

Here is the example code for generating the Entity Attribute Knowledge Graph:

```python
from knowledge_graph_builder import KnowledgeGraphBuilder,EAOntology,GroqClient,Document
# Create an entity attribute KGBuilder instance
Ontology_EA = define_EAontology()
EAKGBuilder = KnowledgeGraphBuilder(ontology=Ontology_EA, llm_client=LLM)
# Convert these chunks into Documents.
docs = EAKGBuilder.create_docs(user_text)
# Building Entity Attribute Knowledge Graph
EAKnowledgeGraph = EAKGBuilder.documents_to_graph(list(docs), delay=0)
```

The Entity Attribute Knowledge Graph output is the final graph as a list of edges, where each edge is a pydical model.

```python
# Entity Attribute Node 1
class EANode1(BaseModel):
    entity: str
    name: str
# Entity Attribute Node 2
class EANode2(BaseModel):
    attribute: str
    name: str  
# Entity Attribute Edge
class EAEdge(BaseModel):
    node_1: EANode1
    node_2: EANode2
    relationship: str
    metadata: dict = {}
    sequence: Union[int, None] = None
```

### 7.Extract Knowledge Graph Triples to EXCEL

In order to understand the Knowledge Graph Generator by the model and to facilitate manual inspection of the Knowledge Graph generated by the large language model for errors, we import the Entity Relationship Knowledge Graph and Entity Attribute Knowledge Graph built by Knowledge Graph Generator into two different EXCEL files, **ERTriples.excel** and **EATriples.excel** respectively,The directory where these two EXCEL files are stored is specified by the user.

**ERTriples.excel**：After extracting the Entity Relationship Knowledge Graph from multiple input text of the user, the triplets are extracted into the EXCEL document uniformly.

**EATriples.excel**：After extracting the Entity Attribute  Knowledge Graph from multiple input text of the user, the triplets are extracted into the EXCEL document uniformly.

The following is a function method for extracting entity relationship triples and extracting entity attribute triples to a specified directory:

```python
def export_to_directory(graph, ontology, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define file name
    ER_filename = "ERTriples.xlsx"
    EA_filename = "EATriples.xlsx"
    
    # Build a complete file path
    ER_outputfile = os.path.join(output_dir, ER_filename)
    EA_outputfile = os.path.join(output_dir, EA_filename)
    
    # Extracting Entity Relationship Triples
    ER_extracted_data = [
        [edge.node_1.entity, edge.node_1.name, edge.node_2.entity, edge.node_2.name, edge.relationship]
        for edge in graph
        if isinstance(ontology, EROntology)  
    ]
    # Extracting Entity Attribute Triples
    EA_extracted_data = [
        [edge.node_1.entity, edge.node_1.name, edge.node_2.attribute, edge.node_2.name, edge.relationship]
        for edge in graph
        if isinstance(ontology, EAOntology)  
    ]
    
    # Write Entity Relationship Triples to Excel
    if ER_extracted_data:
        ER_df = pd.DataFrame(ER_extracted_data, columns=['head', 'key1', 'tail', 'key2', 'relationship'])
        ER_df = ER_df[['head', 'key1', 'relationship', 'tail', 'key2']]
        ER_fileexists = os.path.isfile(ER_outputfile)
        if not ER_fileexists:
            ER_df.to_excel(ER_outputfile, index=False)
        else:
            with pd.ExcelWriter(ER_outputfile, mode='a', if_sheet_exists='overlay') as writer:
                existing_df_er = pd.read_excel(ER_outputfile)
                combined_df_er = pd.concat([existing_df_er, ER_df], ignore_index=True)
                combined_df_er.to_excel(writer, index=False)
    
    # Write Entity Attribute Triples to Excel
    if EA_extracted_data:
        EA_df = pd.DataFrame(EA_extracted_data, columns=['head', 'key1', 'tail', 'key2', 'attribute'])
        EA_df = EA_df[['head', 'key1', 'attribute', 'tail', 'key2']]
        EA_fileexists = os.path.isfile(EA_outputfile)
        if not EA_fileexists:
            EA_df.to_excel(EA_outputfile, index=False)
        else:
            with pd.ExcelWriter(EA_outputfile, mode='a', if_sheet_exists='overlay') as writer:
                existing_df_ea = pd.read_excel(EA_outputfile)
                combined_df_ea = pd.concat([existing_df_ea, EA_df], ignore_index=True)
                combined_df_ea.to_excel(writer, index=False)
```

### 8.Import to Neo4j

We can import the exported Knowledge Graph Triplet EXCEL files (ERTriples.excel and EATriples.excel) into Neo4j for visualization.

First, you need a Neo4j **account** and **password**（Replace this with your own account and password）.Then call the **graph_to_neo4j** method of the KGToNeo4j class in the **knowledge _graph_builder** project.

```python
from knowledge_graph_builder import KGToNeo4j
# Set the username and password for the neo4j database
uri = "bolt://localhost:7687"
username = ""
password = ""

# User-specified directory for storing Knowledge Graph Triples
Triples_dir = ""
# Create an instance that writes an entity relationship and an entity attribute triples to Neo4j
KGNeo4j = KGToNeo4j(uri, username, password)

# Determine whether it is an entity relationship triple or an entity attribute triple, and call different methods to write to the Neo4j database
if Triples_dir:  
    for filename in os.listdir(Triples_dir):
        file_path = os.path.join(Triples_dir, filename)
        if os.path.isfile(file_path) and filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
            if 'relationship' in df.columns[2]: 
                KGNeo4j.graph_to_neo4j(Ontology_ER, file_path)
            elif 'attribute' in df.columns[2]:
                KGNeo4j.graph_to_neo4j(Ontology_EA, file_path)
```

## UI Operating Procedure
For the convenience of our readers in using our Knowledge Graph Generator, we have developed a simple and user-friendly **UI tool**. Now, let's take a look at this amazing tool together!  Its all in the python file **ui.py**
### 1.Environment preparation
#### （1）Install essential library
We have developed this **UI** tool based on **PYQT5** and **Tkinter**, so your language environment needs to have these two essential Python libraries.

**You can use pip to install these two libraries**
``````shell
$ pip install PyQt5
$ pip install Tkinter
``````
**You can also use conda to install these two libraries if you run this project in your conda environment**
````shell
conda install PyQt5
conda install Tkinter
````
#### （2）Make sure your code files are all in the same directory.
The ui.py begin at the following contents :
```` python
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
from knowledge_graph_builder import KnowledgeGraphBuilder, EROntology, GroqClient, KGToNeo4j
from KGGenerate import define_ERontology,define_EAontology,export_to_directory
import pandas as pd
import os
````
**So,to make sure your ui.py run in correctly,all python files and pictures should in the same directory**

### 2. ui.py  code Explanation  and Visualization operation example.
Our ui.py code contain four main classes: 
**class MyWindow**、**class SecondWindow**、**classExtractionThread**、**class GenerateThread**
#### （1）**class MyWindow（）**
This is the first window of our ui tool and  the simplified code is as follows ：
````python
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        .............
    def get_style_sheet(self):
        .............
    def show_second_window(self):
        self.second_window = SecondWindow(self)
        self.second_window.show()
````
The main interface is as shown in the following .gif picture.
![First Page](G:\code\knowledge_graph_generator\UI-Image\First Page.gif)

#### （2）**class SecondWindow（）**
This class is the most important part of our ui tools, it is divided into four parts: **Home**, **Extract Triples**, **Generate Knowledge Graph**, **Language Settings** and we also define a lot of methods that need to be used in this class (see the code ui.py for details) and  the simplified code is as follows ：

~~~python
class SecondWindow(QWidget):
    def __init__(self, main_window):
        ............................
    def initUI(self):
        .............
    #Home
        home_page = QWidget()
        home_page.setStyleSheet("background-color: rgba(255, 255, 255, 0);") # Set background transparency
        home_layout = QVBoxLayout(home_page)
        .............
    #Extract Triples
        extraction_page = QWidget()
        extraction_layout = QVBoxLayout()
        ............. 
    #Generate Knowledge Graph
        generation_page = QWidget()
        generation_layout = QVBoxLayout()
        .............
    #Language Settings
        language_page = QWidget()
        language_layout = QVBoxLayout()
        language_label = QLabel(self.get_label_text("Select Your Language"))
        language_label.setStyleSheet("font-family: Times New Roman; font-weight: bold;font-size: 25px;")
        language_layout.addWidget(language_label)
        ```py
    def paintEvent(self, event):
    def changePage(self, index):
    def choose_inputdir(self):
    def choose_save_path(self):
    def start_extraction(self):
    def log_message(self, message):
    def choose_generation_dir(self):
    def go_back_to_main(self):
    def show_next_generation_page(self):
    def return_to_first_page(self):
    def start_generation(self):
    def set_language(self, language):
    def update_ui(self):
    def get_label_text(self, en_text):
    def get_style_sheet(self):
    def text_style_sheet(self):
    def choosebutton_style_sheet(self):
    def back_style_sheet(self):
    def back2_style_sheet(self):
    def language_style_sheet(self):
    def get_html_content(self):
~~~

The four interfaces are shown in the following GIF image:
![Second Window](G:\code\knowledge_graph_generator\UI-Image\Second Window.gif)

#### （3）**classExtractionThread（）**

This interface is mainly designed for users to monitor the progress of their triple extraction in real time.
The simplified code is as follows ：

```python
class ExtractionThread(QThread):
    def __init__(self, inputdir_path, save_path, erontology, eaontology, llm):
    ............................
    def run(self):
    ..............
    def ERKGgenerate(self, inputdir_path):
    ......................................
    def EAKGgenerate(self, inputdir_path):
    ......................................
```

**Please see Section 3 for the display of the GIF related to this part.**

#### （4）class GenerateThread（）
Like the extraction class above, this class is mainly used to show the user the progress of the generation of the knowledge graph (i.e., the process of writing the triples to the Neo4j database).
The simplified code is as follows ：

````python
class GenerateThread(QThread):
    def __init__(self, selected_inputdir_path, uri, username, password, erontology, eaontology):
    ..........................
    def run(self):
    ..............
    def start_generation(self, selected_inputdir_path):
    ..............
````
**Please see Section 3 for the display of the GIF related to this part.**
### 3.UI Tool Usage process
#### （1）To extract triples
a.You only need to **select a directory path** for the file you want to use for extracting triples in the Extract Triples interface, and then **choose a directory** to save the extracted triples.

b.Attention！Whether you choose an **extraction path** or a **save path** here, what I mentioned are **directory paths**, not individual file paths. This is because our Knowledge Graph Generator can extract entity relationship triples and entity attribute triples **from multiple documents simultaneously**, and save them to your chosen save path in the form of an Excel spreadsheet.

c. So you may be wondering, how do I extract the triplets of a single file? It's quite simple – you just need to place the individual file in the directory you've selected!

d.Now,let's use it
just three steps:choose InputDir、choose  Save Path、Click Start！

**We will take the ten txt documents in our code compression package located at /data/example as an example for extraction, and place the extracted results in the /data/output directory.**
![Extract Triples](G:\code\knowledge_graph_generator\UI-Image\Extract Triples.gif)
Please **note** that he can **only handle txt documents**, and **if there are many documents, his extraction speed may be slower**; and he extracts triplets by calling large models, so **make sure your computer can call large models**.

#### （2）To Generate Knowledge Graph
a.You need to **select the path** of the triple document you will use to generate the knowledge graph. 

b.Then **enter your neo4j database username and password** (make sure your neo4j database is open and the account and password are correct)

c.**Click the Start Generate button** and just wait
![Generate Knowledge Graph](G:\code\knowledge_graph_generator\UI-Image\Generate Knowledge Graph.gif)

#### （3）Switch language
For a better user experience with our UI tool, our UI **supports Chinese-English bilingual switching**. Be sure to place the Dictionary.py file in the same directory, as our language switching relies on this pre-defined dictionary.
![Language Settings](G:\code\knowledge_graph_generator\UI-Image\Language Settings.gif)

## Awaiting improvement
Our Knowledge Graph Generator currently can only extract txt documents, and the documents written to the neo4j database can only be in Excel format. **Our future work will focus on researching how to handle a Knowledge Graph Generator that can process multiple formats**.