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

load_dotenv()

# Load data and index
print("Loading data...")
df = pd.read_pickle('hospital_data_with_embeddings.pkl')
index = faiss.read_index('hospital_faiss_index.bin')
embedder = SentenceTransformer('all-mpnet-base-v2')

parser = StrOutputParser()

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
    
    # Create prompt for GPT
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a warm, caring, and conversational assistant for Hameed Latif Hospital. Always answer as if you are directly helping a patient. Be professional but approachable, and avoid robotic or repetitive phrases like 'Certainly' or 'Based on the context'. Always sound human and supportive."),
        ("human", """
        CONTEXT:
        {context}

        PATIENT QUESTION:
        {question}

        Instructions:
        - Speak warmly and clearly, as if guiding a patient at the hospital front desk. 
        - Do NOT use stiff phrases like "Based on the information available" or "Certainly".
        - If the question is about a **procedure**:
            * Explain it in simple, patient-friendly language using the context.
            * Explain the procedures
            * Mention the relevant department(s).
            * List at least 3-5 doctors (if available), including their name, specialization, qualifications, and expertise.
        - If the question is about a **doctor**:
            * Provide name, specialization, qualifications, areas of expertise, and appointment number (if in context).
            * Mention at least 3 doctors if more are available in the context.
        - If the question is about a **department**:
            * Organize the answer with headings: Description, Services, Facilities, Procedures, Doctors.
        - If the question is about the **hospital in general**, include:
            * Name: Hameed Latif Hospital
            * Location: Lahore, Pakistan
            * Main Phone: +92 (42) 111-000-043
            * Website: https://www.hameedlatifhospital.com
            * Address: 14- Abu Baker Block, New Garden Town, Lahore
        - If any requested detail is missing, politely mention this and suggest contacting the hospital directly.
        - Do not provide medical prescriptions or diagnosis. Always suggest contacting a doctor for medical advice.
        - If the question is broad or unclear (e.g., "surgery"), list the types of surgeries or departments in the context, then invite the patient to clarify.

        Always:
        - Be concise, warm, and reassuring.
        - Speak naturally, like a hospital representative who truly cares for the patient.
        """)
    ])
            
    # Get response from GPT
    try:
        llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2,
        max_output_tokens=500,
    )
        chain = prompt | llm | parser
        
        response = chain.invoke({
            "context" : context,
            "question" : question
        })
        return response
    except:
        # Fallback: just return search results if GPT fails
        return f"I found these relevant results:\n\n{context}"

# Simple chat interface
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