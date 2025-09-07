#!/usr/bin/env python3
"""
Final Corrected Hospital Data Formatter V3
FIXES: Ensures ALL doctors from all_doctors are assigned to appropriate departments
"""

import json
import re
from datetime import datetime
from collections import defaultdict

class FinalCorrectedHospitalFormatterV3:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.doctors = {}
        self.raw_departments = {}
        
        # ID counters and lookups
        self._next_doctor_id = 1
        self._next_department_id = 1
        self.department_name_to_id = {}
        
        # Exact department list provided by user
        self.target_departments = [
            'Anesthesia and Pain Management',
            'Cardiac and Vascular Surgery', 
            'Cardiac Surgery',
            'Clinical Psychology',
            'Dental',
            'Dietetics & Nutrition',
            'Emergency Services',
            'Endocrinology',
            'ENT',
            'Fetal Medicine',
            'Gastroenterology',
            'General Surgery',
            'General Thoracic Surgery',
            'Gynecology and Obstetrics',
            'Infectious Diseases',
            'Intensive Care Unit',
            'Internal Medicine',
            'Interventional Cardiac Electrophysiologist',
            'Interventional Cardiology',
            'Interventional Radiology',
            'Laboratories',
            'Lactation Management',
            'Nephrology & Dialysis',
            'Neurology & Stroke Management',
            'Neurosurgery & Spine',
            'Oncology',
            'OPD',
            'Ophthalmology',
            'Orthopedics',
            'Pediatrics',
            'Physiotherapy & Hydrotherapy',
            'Plastic Surgery',
            'Psychiatry',
            'Pulmonology',
            'Radiology',
            'Rheumatology',
            'Speech Therapy',
            'Urology and Lithotripsy'
        ]
        
        # Pediatric doctors as provided by user
        self.pediatric_doctors = [
            {
                'name': 'Dr. Shoaib Butt',
                'specialization': 'Pediatrician',
                'qualifications': ['MBBS', 'DCH (Diploma in Child Health)'],
                'subspecialty': 'General Pediatrics'
            },
            {
                'name': 'Dr. Sajjad Rafique', 
                'specialization': 'Pediatrician',
                'qualifications': ['MBBS', 'MRCP', 'MRCPCH'],
                'subspecialty': 'General Pediatrics'
            },
            {
                'name': 'Dr. Haroon Hamid',
                'specialization': 'Pediatrician',
                'qualifications': ['MBBS', 'FCPS', 'MRCP (IRELAND)', 'FRCP NEONATAL FELLOWSHIP (RCPCH UK)'],
                'subspecialty': 'Neonatology'
            },
            {
                'name': 'Dr. Ubaid Ullah',
                'specialization': 'Pediatrician', 
                'qualifications': ['MBBS', 'FCPS (PAEDIATRICS)'],
                'subspecialty': 'General Pediatrics'
            },
            {
                'name': 'Dr. Khalid Javaid',
                'specialization': 'Pediatrician',
                'qualifications': ['MBBS', 'DCH'],
                'subspecialty': 'General Pediatrics'
            },
            {
                'name': 'Dr. Saed Aftab',
                'specialization': 'Pediatrician',
                'qualifications': ['MBBS', 'MD', 'MRCP (PAEDS)', 'DABIM', 'FAAP', 'FACPS'],
                'subspecialty': 'General Pediatrics'
            },
            {
                'name': 'Dr. Jaida Manzoor',
                'specialization': 'Pediatrician',
                'qualifications': ['MBBS', 'FCPS'],
                'subspecialty': 'General Pediatrics'
            },
            {
                'name': 'Dr. Sommayya Aftab',
                'specialization': 'Pediatric Endocrinologist',
                'qualifications': ['MBBS (KE)', 'FCPS (PAEDS)', 'MRCPCH (UK)', 'PGPN (BOSTON)'],
                'subspecialty': 'Pediatric Endocrinology'
            },
            {
                'name': 'Dr. Nabeela Tallat',
                'specialization': 'Pediatrician',
                'qualifications': ['MBBS', 'FCPS'],
                'subspecialty': 'General Pediatrics'
            },
            {
                'name': 'Dr. Mahmood Shaukat',
                'specialization': 'Pediatric Surgeon',
                'qualifications': ['MBBS', 'FRCS'],
                'subspecialty': 'Pediatric Surgery'
            },
            {
                'name': 'Dr. Muhammad Saleem',
                'specialization': 'Pediatric Surgeon',
                'qualifications': ['MBBS', 'FRSC (GLASGOW)', 'FRCS TRAUMA'],
                'subspecialty': 'Pediatric Surgery'
            },
            {
                'name': 'Dr. Faiz Rasool',
                'specialization': 'Pediatric Cardiac Surgeon',
                'qualifications': ['MBBS', 'FCPS (CARDIAC SURGERY)'],
                'subspecialty': 'Pediatric Cardiac Surgery'
            },
            {
                'name': 'Dr. Mehwish Faizan',
                'specialization': 'Pediatric Hematologist/Oncologist',
                'qualifications': ['MBBS', 'MCPS', 'FCPS'],
                'subspecialty': 'Pediatric Hematology/Oncology'
            },
            {
                'name': 'Dr. Syed Najam Hyder',
                'specialization': 'Pediatric Cardiologist',
                'qualifications': ['MBBS', 'MCPS', 'FCPS'],
                'subspecialty': 'Pediatric Cardiology'
            }
        ]

    def load_scraped_data(self):
        """Load scraped data with error handling"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.endswith('%'):
                    content = content[:-1]
                if content.endswith(','):
                    content = content[:-1]
                if not content.endswith(']'):
                    content += ']'
                return json.loads(content)
        except Exception as e:
            print(f"Error loading data: {e}")
            return []

    def clean_doctor_name(self, name):
        """Clean and normalize doctor names"""
        if not name:
            return None
            
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'^Dr\.\s+Prof\s+Dr\s+', 'Prof. Dr. ', name)
        name = re.sub(r'^Dr\.\s+Professor\s+Dr\s+', 'Prof. Dr. ', name)
        name = re.sub(r'^Dr\.\s+Brig\s+Dr\s+', 'Brig. Dr. ', name)
        name = re.sub(r'^Professor\s+Dr\.', 'Prof. Dr.', name)
        name = re.sub(r'^Brigadier\s+Dr\.', 'Brig. Dr.', name)
        
        if not re.match(r'^(Dr\.|Prof\.|Brig\.)', name):
            name = 'Dr. ' + name
            
        return name

    def extract_doctors_from_malformed_text(self, malformed_doctor_text):
        """Extract clean doctor information from malformed text"""
        if not malformed_doctor_text or not isinstance(malformed_doctor_text, str):
            return None
        
        text = re.sub(r'\s+', ' ', malformed_doctor_text).strip()
        
        patterns = [
            r'^((?:Prof\.\s+)?(?:Col\.\(R\)\.\s+)?(?:Brig\.\s+)?Dr\.\s+[A-Za-z\s\-\.()]+?)\s+(Peadiatrician|Pediatrician|Cardiologist|Urologist|Gynecologist|Orthopedic|Neurologist|Anesthesiologist|Radiologist|General\s+Surgeon|ENT|Physiotherapist|Plastic\s+Surgeon|Gastroenterologist|Nephrologist|Endocrinologist|Dermatologist|Oncologist|Psychiatrist|Dental\s+Surgeon|Lactation\s+Specialist|Ophthalmologist|Opthalmologist|Speech\s+and\s+Language\s+Therapist|Infectious\s+Disease\s+Specialist|Rheumatologist|Pulmonologist|Interventional\s+Radiologist|Cardiac\s+Surgeon|Neurosurgeon|Peads\s+Surgeon|Paeds\s+Cardiologist|Peads\s+Cardiologist|Peads\s+Hemotologist|Endocrinologist/\s+Diabaties|Fetal\s+Medicine)\s+Dr(?:\s|$)',
            r'^((?:Prof\.\s+)?(?:Col\.\(R\)\.\s+)?(?:Brig\.\s+)?Dr\.\s+[A-Za-z\s\-\.()]+?)\s+(Peadiatrician|Pediatrician|Cardiologist|Urologist|Gynecologist|Orthopedic|Neurologist|Anesthesiologist|Radiologist|General\s+Surgeon|ENT|Physiotherapist|Plastic\s+Surgeon|Gastroenterologist|Nephrologist|Endocrinologist|Dermatologist|Oncologist|Psychiatrist|Dental\s+Surgeon|Lactation\s+Specialist|Ophthalmologist|Opthalmologist|Speech\s+and\s+Language\s+Therapist|Infectious\s+Disease\s+Specialist|Rheumatologist|Pulmonologist|Interventional\s+Radiologist|Cardiac\s+Surgeon|Neurosurgeon|Peads\s+Surgeon|Paeds\s+Cardiologist|Peads\s+Cardiologist|Peads\s+Hemotologist|Endocrinologist/\s+Diabaties|Fetal\s+Medicine)(?:\s|$)',
            r'^((?:Prof\.\s+)?(?:Col\.\(R\)\.\s+)?(?:Brig\.\s+)?Dr\.\s+[A-Za-z\s\-\.()]+?)(?:\s+[A-Z]|\s*$)',
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    name = match.group(1).strip()
                    specialty = match.group(2).strip()
                elif len(match.groups()) >= 1:
                    name = match.group(1).strip()
                    specialty = None
                else:
                    continue
                
                clean_name = self.clean_doctor_name(name)
                if clean_name and len(clean_name) > 8:
                    return {
                        'name': clean_name,
                        'specialization': specialty,
                        'extracted_from': 'malformed_text_parsing'
                    }
        
        return None

    def extract_doctors_from_comprehensive_text(self, text):
        """Extract all doctor mentions from comprehensive text content"""
        if not text:
            return []
        
        doctors = []
        
        # Enhanced patterns for doctor extraction including Fetal Medicine
        patterns = [
            r'((?:Prof\.\s+)?(?:Col\.\(R\)\.\s+)?(?:Brig\.\s+)?Dr\.\s+[A-Za-z\s\-\.()]+?)\s+(Peadiatrician|Pediatrician|Cardiologist|Urologist|Gynecologist|Orthopedic|Neurologist|Anesthesiologist|Radiologist|General\s+Surgeon|ENT|Physiotherapist|Plastic\s+Surgeon|Gastroenterologist|Nephrologist|Endocrinologist|Dermatologist|Oncologist|Psychiatrist|Dental\s+Surgeon|Lactation\s+Specialist|Ophthalmologist|Opthalmologist|Speech\s+and\s+Language\s+Therapist|Infectious\s+Disease\s+Specialist|Rheumatologist|Pulmonologist|Interventional\s+Radiologist|Cardiac\s+Surgeon|Neurosurgeon|Peads\s+Surgeon|Paeds\s+Cardiologist|Peads\s+Cardiologist|Peads\s+Hemotologist|Endocrinologist/\s+Diabaties|Fetal\s+Medicine)\s+((?:Prof\.\s+)?(?:Col\.\s+)?(?:Brig\.\s+)?Dr\.\s+[A-Za-z\s\-\.()]+?)\s+Specialit?y\s+([A-Za-z\s&/(),.-]+?)\s+Degrees\s+([^A-Z]+?)(?:\s+Areas|\s+Clinic|\s+Appointment|(?=(?:Prof\.\s+)?Dr\.)|$)',
            r'((?:Prof\.\s+)?(?:Col\.\s+)?(?:Brig\.\s+)?Dr\.\s+[A-Za-z\s\-\.()]+?)\s+Specialit?y\s+([A-Za-z\s&/(),.-]+?)\s+Degrees\s+([^A-Z]+?)(?:\s+Areas|\s+Clinic|\s+Appointment|(?=(?:Prof\.\s+)?Dr\.)|$)',
            r'(?:Prof\.\s+)?(?:Col\.\(R\)\.\s+)?(?:Brig\.\s+)?Dr\.\s+([A-Za-z\s\-\.()]+?)(?:\s+(?:MBBS|MD|FCPS|MS|PhD|BSc|MSc|FRCS|MRCP|FACS|FICS|MCPS|Specialist|Consultant|Professor|Senior|Head|Department|Specialty|Degrees|Areas|Clinic|Appointment|Fetal\s+Medicine)|\s*[-–]\s*|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) >= 5:
                        name, specialty1, name2, specialty2, degrees = match[:5]
                        doctor_name = self.clean_doctor_name(name2 if name2 else name)
                        doctor_specialty = specialty2 if specialty2 else specialty1
                    elif len(match) >= 3:
                        name, specialty, degrees = match[:3]
                        doctor_name = self.clean_doctor_name(name)
                        doctor_specialty = specialty
                    elif len(match) >= 1:
                        name = match[0] if isinstance(match, tuple) else match
                        doctor_name = self.clean_doctor_name(f"Dr. {name}")
                        doctor_specialty = None
                else:
                    doctor_name = self.clean_doctor_name(f"Dr. {match}")
                    doctor_specialty = None
                
                if doctor_name and len(doctor_name) > 8:
                    doctors.append({
                        'name': doctor_name,
                        'specialization': doctor_specialty,
                        'extracted_from': 'comprehensive_text_extraction'
                    })
        
        # Remove duplicates
        seen = set()
        unique_doctors = []
        for doctor in doctors:
            if doctor['name'] not in seen:
                seen.add(doctor['name'])
                unique_doctors.append(doctor)
        
        return unique_doctors

    def extract_qualifications_from_content(self, content):
        """Extract qualifications from content"""
        qualifications = []
        
        if not content:
            return qualifications
            
        patterns = [
            r'Degrees\s+([^A-Z]*?)(?:\s+Areas|\s+Clinic|\s+Appointment|\s+©|$)',
            r'Degrees\s+(.+?)(?:\s+Areas of Expertise|\s+Clinic|\s+Appointment|\s+©|$)',
            r'Specialty\s+[^D]*?Degrees\s+(.+?)(?:\s+Areas|\s+Clinic|\s+Appointment|\s+©|$)',
            r'(?:MBBS|MD|FCPS|MS|PhD|BSc|MSc|FRCS|MRCP|FACS|FICS|MCPS|DCH|DMRD|DABIM|FAAP|FACPS|MRCPCH|PGPN|FRSC|FIPP|FRCOG|DAOUS|RGOC|RCR)[^A-Za-z]*(?:[,;]\s*(?:MBBS|MD|FCPS|MS|PhD|BSc|MSc|FRCS|MRCP|FACS|FICS|MCPS|DCH|DMRD|DABIM|FAAP|FACPS|MRCPCH|PGPN|FRSC|FIPP|FRCOG|DAOUS|RGOC|RCR)[^A-Za-z]*)*'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                degrees_text = match.group(1).strip()
                degrees_text = re.sub(r'\s+', ' ', degrees_text)
                
                quals = re.split(r'[,;]+(?![^()]*\))', degrees_text)
                for qual in quals:
                    qual = qual.strip().rstrip('.,;()')
                    if (qual and len(qual) > 1 and len(qual) < 150 and 
                        not any(noise in qual.lower() for noise in ['areas of expertise', 'clinic', 'appointment', 'profile', 'home'])):
                        qualifications.append(qual)
                
                if qualifications:
                    break
        
        return qualifications

    def process_all_data(self, items):
        """Process all data from scraped items"""
        print("🔄 Processing raw scraped data with enhanced doctor extraction...")
        
        # First, add all pediatric doctors to the main doctors array
        print("🏥 Adding pediatric doctors to main doctors array...")
        for pediatric_doctor in self.pediatric_doctors:
            self.doctors[pediatric_doctor['name']] = {
                'name': pediatric_doctor['name'],
                'specialization': pediatric_doctor['specialization'],
                'qualifications': pediatric_doctor['qualifications'],
                'subspecialty': pediatric_doctor['subspecialty'],
                'appointment_number': None,
                'areas_of_expertise': [],
                'description': None,
                'profile_url': None,
                'extracted_from': 'pediatric_manual_entry',
                'docter_id': None,
                'department_id': None
            }
        
        # Process all other items
        for item in items:
            # Process doctor profiles
            if item.get('page_type') == 'doctor_profile':
                doctor_info = self.process_doctor_profile(item)
                if doctor_info and doctor_info['name'] not in self.doctors:
                    # add placeholders for ids
                    doctor_info['docter_id'] = None
                    doctor_info['department_id'] = None
                    self.doctors[doctor_info['name']] = doctor_info
            
            # Process department pages
            elif item.get('page_type') == 'department_page':
                dept_info = self.process_department_page(item)
                if dept_info:
                    self.raw_departments[dept_info['name']] = dept_info
            
            # Process general pages that might be departments
            elif item.get('page_type') == 'general_page':
                url = item.get('url', '')
                if '/dermatology-cosmetology/' in url:
                    item_copy = item.copy()
                    item_copy['page_type'] = 'department_page'
                    dept_info = self.process_department_page(item_copy)
                    if dept_info:
                        dept_info['name'] = 'Dermatology'
                        self.raw_departments['Dermatology'] = dept_info
        
        # Assign sequential IDs to all doctors
        for doctor_name, doctor_info in self.doctors.items():
            if doctor_info.get('docter_id') is None:
                doctor_info['docter_id'] = self._next_doctor_id
                self._next_doctor_id += 1
        
        print(f"✅ Processed {len(self.doctors)} total doctors")
        print(f"✅ Processed {len(self.raw_departments)} raw departments")
        print(f"✅ Added {len(self.pediatric_doctors)} pediatric doctors manually")

    def process_doctor_profile(self, item):
        """Process doctor profile pages"""
        if item.get('page_type') != 'doctor_profile':
            return None
            
        doctor_profile = item.get('doctor_profile', {})
        main_content = item.get('main_content', '')
        url = item.get('url', '')
        
        raw_name = doctor_profile.get('name')
        if not raw_name:
            return None
            
        clean_name = self.clean_doctor_name(raw_name)
        if not clean_name:
            return None
        
        specialization = doctor_profile.get('specialization')
        if not specialization and main_content:
            spec_match = re.search(r'Specialit?y\s+([A-Za-z\s&/(),.-]+?)(?:\s+Degrees|\s+Areas|\s+©|$)', main_content, re.IGNORECASE)
            if spec_match:
                specialization = spec_match.group(1).strip()
        
        qualifications = self.extract_qualifications_from_content(main_content)
        if not qualifications:
            qualifications = doctor_profile.get('qualifications', [])
        
        appointment_number = doctor_profile.get('appointment_number')
        if not appointment_number and main_content:
            appt_match = re.search(r'Appointment\s+Number\s*:?\s*([+\d\s()-]+)', main_content, re.IGNORECASE)
            if appt_match:
                appointment_number = appt_match.group(1).strip()
        
        expertise = doctor_profile.get('expertise', [])
        if not expertise or expertise == ['Clinic']:
            expertise_match = re.search(r'Areas of Expertise\s+([^©]+?)(?:Clinic|Appointment|©|$)', main_content, re.IGNORECASE)
            if expertise_match:
                expertise_text = expertise_match.group(1).strip()
                expertise = [exp.strip() for exp in expertise_text.split() if exp.strip() and exp.strip() != 'Clinic']
        
        return {
            'name': clean_name,
            'specialization': specialization,
            'qualifications': qualifications,
            'appointment_number': appointment_number,
            'areas_of_expertise': expertise,
            'description': doctor_profile.get('description'),
            'profile_url': url,
            'extracted_from': 'doctor_profile_page'
        }

    def process_department_page(self, item):
        """Process department pages with enhanced doctor extraction"""
        if item.get('page_type') != 'department_page':
            return None
            
        main_content = item.get('main_content', '')
        url = item.get('url', '')
        title = item.get('title', '')
        
        # Extract department name and map to target departments
        dept_name = None
        if '/departments/' in url:
            url_parts = url.rstrip('/').split('/')
            if url_parts and url_parts[-1]:
                url_name = url_parts[-1].replace('-', ' ').title()
                dept_name = self.map_to_target_department(url_name)
        
        if not dept_name and title:
            title_name = title.split('-')[0].strip()
            dept_name = self.map_to_target_department(title_name)
            
        if not dept_name:
            return None
        
        # Extract doctors from multiple sources (names only)
        dept_doctor_names = []
        
        # 1. Extract from malformed arrays
        if item.get('doctors'):
            for malformed_doctor in item['doctors']:
                if isinstance(malformed_doctor, str):
                    doctor_info = self.extract_doctors_from_malformed_text(malformed_doctor)
                    if doctor_info:
                        dept_doctor_names.append(doctor_info['name'])
        
        # 2. Extract from comprehensive text content
        content_doctors = self.extract_doctors_from_comprehensive_text(main_content)
        for doctor_info in content_doctors:
            if doctor_info['name'] not in dept_doctor_names:
                dept_doctor_names.append(doctor_info['name'])
        
        # 3. Extract from other content fields
        for field in ['services', 'procedures', 'faqs', 'descriptions']:
            if item.get(field):
                field_content = ' '.join(item[field]) if isinstance(item[field], list) else str(item[field])
                field_doctors = self.extract_doctors_from_comprehensive_text(field_content)
                for doctor_info in field_doctors:
                    if doctor_info['name'] not in dept_doctor_names:
                        dept_doctor_names.append(doctor_info['name'])
        
        return {
            'name': dept_name,
            'description': self.clean_text(main_content),
            'services': self.extract_list_content(item, 'services'),
            'procedures': self.extract_list_content(item, 'procedures'),
            'faqs': self.extract_list_content(item, 'faqs'),
            'doctor_names': list(set(dept_doctor_names)),
            'facilities': self.extract_list_content(item, 'facilities'),
            'url': url,
            'extracted_from': 'department_page_enhanced'
        }

    def map_to_target_department(self, extracted_name):
        """Map extracted department names to target department names"""
        name_mappings = {
            'Anesthesiology': 'Anesthesia and Pain Management',
            'Anesthesia': 'Anesthesia and Pain Management',
            'Cardiac And Vascular Surgery': 'Cardiac and Vascular Surgery',
            'Dietetics & Nutrition': 'Dietetics & Nutrition',
            'Gynecology And Obstetrics': 'Gynecology and Obstetrics',
            'Gynecology': 'Gynecology and Obstetrics',
            'Infectious Diseases Department': 'Infectious Diseases',
            'Nephrology': 'Nephrology & Dialysis',
            'Neurology & Stroke Management': 'Neurology & Stroke Management',
            'Neurology': 'Neurology & Stroke Management',
            'Neurosurgery & Spine': 'Neurosurgery & Spine',
            'Neurosurgery Spine': 'Neurosurgery & Spine',
            'Physiotherapy & Hydrotherapy': 'Physiotherapy & Hydrotherapy',
            'Physiotherapy': 'Physiotherapy & Hydrotherapy',
            'Urology And Lithotripsy': 'Urology and Lithotripsy',
            'Urology': 'Urology and Lithotripsy',
            'Pediatric Surgery': 'Pediatrics',
            'Pediatric Cardiology': 'Pediatrics',
            'Pediatric Urology': 'Pediatrics'
        }
        
        if extracted_name in name_mappings:
            return name_mappings[extracted_name]
        
        if extracted_name in self.target_departments:
            return extracted_name
        
        for target_dept in self.target_departments:
            if extracted_name.lower() in target_dept.lower() or target_dept.lower() in extracted_name.lower():
                return target_dept
        
        return extracted_name

    def extract_list_content(self, item, field_name):
        """Extract and clean list content"""
        content = []
        
        if item.get(field_name):
            if isinstance(item[field_name], list):
                content.extend(item[field_name])
            else:
                content.append(item[field_name])
        
        if item.get('department_info', {}).get(field_name):
            dept_content = item['department_info'][field_name]
            if isinstance(dept_content, list):
                content.extend(dept_content)
            else:
                content.append(dept_content)
        
        cleaned_content = []
        seen = set()
        
        for item_content in content:
            if item_content and isinstance(item_content, str):
                clean_item = self.clean_text(item_content)
                if (clean_item and len(clean_item.strip()) > 10 and 
                    clean_item not in seen):
                    cleaned_content.append(clean_item)
                    seen.add(clean_item)
        
        return cleaned_content

    def clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ""
            
        text = re.sub(r'\s+', ' ', text).strip()
        
        noise_patterns = [
            r'© \d{4} Hameed Latif Hospital[^.]*',
            r'All rights reserved[^.]*',
            r'Powered by[^.]*',
            r'Skip to content',
            r'Back to top',
            r'FIRST NAME PHONE NUMBER.*',
            r'We will contact you within one business day.*'
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()

    def assign_all_doctors_to_departments(self, consolidated_departments):
        """CRITICAL FIX: Assign ALL doctors from all_doctors to appropriate departments"""
        print("🔄 CRITICAL FIX: Assigning ALL doctors to departments...")
        
        # Enhanced specialization mapping
        specialization_mapping = {
            'Anesthesiologist': 'Anesthesia and Pain Management',
            'Anesthesia Consultant': 'Anesthesia and Pain Management',
            'Pain Physician': 'Anesthesia and Pain Management',
            'Cardiologist': 'Interventional Cardiology',
            'Cardiac Surgeon': 'Cardiac Surgery',
            'Urologist': 'Urology and Lithotripsy',
            'Gynecologist': 'Gynecology and Obstetrics',
            'Orthopedic': 'Orthopedics',
            'Orthopedic Surgeon': 'Orthopedics',
            'Neurologist': 'Neurology & Stroke Management',
            'Neuro Surgeon': 'Neurosurgery & Spine',
            'Neurosurgeon': 'Neurosurgery & Spine',
            'Radiologist': 'Radiology',
            'General Surgeon': 'General Surgery',
            'Plastic Surgeon': 'Plastic Surgery',
            'ENT': 'ENT',
            'ENT Consultant': 'ENT',
            'Physiotherapist': 'Physiotherapy & Hydrotherapy',
            'Dermatologist': 'Dermatology',
            'Psychiatrist': 'Psychiatry',
            'Oncologist': 'Oncology',
            'Pulmonologist': 'Pulmonology',
            'Nephrologist': 'Nephrology & Dialysis',
            'Endocrinologist': 'Endocrinology',
            'Rheumatologist': 'Rheumatology',
            'Gastroenterologist': 'Gastroenterology',
            'Ophthalmologist': 'Ophthalmology',
            'Opthalmologist': 'Ophthalmology',
            'Infectious Disease Specialist': 'Infectious Diseases',
            'Speech and Language Therapist': 'Speech Therapy',
            'Lactation Specialist': 'Lactation Management',
            'Dental Surgeon': 'Dental',
            'Fetal Medicine': 'Fetal Medicine',
            'Fetal Medicine Specialist': 'Fetal Medicine'
        }
        
        # Additional keyword-based mapping for doctors with None specialization
        keyword_mapping = {
            'anesthesia': 'Anesthesia and Pain Management',
            'pain': 'Anesthesia and Pain Management',
            'cardiac': 'Cardiac Surgery',
            'heart': 'Cardiac Surgery',
            'urology': 'Urology and Lithotripsy',
            'gynecology': 'Gynecology and Obstetrics',
            'obstetrics': 'Gynecology and Obstetrics',
            'orthopedic': 'Orthopedics',
            'bone': 'Orthopedics',
            'neurology': 'Neurology & Stroke Management',
            'neuro': 'Neurosurgery & Spine',
            'spine': 'Neurosurgery & Spine',
            'radiology': 'Radiology',
            'surgery': 'General Surgery',
            'plastic': 'Plastic Surgery',
            'ent': 'ENT',
            'ear': 'ENT',
            'nose': 'ENT',
            'throat': 'ENT',
            'physiotherapy': 'Physiotherapy & Hydrotherapy',
            'dermatology': 'Dermatology',
            'skin': 'Dermatology',
            'psychiatry': 'Psychiatry',
            'mental': 'Psychiatry',
            'oncology': 'Oncology',
            'cancer': 'Oncology',
            'pulmonology': 'Pulmonology',
            'lung': 'Pulmonology',
            'nephrology': 'Nephrology & Dialysis',
            'kidney': 'Nephrology & Dialysis',
            'endocrinology': 'Endocrinology',
            'diabetes': 'Endocrinology',
            'rheumatology': 'Rheumatology',
            'gastroenterology': 'Gastroenterology',
            'stomach': 'Gastroenterology',
            'ophthalmology': 'Ophthalmology',
            'eye': 'Ophthalmology',
            'infectious': 'Infectious Diseases',
            'speech': 'Speech Therapy',
            'lactation': 'Lactation Management',
            'dental': 'Dental',
            'fetal': 'Fetal Medicine',
            'pregnancy': 'Fetal Medicine'
        }
        
        assigned_count = 0
        unassigned_doctors = []
        
        for doctor_name, doctor_info in self.doctors.items():
            # Skip pediatric doctors here; they are handled separately during consolidation
            if doctor_name in [pd['name'] for pd in self.pediatric_doctors]:
                continue
            
            specialization = doctor_info.get('specialization', '')
            assigned = False
            
            # Try specialization-based mapping first
            if specialization and specialization in specialization_mapping:
                target_dept_name = specialization_mapping[specialization]
                if target_dept_name in consolidated_departments:
                    self.add_doctor_to_department(consolidated_departments[target_dept_name], doctor_info)
                    assigned = True
                    assigned_count += 1
                    print(f"  ✅ {doctor_name} -> {target_dept_name} (by specialization: {specialization})")
            
            # Try keyword-based mapping if not assigned
            if not assigned:
                search_text = f"{doctor_name} {specialization}".lower()
                for keyword, target_dept_name in keyword_mapping.items():
                    if keyword in search_text and target_dept_name in consolidated_departments:
                        self.add_doctor_to_department(consolidated_departments[target_dept_name], doctor_info)
                        assigned = True
                        assigned_count += 1
                        print(f"  ✅ {doctor_name} -> {target_dept_name} (by keyword: {keyword})")
                        break
            
            # If still not assigned, add to unassigned list
            if not assigned:
                unassigned_doctors.append((doctor_name, specialization))
        
        print(f"\n📊 Assignment Results:")
        print(f"  - Successfully assigned: {assigned_count}")
        print(f"  - Unassigned doctors: {len(unassigned_doctors)}")
        
        if unassigned_doctors:
            print(f"\n❌ Unassigned doctors:")
            for i, (name, spec) in enumerate(unassigned_doctors, 1):
                print(f"  {i:2d}. {name} ({spec or 'No specialization'})")
        
        # Update department doctor counts
        for dept_name, dept_info in consolidated_departments.items():
            dept_info['total_doctors'] = len(dept_info['docter_ids'])
        
        return consolidated_departments

    def add_doctor_to_department(self, department, doctor_info):
        """Link a doctor to a department using IDs only"""
        doctor_id = doctor_info.get('docter_id')
        if doctor_id is None:
            return
        if doctor_id not in department['docter_ids']:
            department['docter_ids'].append(doctor_id)
        # Assign doctor's department_id if not already set
        if not doctor_info.get('department_id'):
            doctor_info['department_id'] = department['department_id']

    def assign_orphan_doctors_with_heuristics(self, consolidated_departments):
        """Heuristically assign orphan doctors using department page doctor_names and text keywords"""
        print("🧠 Heuristic assignment: resolving orphan doctors...")
        # Build name -> department mapping from raw_departments doctor_names
        name_to_dept_candidates = {}
        for raw_dept_name, raw_dept_info in self.raw_departments.items():
            names = raw_dept_info.get('doctor_names', [])
            if not names:
                continue
            for nm in names:
                name_to_dept_candidates.setdefault(nm.strip(), set()).add(self.map_to_target_department(raw_dept_name))
        
        # Simple keyword hints from department names
        dept_keywords = {dept_name.lower(): dept_name for dept_name in consolidated_departments.keys()}
        
        assigned = 0
        for doc_name, doc in self.doctors.items():
            if doc_name in [pd['name'] for pd in self.pediatric_doctors]:
                continue
            if doc.get('department_id'):
                continue
            # 1) Exact/normalized name presence on department pages
            candidates = name_to_dept_candidates.get(doc_name)
            if candidates:
                # pick first available consolidated dept
                for cand in candidates:
                    if cand in consolidated_departments:
                        self.add_doctor_to_department(consolidated_departments[cand], doc)
                        assigned += 1
                        break
                if doc.get('department_id'):
                    continue
            # 2) Text-based keyword scan across doc fields
            text_parts = [
                str(doc.get('description') or ''),
                ' '.join(doc.get('areas_of_expertise') or []),
                str(doc.get('specialization') or ''),
                str(doc.get('profile_url') or ''),
            ]
            blob = (' '.join(text_parts)).lower()
            matched_dept = None
            for key, dept_name in dept_keywords.items():
                if key in blob and dept_name in consolidated_departments:
                    matched_dept = dept_name
                    break
            if matched_dept:
                self.add_doctor_to_department(consolidated_departments[matched_dept], doc)
                assigned += 1
        
        # Recompute totals
        for dept in consolidated_departments.values():
            dept['total_doctors'] = len(dept['docter_ids'])
        print(f"🧾 Heuristic assignment completed. Newly assigned: {assigned}")
        return consolidated_departments

    def consolidate_final_departments(self):
        """Create final consolidated departments matching target structure"""
        print("🔄 Consolidating departments to match target structure...")
        
        consolidated = {}
        
        # Initialize all target departments with IDs
        for target_dept in self.target_departments:
            dept_id = self._next_department_id
            self._next_department_id += 1
            self.department_name_to_id[target_dept] = dept_id
            consolidated[target_dept] = {
                'department_id': dept_id,
                'name': target_dept,
                'description': '',
                'services': [],
                'procedures': [],
                'faqs': [],
                'docter_ids': [],
                'facilities': [],
                'subspecialties': [],
                'url': '',
                'extracted_from': 'target_structure',
                'total_doctors': 0,
                'last_updated': datetime.now().isoformat()
            }
        
        # Map raw departments to target departments
        for raw_dept_name, raw_dept_info in self.raw_departments.items():
            target_dept = self.map_to_target_department(raw_dept_name)
            
            if target_dept in consolidated:
                # Merge content
                if len(raw_dept_info.get('description', '')) > len(consolidated[target_dept]['description']):
                    consolidated[target_dept]['description'] = raw_dept_info.get('description', '')
                
                consolidated[target_dept]['services'].extend(raw_dept_info.get('services', []))
                consolidated[target_dept]['procedures'].extend(raw_dept_info.get('procedures', []))
                consolidated[target_dept]['faqs'].extend(raw_dept_info.get('faqs', []))
                consolidated[target_dept]['facilities'].extend(raw_dept_info.get('facilities', []))
                
                if not consolidated[target_dept]['url']:
                    consolidated[target_dept]['url'] = raw_dept_info.get('url', '')
        
        # Special handling for Pediatrics - link pediatric doctors by IDs
        if 'Pediatrics' in consolidated:
            pediatric_subspecialties = []
            pediatrics_dept_id = consolidated['Pediatrics']['department_id']
            for pediatric_doctor in self.pediatric_doctors:
                name = pediatric_doctor['name']
                if name in self.doctors:
                    # ensure base info (already set in process_all_data)
                    doc = self.doctors[name]
                    # assign department
                    doc['department_id'] = pediatrics_dept_id
                    # add id to department list
                    if doc['docter_id'] not in consolidated['Pediatrics']['docter_ids']:
                        consolidated['Pediatrics']['docter_ids'].append(doc['docter_id'])
                    
                    if pediatric_doctor['subspecialty'] not in pediatric_subspecialties:
                        pediatric_subspecialties.append(pediatric_doctor['subspecialty'])
            
            consolidated['Pediatrics']['subspecialties'] = pediatric_subspecialties
            consolidated['Pediatrics']['total_doctors'] = len(consolidated['Pediatrics']['docter_ids'])
        
        # Remove duplicates from content lists
        for dept_name, dept_info in consolidated.items():
            dept_info['services'] = list(set(dept_info['services']))[:15]
            dept_info['procedures'] = list(set(dept_info['procedures']))[:15]
            dept_info['faqs'] = list(set(dept_info['faqs']))[:5]
            dept_info['facilities'] = list(set(dept_info['facilities']))
        
        # CRITICAL FIX: Assign ALL doctors to departments
        consolidated = self.assign_all_doctors_to_departments(consolidated)
        
        # Heuristic assignment for remaining orphans
        consolidated = self.assign_orphan_doctors_with_heuristics(consolidated)
        
        print(f"✅ Consolidated {len(consolidated)} departments with ALL doctors assigned")
        return consolidated

    def create_final_output(self, consolidated_departments):
        """Create the final formatted JSON output"""
        total_doctors_in_depts = sum(len(dept['docter_ids']) for dept in consolidated_departments.values())
        
        # Convert mapping structures to lists for tabular output
        departments_list = list(consolidated_departments.values())
        doctors_list = list(self.doctors.values())
        
        output_data = {
            'hospital_info': {
                'name': 'Hameed Latif Hospital',
                'location': 'Lahore, Pakistan',
                'main_phone': '+92 (42) 111-000-043',
                'website': 'https://www.hameedlatifhospital.com',
                'address': '14- Abu Baker Block, New Garden Town, Lahore'
            },
            'departments': departments_list,
            'doctors': doctors_list,
            'data_summary': {
                'total_departments': len(departments_list),
                'total_doctors': len(doctors_list),
                'total_doctors_in_departments': total_doctors_in_depts,
                'departments_with_doctors': sum(1 for dept in departments_list if dept['docter_ids']),
                'average_doctors_per_department': round(total_doctors_in_depts / len(departments_list), 2) if departments_list else 0
            },
            'extraction_metadata': {
                'formatted_at': datetime.now().isoformat(),
                'source_file': self.input_file,
                'formatter_version': '6.3 - docter_id keys & docter_ids lists',
                'notes': 'Departments use department_id and docter_ids; doctors use docter_id and department_id',
                'pediatric_doctors_manually_added': len(self.pediatric_doctors)
            }
        }
        
        return output_data

    def save_data(self, output_data):
        """Save the final data to JSON file"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            stats = output_data['data_summary']
            print(f"\n✅ SUCCESS! Saved fully consistent data to {self.output_file}")
            print(f"📊 Final Statistics:")
            print(f"  - Total departments: {stats['total_departments']}")
            print(f"  - Total unique doctors: {stats['total_doctors']}")
            print(f"  - Doctors in departments: {stats['total_doctors_in_departments']}")
            print(f"  - Departments with doctors: {stats['departments_with_doctors']}")
            print(f"  - Average per department: {stats['average_doctors_per_department']}")
            
            return True
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False

    def run(self):
        """Run the final corrected hospital data formatting with ALL doctors assigned"""
        print("🚀 Starting FINAL CORRECTED hospital data formatting V3...")
        print("   (CRITICAL FIX: Assigns ALL doctors from all_doctors to departments)")
        
        items = self.load_scraped_data()
        if not items:
            print("❌ Failed to load raw data!")
            return False
        
        print(f"✅ Loaded {len(items)} raw items")
        
        # Process all data
        self.process_all_data(items)
        
        # Consolidate departments with ALL doctors assigned
        consolidated_departments = self.consolidate_final_departments()
        
        # Create final output
        final_data = self.create_final_output(consolidated_departments)
        
        # Save final data
        success = self.save_data(final_data)
        
        if success:
            print("\n🎉 FINAL CORRECTED V3 formatting completed successfully!")
            print("🔧 ALL doctors have ids and department_id; departments store doctor_ids!")
        
        return success

def main():
    """Main function to run the final corrected formatter V3"""
    formatter = FinalCorrectedHospitalFormatterV3(
        input_file='/Users/macworld/Desktop/HameedLateef/scrapper/improved_hospital_data.json',
        output_file='/Users/macworld/Desktop/HameedLateef/final_corrected_hospital_data_v3.json'
    )
    
    success = formatter.run()
    
    if success:
        print("✨ All done! Check the final_corrected_hospital_data_v3.json file for results.")
        print("🔧 This version ensures ALL doctors are assigned to departments.")
    else:
        print("💥 Something went wrong during final corrected V3 formatting.")

if __name__ == "__main__":
    main()
