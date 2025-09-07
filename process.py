import pandas as pd
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Load your JSON data
print(("Loading JSON data..."))
with open("final_hospital_data.json", "r", encoding='utf-8') as f:
    data = json.load(f)
    
# Create a list to store all searchable items
all_items = []

# Process hospital info
if 'hospital_info' in data:
    hosp = data['hospital_info']
    content = f"Hospital: {hosp.get('name','')} | Phone: {hosp.get('main_phone', '')} | Address: {hosp.get('address', '')} | Website: {hosp.get('website', '')}"
    all_items.append({
        "id": f"hosp_{len(all_items)}",
        "type": "hospital_info",
        "name": hosp.get('name', ''),
        "content": content,
        "original_data": json.dumps(hosp),
        "category" : 'general'
    })
    
# Process departments
if 'departments' in data:
    for dept_name, dept_data in data["departments"].items():
        # Create searchable content for departments
        dept_content = f"""
        DEPARTMENT: {dept_data.get('name', '')}
        DESCRIPTION: {dept_data.get('description', '')[:300]}
        SERVICES: {', '.join(dept_data.get('services', [])[:12])}
        FACILITIES: {', '.join(dept_data.get('facilities', [])[:3])}
        PROCEDURES: {', '.join(dept_data.get('procedures', [])[:15])}
        DOCTORS: {', '.join([doc['name'] for doc in dept_data.get('doctors', [])[:10]])}
        URL: {dept_data['url']}
        """

        all_items.append({
            'id': f"dept_{len(all_items)}",
            'type': 'department',
            'name': dept_data.get('name', ''),
            'content': ' '.join(dept_content.split()),
            'original_data': json.dumps(dept_data),
            'category': dept_data.get('name', '')
        })
        
        # Process doctors within this department
        for doctor in dept_data.get('doctors', []):
            doc_content = f"""
            DOCTOR: {doctor.get('name', '')}
            SPECIALIZATION: {doctor.get('specialization', '')}
            QUALIFICATIONS: {', '.join(doctor.get('qualifications', []))}
            EXPERTISE: {', '.join(doctor.get('areas_of_expertise', []))}
            APPOINTMENT: {doctor.get('appointment_number', '')}
            DEPARTMENT: {dept_data.get('name', '')}
            URL: {dept_data['url']}
            """
            
            all_items.append({
                'id': f"doc_{len(all_items)}",
                'type': 'doctor',
                'name': doctor.get('name', ''),
                'content': ' '.join(doc_content.split()),
                'original_data': json.dumps(doctor),
                'category': dept_data.get('name', '')
            })
            
# Process all doctors (from the separate all_doctors section)
if 'all_doctors' in data:
    for doc_name, doctor in data['all_doctors'].items():
        # Check if this doctor was already added from departments
        existing_doc = any(item for item in all_items if item['type'] == 'doctor' and item['name'] == doc_name)
        if not existing_doc:
            doc_content = f"""
            DOCTOR: {doctor.get('name', '')}
            SPECIALIZATION: {doctor.get('specialization', '')}
            QUALIFICATIONS: {', '.join(doctor.get('qualifications', []))}
            EXPERTISE: {', '.join(doctor.get('areas_of_expertise', []))}
            APPOINTMENT: {doctor.get('appointment_number', '')}
            DESCRIPTION: {doctor.get('description', '')[:200] if doctor.get('description') else ''}
            URL: {dept_data['url']}
            """
            
            all_items.append({
                'id': f"doc_{len(all_items)}",
                'type': 'doctor',
                'name': doctor.get('name', ''),
                'content': ' '.join(doc_content.split()),
                'original_data': json.dumps(doctor),
                'category': doctor.get('specialization', '')
            })
            

# Create DataFrame
df = pd.DataFrame(all_items)
print(f"Created {len(df)} search items")

# Save to CSV
df.to_csv('hospital_search_data.csv', index=False, encoding='utf-8')
print("CSV file saved: hospital_search_data.csv")

# Create embeddings
print("Creating embeddings...")
embedder = SentenceTransformer('all-mpnet-base-v2')
contents = df['content'].tolist()
embeddings = embedder.encode(contents, convert_to_numpy=True)

# Add embeddings to DataFrame
df['embedding'] = list(embeddings)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings.astype('float32'))

# Save FAISS index
faiss.write_index(index, 'hospital_faiss_index.bin')
print("FAISS index saved: hospital_faiss_index.bin")

# Save DataFrame with embeddings
df.to_pickle('hospital_data_with_embeddings.pkl')
df.to_csv('hospital_embedding_data.csv', index=False, encoding='utf-8') # also storing to csv

print("Data with embeddings saved: hospital_data_with_embeddings.pkl")

print("✅ All done! Data processing completed.")