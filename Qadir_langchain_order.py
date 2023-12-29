from config1 import openai_keys
import os
import sys
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain,SequentialChain
from langchain.document_loaders import TextLoader
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import streamlit as st
import threading
import time

    
os.environ['OPENAI_API_KEY']=openai_keys.API_KEY
model=ChatOpenAI(openai_api_key=openai_keys.API_KEY,temperature=0.5,model='gpt-4', max_tokens=10, streaming= True)# add further parameters as per user preference

book=[] #creation of main book
memory = ConversationBufferMemory(return_message=True)
conversation = ConversationChain(

    llm=model,
    memory = memory,
)

class Bot:
    def __init__(self,**kwargs) -> None:
        self.name=kwargs['name']
        self.characteristics=kwargs['characteristics']
        self.interests=kwargs['interests']
        self.knowledge=kwargs['knowledge']
        
        


    def generate_prompt(self,other_model_input:str)->None:

        messages=ChatPromptTemplate.from_messages([
            SystemMessage(content="""
                IMPORTANT :: Strictly Give Answer only as a narrative sentence that can be written in a book
                Imagine you are an a person with Interests in {interest}. 
                Your primary focus is on {interest}, and answer with exact matching specific characteristics as given:
                {characteristics}.
                You are writing a captivating book.
                The goal is to seamlessly integrate deep knowledge into the content of the book. 
                Incorporate essential background information and key concepts related to {knowledge}. 
                Aim strictly for 10-20 words ONLY with a balance of depth and readability. 
                Thank you for crafting content that combines expertise with engagement."""),
            HumanMessagePromptTemplate.from_template("""
                                                        Give one line that comes next in timeline and story line sequence to and create further story: 
                                                        {other_model_input}"""
                                                    if len(other_model_input)!=0 else """
                                                        Start a conversation for a book""")
            ])
        
        response=conversation.predict(input=messages.format_messages(interest=self.interests,characteristics=self.characteristics,knowledge=self.knowledge,other_model_input=other_model_input))
        
        return response
    

def init_conversation2(bot1:Bot,bot2:Bot,res):
    res=(f"{bot2.generate_prompt(res).split('.')[0]}.")
    book.append(f"Persona {bot2.name} : {res}")
    st.text_area('PERSONA1',value=f"Persona {bot2.name} : {res}")
    init_conversation1(bot1,bot2,res)
    return 0

def init_conversation1(bot1:Bot,bot2:Bot,res):
    res= (f"{bot1.generate_prompt(res).split('.')[0]}.")
    book.append(f"Persona {bot1.name} : {res}")
    st.text_area("persona2",value=f"Persona {bot1.name} : {res}")

    print('\n'.join(book[-2:]))
    init_conversation2(bot1,bot2,res)
    return 0


def createpersona(**kwargs)->str:
    bot1= Bot(**kwargs)
    return bot1


    
    # persona1=createpersona(name='A',
    #                        characteristics='it is usually angry',
    #                        interests='it likes to watch action movies',
    #                        knowledge='')
    
    # persona2=createpersona(name='B',
    #                        characteristics='it is usually happy',
    #                        interests='it likes to watch underage kids cartoons',
    #                        knowledge='')
    
    # res=''
    # res=persona2.generate_prompt(res).split('.')[0]
    # print(res)
    

    
    
def main():
    
    
    st.title("Persona Input App")
    st.sidebar.header("Persona 1")
    
    persona1_name = st.sidebar.text_input("Name:", value="A")
    persona1_characteristics = st.sidebar.text_input("Characteristics:", "It is usually angry")
    persona1_interests = st.sidebar.text_input("Interests:", "It likes to watch action movies")
    persona1_knowledge = st.sidebar.text_input("Knowlege_base:","")

    st.sidebar.header("Persona 2")
    persona2_name = st.sidebar.text_input("Name2:", value="B")
    persona2_characteristics = st.sidebar.text_input("Characteristics2:", "It is usually happy")
    persona2_interests = st.sidebar.text_input("Interests2:", "It likes to watch underage kids cartoons")
    persona2_knowledge = st.sidebar.text_input("Knowlege_base:","" , key='knowledg1')
    
    persona1=createpersona(name=persona1_name,
                        characteristics=persona1_characteristics,
                        interests=persona1_interests,
                        knowledge=persona1_knowledge)
    
    
    persona2=createpersona(name=persona2_name,
                        characteristics=persona2_characteristics,
                        interests=persona2_interests,
                        knowledge=persona2_knowledge)
    
    
    




    input_text = st.text_input("You:", placeholder="Ask me anything...", key="input")

    if st.button("Submit", type="primary"):
        # Generate response and append to the conversation history
        response = init_conversation1(persona1, persona2, input_text)




        
if __name__=="__main__":
    main()