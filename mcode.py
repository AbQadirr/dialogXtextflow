from config import All_keys
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.memory import ConversationBufferWindowMemory
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
import pinecone
import streamlit as st
import tempfile
import os
          
          
def main_page():
    print("Executing run_chat_app")
              
     
                            
    model=ChatOpenAI(openai_api_key=All_keys.Openai_API_KEY,temperature=0.2,model='gpt-4',max_tokens=2000)# add further parameters as per user preference
    embeddings = OpenAIEmbeddings(openai_api_key=All_keys.Openai_API_KEY)
    PINECONE_API_KEY = All_keys.PINECONE_API_KEY
    PINECONE_API_ENV = All_keys.PINECONE_API_ENV

    book=[] #creation of main book
    all_personas=[] #all personas stored here

    chatmemory = ConversationBufferWindowMemory(k=3)


        

    class Bot:
        def __init__(self,**kwargs) -> None:
            self.name=kwargs['name']
            self.characteristics=kwargs['characteristics']
            self.interests=kwargs['interests']
            self.knowledge_file=kwargs['knowledge_file']

        def knowledge(self,kpath):
            loader=TextLoader(file_path=kpath)
            data=loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
            texts = text_splitter.split_documents(data)
            # initialize pinecone
            pinecone.init(
                api_key=PINECONE_API_KEY,  # find at app.pinecone.io
                environment=PINECONE_API_ENV  # next to api key in console
            )
            index = "bookbots" # put in the name of pinecone index
            docsearch = Pinecone.from_documents(texts, embeddings, index_name=index)
            return docsearch
        
        def generate_prompt(self,other_model_input:str)->None:
        
            if len(other_model_input)==0:
                other_model_input='Start a story for a book'

            query=f"""
                %INSTRUCTIONS:
                    Suppose that event has occured as follows:
                    "{other_model_input}"      
                    After that tell us what is likely to occur next from the information given.         
                    Write this one sentence such that its tone matches a persona with Interests in:
                        {self.interests}. 
                    Write this one sentence such that its tone matches a persona characteristics as given:
                        {self.characteristics}.
                    Write this one sentence such that a book is being written.
                %RESTRICTIONS:
                    IMPORTANT :: Aim strictly for one easy short sentence with subject object and verb."""
            
            qa_chain = RetrievalQA.from_chain_type(
            model,
            retriever=self.knowledge(self.knowledge_file).as_retriever(search_type="similarity", search_kwargs={"k": 4}),
            chain_type="stuff",memory=chatmemory)
            response=qa_chain.run({"query":query})
            return response

    def init_conversation2(bot1:Bot,bot2:Bot,res):
        res=(f"{bot2.generate_prompt(res).split('.')[0]}.")
        book.append(f"Persona {bot2.name} : {res}")
        st.text_area('PERSONA1',value=f"Persona {bot2.name} : {res}")
        print('\n'.join(book[-1:]))
        init_conversation1(bot1,bot2,res)
        return 0

    def init_conversation1(bot1:Bot,bot2:Bot,res):
        res= (f"{bot1.generate_prompt(res).split('.')[0]}.")
        print(f"asdasd ::: {res}")
        book.append(f"Persona {bot1.name} : {res}")
        st.text_area("PERSONA2",value=f"Persona {bot1.name} : {res}")
        print('\n'.join(book[-1:]))
        init_conversation2(bot1,bot2,res)
        return 0

    def init_conv(botnum:int,persona1:Bot,persona2:Bot,topic:str):
        init_conversation1(persona1,persona2,topic) if botnum==1 else init_conversation2(persona1,persona2,topic)


    def edit_book(line_num:int,newcontent:str):
        book=book[:line_num-1]+newcontent+book[line_num+1:]
        return f'Book edited at line {line_num}'

    def createpersona(**kwargs)->str:
        newbot=Bot(**kwargs)
        all_personas.append(newbot)
        return all_personas[-1]

    def choose_persona():
        return all_personas


    # def main():

    st.title("Dialogue-Interaction")
    
    # Persona 1 input
    st.sidebar.title('Dashboard')
    st.sidebar.header("Persona 1")
    persona1_name = st.sidebar.text_input("Name:", value="A", key='p1_name')
    persona1_characteristics = st.sidebar.text_input("Characteristics:", "e.g. It is usually angry")
    persona1_interests = st.sidebar.text_input("Interests:", "e.g. It likes to fight a lot")
    
    uploaded_file_p1 = st.sidebar.file_uploader("Knowledge-Base", type=["txt"], key='text1')
    if uploaded_file_p1 is not None:
        try:
            data_p1 = uploaded_file_p1.read().decode('utf-8')
            with open('file1.txt', 'w') as f:
                f.write(data_p1)
        except FileNotFoundError:
            st.error("File not found. Please upload a valid text file for Persona 1.")

    # Persona 2 input
    st.sidebar.header("Persona 2")
    persona2_name = st.sidebar.text_input("Name2:", value="B", key='p2_name')
    persona2_characteristics = st.sidebar.text_input("Characteristics2:", "e.g. It is usually happy")
    persona2_interests = st.sidebar.text_input("Interests2:", "e.g. It likes to make friends")
    
    uploaded_file_p2 = st.sidebar.file_uploader("Knowledge-Base", type=["txt"], key='text2')
    if uploaded_file_p2 is not None:
        try:
            data_p2 = uploaded_file_p2.read().decode('utf-8')
            with open('file2.txt', 'w') as f:
                f.write(data_p2)
        except FileNotFoundError:
            st.error("File not found. Please upload a valid text file for Persona 2.")

    # Create personas
    persona1 = createpersona(
        name=persona1_name,
        characteristics=persona1_characteristics,
        interests=persona1_interests,
        knowledge_file='file1.txt'
    )
    
    persona2 = createpersona(
        name=persona2_name,
        characteristics=persona2_characteristics,
        interests=persona2_interests,
        knowledge_file='file2.txt'
    )

    # User input
    input_text = st.text_input("", placeholder="Write story starting e.g., a person goes out for fishing.", key="input")

    if st.button("Start", type="primary"):
        # Generate response and append to the conversation history
        response = init_conv(1, persona1, persona2, input_text)
        st.text("Response: " + response)





if __name__=="__main__":
    main_page()
# persona1=createpersona(name='A',characteristics='it is usually angry',interests='it likes to watch action movies',knowledge_file='knowledge1.txt')
    # persona2=createpersona(name='B',characteristics='it is usually happy',interests='it likes to watch underage kids cartoons',knowledge_file='knowledge2.txt')
    
    # # print(persona1.knowledge(kpath="knowledge1.txt",query='person'))
    
    # topic='Ben goes outside with his girlfriend'
    # # while(True):
    # #     init_conversation1(persona1,persona2,'Ben goes outside with his girlfriend')
    
    # init_conv(1,persona1,persona2,topic)
    
    
    
