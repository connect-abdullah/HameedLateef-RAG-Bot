from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import faiss
import json
import os
from pathlib import Path
from langchain_core.runnables import RunnableConfig
from langchain.memory import ConversationSummaryMemory

load_dotenv()

# Get the project root directory (parent of backend folder)
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Load data and index with absolute paths
print("Loading data...")
print(f"Project root: {PROJECT_ROOT}")
df_path = PROJECT_ROOT / 'data' / 'hospital_data_with_embeddings.pkl'
index_path = PROJECT_ROOT / 'data' / 'hospital_faiss_index.bin'

print(f"Loading dataframe from: {df_path}")
print(f"Loading FAISS index from: {index_path}")

df = pd.read_pickle(df_path)
index = faiss.read_index(str(index_path))
embedder = SentenceTransformer('all-mpnet-base-v2')

parser = StrOutputParser()

summary_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2,
        max_output_tokens=200,  # Shorter for summaries
    )

# Initialize ConversationSummaryMemory
memory = ConversationSummaryMemory(
    llm=summary_llm,
    memory_key="chat_history",
    return_messages=True
)

def search_hospital_data(query, top_k=5):
    """Search for relevant hospital information"""
    query_embedding = embedder.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding.astype('float32'), top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        row = df.iloc[idx]
        similarity = 1 / (1 + distances[0][i])  # Convert to similarity score
        
        results.append({
            'type': row['type'],
            'name': row['name'],
            'content': row['content'],
            'similarity': round(similarity, 3),
            # 'original_data': json.loads(row['original_data']),
            'category': row['category']
        })
    
    return results

# Initializing LLM
llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2,
        max_output_tokens=500,
        )

# Create prompt for LLM
prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly and helpful assistant for Hameed Latif Hospital. Be conversational and natural, like someone who genuinely cares about helping patients. Avoid being too formal or robotic, but also maintain a warm, professional tone."),
        ("human", """
        CONVERSATION CONTEXT:
        {chat_history}

        CURRENT CONTEXT:
        {context}

        PATIENT QUESTION:
        {question}

        **CORE GUIDELINES:**
        - Use the conversation summary to remember patient details and reference them naturally
        - Speak like you're having a friendly conversation with someone who needs help
        - Be concise, warm, and reassuring - like a hospital representative who genuinely cares
        - Vary your responses naturally, don't use repetitive phrases

        **AVOID ROBOTIC PHRASES:**
        - ❌ "Hello!", "Certainly", "Based on the information"
        - ❌ "I'm happy to help", "How can I assist you today?"
        - ❌ Stiff formal language or repetitive greetings
        - ❌ Starting every response with greetings

        **RESPONSE STRATEGIES:**
        - **Procedures**: Explain simply in patient-friendly language, mention relevant departments
        - **Doctors**: Provide name, specialization, qualifications, expertise, appointment info if available
        - **Departments/Specialties**: Brief listings with short descriptions (2-3 lines max)
        - **Hospital Info**: Include name (Hameed Latif Hospital), location (Lahore, Pakistan), phone (+92 42 111-000-043), website, address when relevant
        - **Missing Info**: Politely suggest contacting the hospital directly without formality
        - **Medical Advice**: Never diagnose or prescribe - always suggest seeing a doctor

        **NATURAL TONE EXAMPLES:**
        - Instead of "Hello! I'm happy to help" → "Sure, let me find that for you"
        - Instead of "How can I assist you today?" → "What else would you like to know?"
        - Instead of "Certainly!" → "Of course" or just start with the answer
        - "You're asking about Dr. Khan? He's a cardiologist with MBBS, FCPS qualifications."
        - "For heart-related concerns, our cardiology department would be the right place."
        - "I don't have that specific information, but the main desk can help you at +92 (42) 111-000-043."

        **SPECIFIC INSTRUCTIONS:**
        1. Use conversation history to maintain context and remember patient details
        2. For procedures: Explain simply, mention relevant departments, only list doctors if clearly in context
        3. For doctors: Provide available details (name, specialization, qualifications, expertise, appointment)
        4. For departments: Brief overviews only, don't mention doctors unless clearly listed
        5. For general info: Include hospital name, location, phone, website, address as needed
        6. For missing information: Suggest contacting hospital directly in a friendly way
        7. For medical advice: Always defer to doctors - never diagnose or prescribe
        8. For broad questions: List available options and invite clarification

        **ALWAYS:**
        - Sound like a real person who works at the hospital and wants to help
        - Be approachable and professional without being stiff
        - Reference previous conversation when appropriate
        - Keep responses concise and helpful"""
        )
    ])


def ask_question(question):
    """Get answer using semantic search + GPT"""
    # Search for relevant information
    results = search_hospital_data(question, top_k=5)
    
    # Build context with full structured data
    context = "RELEVANT HOSPITAL INFORMATION:\n\n"
    for i, result in enumerate(results, 1):
        context += f"{i}. [{result['type'].upper()}] | {result['name']} | (Score: {result['similarity']})\n Content: {result['content']} \n"
        
    # Extract full structured data
        # original_data = result['original_data']
        
        # if result['type'] == 'department':
        #     # For departments, include description, services, procedures, facilities, and doctors
        #     if original_data.get('description'):
        #         context += f"   Description: {original_data['description'][:200]}...\n"
            
        #     if original_data.get('services'):
        #         context += f"   Services: {', '.join(original_data['services'][:5])}\n"
            
        #     if original_data.get('procedures'):
        #         context += f"   Procedures: {', '.join(original_data['procedures'][:5])}\n"
            
        #     if original_data.get('facilities'):
        #         context += f"   Facilities: {', '.join(original_data['facilities'])}\n"
            
        #     if original_data.get('doctors'):
        #         doctor_names = [doc.get('name', '') for doc in original_data['doctors'][:5]]
        #         context += f"   Doctors: {', '.join(doctor_names)}\n"
                
        # elif result['type'] == 'doctor':
        #     # For doctors, include specialization, qualifications, expertise, appointment
        #     if original_data.get('specialization'):
        #         context += f"   Specialization: {original_data['specialization']}\n"
            
        #     if original_data.get('qualifications'):
        #         context += f"   Qualifications: {', '.join(original_data['qualifications'])}\n"
            
        #     if original_data.get('areas_of_expertise'):
        #         context += f"   Expertise: {', '.join(original_data['areas_of_expertise'])}\n"
            
        #     if original_data.get('appointment_number'):
        #         context += f"   Appointment: {original_data['appointment_number']}\n"
            
        #     if original_data.get('description'):
        #         context += f"   Description: {original_data['description'][:150]}...\n"
        
    # context += "\n"
    
    
    # Get response from LLM
    try:
        history_data = memory.load_memory_variables({"input": question})
        chat_history = history_data.get("chat_history", "")
        chain = prompt | llm | parser
        
        
        config = RunnableConfig(configurable={"session_id": "thread-1"})   
             
        response = chain.invoke({
            "context" : context,
            "question" : question,
            "chat_history" : chat_history
        })
        
        memory.save_context({"input": question}, {"output": response})
        return response
    except Exception as e:
        # Fallback: just return search results if LLM fails
        print(f"LLM error: {e}")
        return f"I found these relevant results:\n\n{context}"

if __name__ == "__main__":
    # Simple chat interface (only runs when executing this file directly)
    print("🤖 Hameed Latif Hospital Assistant")
    print("   Type 'quit' to exit\n")

    while True:
        try:
            question = input("You: ").strip()
            if question.lower() in ['quit', 'exit', 'bye']:
                print("🤖 Thank you for visiting! Get well soon!")
                break
            
            if not question:
                continue
            
            print("🤖 Searching...")
            answer = ask_question(question)
            print(f"🤖 {answer}\n")
        
        except KeyboardInterrupt:
            print("\n🤖 Goodbye!")
            break
        except Exception as e:
            print(f"🤖 Sorry, I encountered an error: {e}")