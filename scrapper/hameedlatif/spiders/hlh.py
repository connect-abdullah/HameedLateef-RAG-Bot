import scrapy
import re
from datetime import datetime
from urllib.parse import urljoin
from hameedlatif.items import HameedlatifItem


class HLHSpider(scrapy.Spider):
    name = "hlh"
    allowed_domains = ["hameedlatifhospital.com"]

    start_urls = [
        "https://www.hameedlatifhospital.com/",  # Homepage
        "https://www.hameedlatifhospital.com/doctors/",
        "https://www.hameedlatifhospital.com/departments/",
        "https://www.hameedlatifhospital.com/visitors-information-guide/",
        "https://www.hameedlatifhospital.com/board-of-directors/",
        "https://www.hameedlatifhospital.com/hlh-core-committee/",
        "https://www.hameedlatifhospital.com/news-events/",
        "https://www.hameedlatifhospital.com/life-infertility-services/",
        "https://www.hameedlatifhospital.com/dermatology-cosmetology/",
        "https://www.hameedlatifhospital.com/executive-health-clinic/",
        "https://www.hameedlatifhospital.com/hameed-latif-medical-centre/",
        "https://www.hameedlatifhospital.com/pharmacy-24-7/",
        "https://www.hameedlatifhospital.com/blood-bank-24-7/",
        "https://www.hameedlatifhospital.com/cafeteria/",
        "https://www.hameedlatifhospital.com/post-graduate-trainings/",
        "https://www.hameedlatifhospital.com/contact-us/",
        "https://www.hameedlatifhospital.com/about-us/",
        "https://www.hameedlatifhospital.com/hlh-doctors/",
    ]

    def __init__(self):
        self.visited_urls = set()

    def clean_text(self, text):
        """Clean text by removing extra whitespace and unwanted characters"""
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove common website noise
        noise_patterns = [
            r'Skip to content', r'Back to top', r'Home\s*\|', r'Menu',
            r'window\.', r'jQuery', r'javascript:', r'function\s*\(',
        ]
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()

    def remove_navbar_repetition(self, content):
        """Remove navbar repetition from content"""
        if not content:
            return ""
        
        # Common navbar patterns to remove
        navbar_patterns = [
            r'\+92 \(42\) 111-000-043 Download Brochure \| Complaint.*?Contact Us',
            r'About Us Board of Directors Visitors Information Guide.*?Contact Us',
            r'Clinical Departments Fetal Medicine Gynecology.*?Contact Us',
            r'LIFE \(Fertility Services\) Dermatology & Cosmetology.*?Contact Us',
        ]
        
        for pattern in navbar_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        return content.strip()

    def extract_clean_content(self, response):
        """Extract only clean, meaningful content avoiding navbar repetition"""
        try:
            # First try to get main content area
            main_selectors = [
                '.entry-content',
                '.post-content', 
                '.page-content',
                'main',
                'article',
                '.content-area',
                '.site-content'
            ]
            
            main_content = []
            for selector in main_selectors:
                content = response.css(f'{selector} *::text').getall()
                if content:
                    main_content = content
                    break
            
            # If no main content found, get body but exclude header/footer/nav
            if not main_content:
                main_content = response.css('body *:not(header):not(footer):not(nav):not(script):not(style)::text').getall()
            
            # Clean and filter meaningful content
            clean_texts = []
            for text in main_content:
                cleaned = self.clean_text(text)
                if cleaned and len(cleaned.strip()) > 2:
                    clean_texts.append(cleaned)
            
            # Join and remove navbar repetition
            full_content = ' '.join(clean_texts)
            clean_content = self.remove_navbar_repetition(full_content)
            
            return clean_content
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {response.url}: {e}")
            return ""

    def extract_doctor_info(self, content, url):
        """Extract individual doctor information"""
        if '/doctors/' not in url or url.endswith('/doctors/') or url.endswith('/doctors'):
            return None
        
        doctor_info = {
            'name': None,
            'specialization': None,
            'qualifications': [],
            'appointment_number': None,
            'room': None,
            'expertise': [],
            'description': None
        }
        
        # Extract doctor name from URL
        url_parts = url.rstrip('/').split('/')
        if url_parts and url_parts[-1]:
            name_slug = url_parts[-1]
            # Handle both "dr-name" and just "name" formats
            if name_slug.startswith('dr-'):
                name_parts = name_slug.replace('dr-', '').replace('-', ' ').split()
            else:
                name_parts = name_slug.replace('-', ' ').split()
            
            # Always add "Dr." prefix if not already present
            doctor_name = 'Dr. ' + ' '.join([part.capitalize() for part in name_parts])
            doctor_info['name'] = doctor_name
        
        # Extract specialization - MULTIPLE PATTERNS for comprehensive extraction
        specialization = None
        
        # Pattern 1: "Specialty [specialization]" or "Speciality [specialization]" - IMPROVED
        spec_match = re.search(r'Specialit?y\s+([^A-Z]*?)(?:\s+Degrees|\s+Areas|\s+Clinic|\s+Appointment|\s+©|$)', content, re.IGNORECASE)
        if spec_match:
            specialization = spec_match.group(1).strip()
        
        # Pattern 2: Doctor name followed by specialization - IMPROVED
        if not specialization and doctor_info['name']:
            name_without_dr = doctor_info['name'].replace('Dr. ', '').strip()
            # Look for name followed by specialization (more flexible)
            name_spec_pattern = rf'{re.escape(name_without_dr)}\s+([^A-Z]*?)(?:\s+Specialty|\s+Degrees|\s+Areas|\s+©|$)'
            name_spec_match = re.search(name_spec_pattern, content, re.IGNORECASE)
            if name_spec_match:
                potential_spec = name_spec_match.group(1).strip()
                # Filter out noise but be more lenient
                if (len(potential_spec) > 3 and len(potential_spec) < 200 and 
                    not any(noise in potential_spec.lower() for noise in ['home', 'hospital', 'contact', 'hameed latif', 'appointment number'])):
                    specialization = potential_spec
        
        # Pattern 3: Look for common medical specializations directly
        if not specialization:
            specializations = [
                'Pulmonologist', 'Ophthalmologist', 'Opthalmologist', 'Cardiologist', 'Neurologist', 
                'Orthopedic', 'Gynecologist', 'Urologist', 'Dermatologist', 'Psychiatrist',
                'Anesthesiologist', 'Radiologist', 'Gastroenterologist', 'Nephrologist',
                'Oncologist', 'Pediatrician', 'Peadiatrician', 'General Surgeon', 'Plastic Surgeon',
                'Cardiac Surgeon', 'Neuro Surgeon', 'ENT Consultant', 'Endocrinologist',
                'Infectious Disease Specialist', 'Pain Physician', 'Fetal Medicine'
            ]
            
            for spec in specializations:
                if spec.lower() in content.lower():
                    specialization = spec
                    break
        
        # Clean and validate specialization
        if specialization:
            specialization = re.sub(r'\s+', ' ', specialization).strip()
            # Remove if it's just the doctor name repeated or common noise
            name_without_dr = doctor_info['name'].replace('Dr. ', '').strip() if doctor_info['name'] else ""
            if (specialization.lower() != name_without_dr.lower() and 
                not any(noise in specialization.lower() for noise in ['home', 'hospital', 'contact us', 'appointment', 'hameed latif'])):
                doctor_info['specialization'] = specialization
        
        # Extract qualifications - COMPREHENSIVE PATTERNS
        qualifications = []
        
        # Pattern 1: "Degrees [qualifications]" - IMPROVED
        degrees_match = re.search(r'Degrees\s+([^A-Z]*?)(?:\s+Areas|\s+Clinic|\s+Appointment|\s+©|$)', content, re.IGNORECASE)
        if degrees_match:
            degrees_text = degrees_match.group(1).strip()
            # Handle complex degrees with parentheses and descriptions
            # Split by common separators but preserve parentheses content
            quals = re.split(r'[,;]+(?![^()]*\))', degrees_text)  # Don't split inside parentheses
            for qual in quals:
                qual = qual.strip().rstrip('.,;')
                if qual and len(qual) > 1 and len(qual) < 200:  # Increased length limit
                    qualifications.append(qual)
        
        # Pattern 2: Look for common medical qualifications directly in content - COMPREHENSIVE
        if not qualifications:
            # COMPREHENSIVE medical and healthcare qualification patterns
            qual_patterns = [
                # Basic Medical Degrees
                r'\b(M\.?B\.?B\.?S\.?)\b',
                r'\b(M\.?D\.?)\b',
                r'\b(D\.?O\.?)\b',
                r'\b(D\.?D\.?S\.?)\b',  # Doctor of Dental Surgery
                r'\b(B\.?D\.?S\.?)\b',  # Bachelor of Dental Surgery
                r'\b(D\.?M\.?D\.?)\b',  # Doctor of Medicine
                r'\b(D\.?V\.?M\.?)\b',  # Doctor of Veterinary Medicine
                
                # Fellowship Degrees
                r'\b(F\.?C\.?P\.?S\.?(?:\s*\([^)]+\))?)\b',
                r'\b(F\.?R\.?C\.?S\.?(?:\s*\([^)]+\))?)\b',
                r'\b(M\.?R\.?C\.?P\.?(?:\s*\([^)]+\))?)\b',
                r'\b(F\.?R\.?C\.?P\.?(?:\s*\([^)]+\))?)\b',
                r'\b(F\.?A\.?C\.?S\.?(?:\s*\([^)]+\))?)\b',
                r'\b(F\.?A\.?C\.?P\.?(?:\s*\([^)]+\))?)\b',
                r'\b(F\.?A\.?A\.?N\.?S\.?)\b',  # Fellowship American Association of Neurological Surgeons
                r'\b(F\.?I\.?C\.?S\.?)\b',  # Fellow of International College of Surgeons
                r'\b(F\.?R\.?C\.?O\.?G\.?)\b',  # Fellow Royal College of Obstetricians and Gynaecologists
                r'\b(F\.?R\.?C\.?R\.?)\b',  # Fellow Royal College of Radiologists
                r'\b(F\.?R\.?C\.?A\.?)\b',  # Fellow Royal College of Anaesthetists
                r'\b(F\.?I\.?P\.?P\.?(?:\s*\([^)]+\))?)\b',
                r'\b(F\.?I\.?C\.?O\.?)\b',
                r'\b(F\.?E\.?S\.?C\.?)\b',  # Fellow European Society of Cardiology
                r'\b(F\.?E\.?B\.?O\.?T\.?)\b',  # Fellow European Board of Orthopaedics and Traumatology
                
                # Membership Degrees
                r'\b(M\.?C\.?P\.?S\.?(?:\s*\([^)]+\))?)\b',
                r'\b(M\.?R\.?C\.?S\.?(?:\s*\([^)]+\))?)\b',
                r'\b(M\.?R\.?C\.?O\.?G\.?)\b',  # Member Royal College of Obstetricians and Gynaecologists
                r'\b(M\.?R\.?C\.?P\.?S\.?(?:\s*\([^)]+\))?)\b',
                r'\b(M\.?R\.?C\.?S\.?Ed\.?)\b',  # Member Royal College of Surgeons Edinburgh
                
                # Master's Degrees
                r'\b(M\.?S\.?(?:\s*\([^)]+\))?)\b',
                r'\b(M\.?Sc\.?(?:\s*\([^)]+\))?[^,]*)\b',  # MSc with specialization
                r'\b(M\.?Phil\.?(?:\s*\([^)]+\))?)\b',
                r'\b(M\.?P\.?H\.?(?:\s*\([^)]+\))?)\b',  # Master of Public Health
                r'\b(M\.?H\.?A\.?)\b',  # Master of Health Administration
                r'\b(M\.?H\.?S\.?)\b',  # Master of Health Sciences
                r'\b(M\.?N\.?)\b',  # Master of Nursing
                r'\b(M\.?S\.?N\.?)\b',  # Master of Science in Nursing
                r'\b(M\.?P\.?T\.?)\b',  # Master of Physical Therapy
                r'\b(M\.?O\.?T\.?)\b',  # Master of Occupational Therapy
                r'\b(M\.?H\.?P\.?E\.?)\b',  # Master of Health Professions Education
                
                # Bachelor's Degrees
                r'\b(B\.?S\.?c\.?(?:\s*\([^)]+\))?[^,]*)\b',  # BSc with specialization
                r'\b(B\.?A\.?(?:\s*\([^)]+\))?[^,]*)\b',  # BA with specialization
                r'\b(B\.?N\.?)\b',  # Bachelor of Nursing
                r'\b(B\.?S\.?N\.?)\b',  # Bachelor of Science in Nursing
                r'\b(B\.?P\.?T\.?)\b',  # Bachelor of Physical Therapy
                r'\b(B\.?O\.?T\.?)\b',  # Bachelor of Occupational Therapy
                r'\b(B\.?Pharm\.?)\b',  # Bachelor of Pharmacy
                r'\b(B\.?S\.?P\.?T\.?)\b',  # Bachelor of Science in Physical Therapy
                
                # Doctorate Degrees
                r'\b(Ph\.?D\.?(?:\s*\([^)]+\))?)\b',
                r'\b(D\.?Phil\.?(?:\s*\([^)]+\))?)\b',
                r'\b(Sc\.?D\.?)\b',  # Doctor of Science
                r'\b(Ed\.?D\.?)\b',  # Doctor of Education
                r'\b(D\.?N\.?P\.?)\b',  # Doctor of Nursing Practice
                r'\b(Pharm\.?D\.?)\b',  # Doctor of Pharmacy
                r'\b(D\.?P\.?T\.?)\b',  # Doctor of Physical Therapy
                r'\b(D\.?O\.?T\.?)\b',  # Doctor of Occupational Therapy
                r'\b(Psy\.?D\.?)\b',  # Doctor of Psychology
                
                # American Board Certifications
                r'\b(D\.?A\.?B\.?I\.?M\.?)\b',  # Diplomate American Board of Internal Medicine
                r'\b(D\.?A\.?P\.?B\.?D\.?)\b',  # Diplomate American Board of Pediatrics
                r'\b(D\.?A\.?B\.?C\.?C\.?M\.?(?:\s*\([^)]+\))?)\b',  # Diplomate American Board of Critical Care Medicine
                r'\b(D\.?A\.?B\.?N\.?)\b',  # Diplomate American Board of Neurology
                r'\b(D\.?A\.?B\.?M\.?)\b',  # Diplomate American Board of Medicine
                r'\b(D\.?A\.?B\.?R\.?)\b',  # Diplomate American Board of Radiology
                r'\b(D\.?A\.?B\.?P\.?)\b',  # Diplomate American Board of Pathology
                r'\b(D\.?A\.?B\.?A\.?)\b',  # Diplomate American Board of Anesthesiology
                r'\b(D\.?A\.?B\.?O\.?G\.?)\b',  # Diplomate American Board of Obstetrics and Gynecology
                r'\b(D\.?A\.?B\.?S\.?)\b',  # Diplomate American Board of Surgery
                r'\b(D\.?A\.?B\.?P\.?S\.?)\b',  # Diplomate American Board of Plastic Surgery
                r'\b(D\.?A\.?B\.?O\.?)\b',  # Diplomate American Board of Ophthalmology
                r'\b(D\.?A\.?B\.?D\.?)\b',  # Diplomate American Board of Dermatology
                r'\b(D\.?A\.?B\.?P\.?M\.?R\.?)\b',  # Diplomate American Board of Physical Medicine and Rehabilitation
                r'\b(D\.?A\.?B\.?E\.?M\.?)\b',  # Diplomate American Board of Emergency Medicine
                r'\b(D\.?A\.?B\.?F\.?M\.?)\b',  # Diplomate American Board of Family Medicine
                r'\b(DIPLOMATE\s+AMERICAN\s+BOARD\s+OF\s+[A-Z\s]+)\b',  # General pattern for American Board
                
                # Specialty Certifications
                r'\b(C\.?C\.?T\.?)\b',  # Certificate of Completion of Training
                r'\b(M\.?H\.?P\.?E\.?)\b',  # Master of Health Professions Education
                r'\b(T\.?P\.?C\.?(?:\s*\([^)]+\))?)\b',  # Training Program Certificate
                r'\b(T\.?D\.?P\.?T\.?)\b',  # Transitional Doctor of Physical Therapy
                r'\b(P\.?G\.?D\.?(?:\s*\([^)]+\))?)\b',  # Post Graduate Diploma
                r'\b(P\.?G\.?C\.?(?:\s*\([^)]+\))?)\b',  # Post Graduate Certificate
                
                # Nursing Specializations
                r'\b(R\.?N\.?)\b',  # Registered Nurse
                r'\b(L\.?P\.?N\.?)\b',  # Licensed Practical Nurse
                r'\b(N\.?P\.?)\b',  # Nurse Practitioner
                r'\b(C\.?N\.?A\.?)\b',  # Certified Nursing Assistant
                r'\b(C\.?R\.?N\.?A\.?)\b',  # Certified Registered Nurse Anesthetist
                
                # Allied Health Professions
                r'\b(R\.?P\.?T\.?)\b',  # Registered Physical Therapist
                r'\b(O\.?T\.?R\.?)\b',  # Occupational Therapist Registered
                r'\b(R\.?D\.?)\b',  # Registered Dietitian
                r'\b(C\.?D\.?E\.?)\b',  # Certified Diabetes Educator
                r'\b(R\.?T\.?)\b',  # Respiratory Therapist
                r'\b(M\.?T\.?)\b',  # Medical Technologist
                r'\b(R\.?A\.?)\b',  # Radiologic Technologist
                
                # International Qualifications
                r'\b(M\.?B\.?Ch\.?B\.?)\b',  # Bachelor of Medicine, Bachelor of Surgery
                r'\b(M\.?B\.?B\.?Ch\.?)\b',  # Bachelor of Medicine, Bachelor of Surgery
                r'\b(B\.?M\.?)\b',  # Bachelor of Medicine
                r'\b(B\.?Ch\.?)\b',  # Bachelor of Surgery
                r'\b(L\.?R\.?C\.?P\.?)\b',  # Licentiate of the Royal College of Physicians
                r'\b(L\.?R\.?C\.?S\.?)\b',  # Licentiate of the Royal College of Surgeons
                r'\b(D\.?R\.?C\.?O\.?G\.?)\b',  # Diploma of the Royal College of Obstetricians and Gynaecologists
                
                # Specialty Fields (as degrees)
                r'\b([A-Z][a-z]+\s+Science\s+and\s+Human\s+Nutrition)\b',  # Food Science and Human Nutrition
                r'\b([A-Z][a-z]+\s+Medicine(?:\s+\([^)]+\))?)\b',  # Pain Medicine, Sports Medicine, etc.
                r'\b([A-Z][a-z]+\s+Surgery(?:\s+\([^)]+\))?)\b',  # Plastic Surgery, Cardiac Surgery, etc.
                r'\b([A-Z][a-z]+\s+Therapy(?:\s+\([^)]+\))?)\b',  # Physical Therapy, Occupational Therapy, etc.
                r'\b([A-Z][a-z]+\s+Technology(?:\s+\([^)]+\))?)\b',  # Medical Technology, etc.
                r'\b([A-Z][a-z]+\s+Administration(?:\s+\([^)]+\))?)\b',  # Health Administration, etc.
                
                # Additional Medical Qualifications
                r'\b(A\.?F\.?S\.?M\.?)\b',  # Armed Forces Medical Services
                r'\b(M\.?P\.?P\.?S\.?)\b',  # Master in Public Policy and Strategy
                r'\b(C\.?H\.?P\.?E\.?)\b',  # Certified Health Physics Expert
                r'\b(F\.?I\.?P\.?M\.?)\b',  # Fellow of International Pain Management
                r'\b(D\.?I\.?P\.?L\.?O\.?M\.?A\.?T\.?E\.?)\b',  # Diplomate
            ]
            
            for pattern in qual_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match and match.strip() and match.strip() not in qualifications:
                        # Clean and format the qualification
                        clean_qual = match.strip().rstrip('.,;')
                        if len(clean_qual) > 1 and len(clean_qual) < 200:
                            qualifications.append(clean_qual)
        
        doctor_info['qualifications'] = qualifications
        
        # Extract appointment number - MULTIPLE PATTERNS
        appointment_number = None
        appt_patterns = [
            r'Appointment Number\s+([0-9\-+\s()]+)',
            r'Appointment\s*:\s*([0-9\-+\s()]+)',
            r'Contact\s*:\s*([0-9\-+\s()]+)',
            r'\b(03[0-9]{9})\b',  # Pakistani mobile numbers
            r'\b(0[0-9]{2,3}[\s\-]?[0-9]{7,8})\b'  # Pakistani landline numbers
        ]
        
        for pattern in appt_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                appointment_number = match.group(1).strip()
                break
        
        doctor_info['appointment_number'] = appointment_number
        
        # Extract room number
        room_match = re.search(r'Room\s*#?\s*([0-9A-Za-z\s]+?)(?:\s+Appointment|\s+©|\s+Areas|$)', content, re.IGNORECASE)
        if room_match:
            doctor_info['room'] = room_match.group(1).strip()
        
        # Extract areas of expertise - COMPREHENSIVE EXTRACTION
        expertise = []
        
        # Pattern 1: "Areas of Expertise [list]"
        expertise_match = re.search(r'Areas of Expertise\s+([^©]*?)(?:\s+Clinic|\s+Appointment|\s+©|$)', content, re.IGNORECASE)
        if expertise_match:
            expertise_text = expertise_match.group(1).strip()
            # Split by various separators
            areas = re.split(r'[,;\n•-]+', expertise_text)
            for area in areas:
                area = area.strip()
                if area and len(area) > 2 and len(area) < 200:
                    expertise.append(area)
        
        # Pattern 2: Look for common medical procedures/expertise
        if not expertise:
            expertise_keywords = [
                'Surgery', 'Treatment', 'Management', 'Procedure', 'Therapy', 'Care',
                'Consultation', 'Diagnosis', 'Screening', 'Examination', 'Laser'
            ]
            
            sentences = re.split(r'[.!?]+', content)
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 10 and len(sentence) < 200 and 
                    any(keyword in sentence for keyword in expertise_keywords)):
                    expertise.append(sentence)
                    if len(expertise) >= 10:  # Limit to avoid too much data
                        break
        
        doctor_info['expertise'] = expertise[:15]  # Limit to 15 areas
        
        # Extract description - COMPREHENSIVE DESCRIPTION EXTRACTION
        description = None
        
        # Pattern 1: Look for descriptive paragraphs about the doctor
        desc_patterns = [
            r'Having[^.]*\.[^.]*\.[^.]*\.',  # Sentences starting with "Having"
            r'Dr\.\s+[A-Za-z\s]+aims[^.]*\.[^.]*\.',  # Sentences about doctor's aims
            r'He believes[^.]*\.[^.]*\.',  # Sentences about beliefs
            r'She believes[^.]*\.[^.]*\.',
            r'With[^.]*experience[^.]*\.[^.]*\.',  # Experience descriptions
            r'[A-Za-z][^.]{50,}medical[^.]*\.[^.]*\.',  # Medical related descriptions
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                description = match.group(0).strip()
                if len(description) > 50:  # Only meaningful descriptions
                    break
        
        # If no specific pattern found, look for the longest sentence as description
        if not description:
            sentences = re.split(r'[.!?]+', content)
            longest_sentence = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > len(longest_sentence) and len(sentence) > 50 and 
                    not any(noise in sentence.lower() for noise in ['specialty', 'degrees', 'appointment', 'clinic'])):
                    longest_sentence = sentence
            
            if longest_sentence:
                description = longest_sentence
        
        doctor_info['description'] = description
        
        return doctor_info

    def extract_department_info(self, content, response):
        """Extract comprehensive department information"""
        department_info = {
            'name': None,
            'description': None,
            'services': [],
            'procedures': [],
            'doctors': [],
            'faqs': [],
            'contact_info': {},
            'specialties': [],
            'facilities': []
        }
        
        # Extract department name from title or URL
        title = response.css('title::text').get() or ""
        url = response.url
        
        # Extract from title
        if 'department' in title.lower() or any(dept in title.lower() for dept in ['medicine', 'surgery', 'cardiology', 'neurology', 'fetal', 'gynecology', 'ophthalmology']):
            dept_match = re.search(r'([A-Za-z\s&]+?)(?:\s*-\s*Hameed Latif Hospital|$)', title)
            if dept_match:
                department_info['name'] = dept_match.group(1).strip()
        
        # Extract from URL if title extraction failed
        if not department_info['name'] and '/departments/' in url:
            url_parts = url.rstrip('/').split('/')
            if url_parts:
                dept_slug = url_parts[-1]
                dept_name = dept_slug.replace('-', ' ').title()
                department_info['name'] = dept_name
        
        # Extract department description - COMPREHENSIVE PATTERNS
        description = None
        
        # Pattern 1: "At Hameed Latif Hospital, our Department of..."
        desc_pattern1 = re.search(r'At Hameed Latif Hospital[^.]*Department[^.]*\.([^.]+(?:\.[^.]+){2,10})', content, re.IGNORECASE | re.DOTALL)
        if desc_pattern1:
            description = desc_pattern1.group(0).strip()
        
        # Pattern 2: "Department of [Name] offers..."
        elif 'Department of' in content:
            desc_pattern2 = re.search(r'Department of [^.]*\.([^.]+(?:\.[^.]+){2,10})', content, re.IGNORECASE | re.DOTALL)
            if desc_pattern2:
                description = desc_pattern2.group(0).strip()
        
        # Pattern 3: Look for the first substantial paragraph
        else:
            sentences = re.split(r'[.!?]+', content)
            paragraph = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 50 and 
                    not any(noise in sentence.lower() for noise in ['specialty', 'degrees', 'appointment', 'clinic', 'home', 'contact'])):
                    paragraph += sentence + ". "
                    if len(paragraph) > 200:  # Good paragraph length
                        description = paragraph.strip()
                        break
        
        department_info['description'] = description
        
        # Extract services - MULTIPLE COMPREHENSIVE PATTERNS
        services = []
        
        # Pattern 1: "Our primary services include:" or "services include:"
        service_patterns = [
            r'(?:primary\s+)?services\s+include[^:]*:([^.]+(?:\.[^.]+)*)',
            r'We offer[^:]*:([^.]+(?:\.[^.]+)*)',
            r'Services[^:]*:([^.]+(?:\.[^.]+)*)',
            r'The following services[^:]*:([^.]+(?:\.[^.]+)*)',
            r'Our services[^:]*:([^.]+(?:\.[^.]+)*)'
        ]
        
        for pattern in service_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                services_text = match.group(1).strip()
                # Split by various separators
                service_items = re.split(r'[,;\n•\-\*]+', services_text)
                for service in service_items:
                    service = service.strip()
                    if service and len(service) > 3 and len(service) < 300:
                        services.append(service)
                break
        
        # Pattern 2: Look for bulleted or listed services
        if not services:
            # Look for patterns like "• Service name" or "- Service name"
            bullet_services = re.findall(r'[•\-\*]\s*([A-Za-z][^•\-\*\n]{5,100})', content)
            for service in bullet_services:
                service = service.strip()
                if len(service) > 5:
                    services.append(service)
        
        # Pattern 3: Extract from "Services:" sections
        if not services:
            services_section = re.search(r'Services:\s*([^A-Z]*?)(?:Doctors|FAQ|Contact|©|$)', content, re.IGNORECASE | re.DOTALL)
            if services_section:
                services_text = services_section.group(1).strip()
                service_lines = re.split(r'\n+', services_text)
                for line in service_lines:
                    line = line.strip()
                    if line and len(line) > 5 and len(line) < 200:
                        services.append(line)
        
        department_info['services'] = services[:20]  # Limit to 20 services
        
        # Extract procedures - COMPREHENSIVE EXTRACTION
        procedures = []
        
        # Look for procedure-related keywords
        proc_keywords = ['procedure', 'treatment', 'surgery', 'scan', 'test', 'screening', 'therapy', 'examination', 'biopsy', 'ultrasound']
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 15 and len(sentence) < 300 and 
                any(keyword in sentence.lower() for keyword in proc_keywords)):
                procedures.append(sentence)
                if len(procedures) >= 15:  # Limit to avoid too much data
                    break
        
        department_info['procedures'] = procedures
        
        # Extract FAQs - COMPREHENSIVE FAQ EXTRACTION
        faqs = []
        
        # Pattern 1: Numbered FAQs like "1- Is therapy good for pregnancy?"
        faq_pattern1 = re.findall(r'(\d+[-.]?\s*[^?]+\?[^?]*(?:\?[^?]*)*)', content)
        for faq in faq_pattern1:
            if len(faq) > 20:
                faqs.append(faq.strip())
        
        # Pattern 2: Q&A format
        faq_pattern2 = re.findall(r'(Q[^?]+\?[^Q]*)', content, re.IGNORECASE)
        for faq in faq_pattern2:
            if len(faq) > 20:
                faqs.append(faq.strip())
        
        # Pattern 3: Questions starting with common question words
        question_starters = ['What', 'How', 'When', 'Where', 'Why', 'Who', 'Which', 'Is', 'Are', 'Can', 'Do', 'Does']
        for starter in question_starters:
            pattern = rf'({starter}\s[^?]+\?[^?]*)'
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 20 and match not in faqs:
                    faqs.append(match.strip())
        
        department_info['faqs'] = faqs[:15]  # Limit to 15 FAQs
        
        # Extract doctors from department content
        doctors = []
        
        # Look for doctor names in the content
        doctor_patterns = [
            r'Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'Prof\.\s+Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'Professor\s+Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        ]
        
        for pattern in doctor_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                doctor_name = f"Dr. {match}"
                if doctor_name not in doctors:
                    doctors.append(doctor_name)
        
        department_info['doctors'] = doctors[:10]  # Limit to 10 doctors
        
        # Extract specialties and facilities
        specialties = []
        facilities = []
        
        # Look for specialty-related content
        specialty_keywords = ['specialty', 'specialization', 'specialized', 'expert', 'expertise']
        facility_keywords = ['facility', 'equipment', 'technology', 'unit', 'center', 'laboratory']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 20 and len(sentence) < 200):
                if any(keyword in sentence.lower() for keyword in specialty_keywords):
                    specialties.append(sentence)
                elif any(keyword in sentence.lower() for keyword in facility_keywords):
                    facilities.append(sentence)
        
        department_info['specialties'] = specialties[:10]
        department_info['facilities'] = facilities[:10]
        
        return department_info

    def determine_page_type(self, url):
        """Determine page type for better content extraction"""
        url_lower = url.lower()
        if "/doctors/" in url and not url.endswith("/doctors") and not url.endswith("/doctors/"):
            return "doctor_profile"
        elif "/doctors" in url:
            return "doctors_list"
        elif "/departments/" in url and not url.endswith("/departments") and not url.endswith("/departments/"):
            return "department_page"
        elif "/departments" in url:
            return "departments_list"
        elif "contact" in url_lower:
            return "contact_page"
        elif "news" in url_lower or "events" in url_lower:
            return "news_events"
        elif "faq" in url_lower:
            return "faq_page"
        elif "about" in url_lower:
            return "about_page"
        elif "visitor" in url_lower:
            return "visitor_info"
        else:
            return "general_page"

    def parse(self, response):
        # Skip if already visited
        if response.url in self.visited_urls:
            return
        self.visited_urls.add(response.url)
        
        # Only process HTML responses
        content_type = response.headers.get('content-type', b'').decode('utf-8').lower()
        if 'text/html' not in content_type:
            return
        
        self.logger.info(f"Processing: {response.url}")
        
        # Extract clean content
        main_content = self.extract_clean_content(response)
        
        if not main_content or len(main_content) < 30:
            return  # Skip pages with no meaningful content
        
        # Initialize item
        item = HameedlatifItem()
        item['url'] = response.url
        item['title'] = self.clean_text(response.css("title::text").get() or "")
        item['page_type'] = self.determine_page_type(response.url)
        item['main_content'] = main_content
        item['scraped_at'] = datetime.now().isoformat()
        item['word_count'] = len(main_content.split())
        
        # Initialize all fields
        item['departments'] = []
        item['doctors'] = []
        item['doctor_qualifications'] = []
        item['phone_numbers'] = []
        item['email_addresses'] = []
        item['addresses'] = []
        item['services'] = []
        item['procedures'] = []
        item['faqs'] = []
        item['visitor_info'] = []
        item['news_events'] = []
        item['appointment_info'] = []
        item['specialties'] = []
        item['facilities'] = []
        item['descriptions'] = []
        
        # Extract information based on page type
        if item['page_type'] == 'doctor_profile':
            # Extract individual doctor information
            doctor_info = self.extract_doctor_info(main_content, response.url)
            if doctor_info and doctor_info['name']:
                item['doctors'] = [doctor_info['name']]
                item['doctor_qualifications'] = doctor_info['qualifications']
                if doctor_info['appointment_number']:
                    item['appointment_info'] = [f"Appointment: {doctor_info['appointment_number']}"]
                if doctor_info['specialization']:
                    item['specialties'] = [doctor_info['specialization']]
                if doctor_info['description']:
                    item['descriptions'] = [doctor_info['description']]
                # Store complete doctor info in a custom field
                item['doctor_profile'] = doctor_info
        
        elif item['page_type'] == 'department_page':
            # Extract comprehensive department information
            dept_info = self.extract_department_info(main_content, response)
            if dept_info['name']:
                item['departments'] = [dept_info['name']]
                item['services'] = dept_info['services']
                item['procedures'] = dept_info['procedures']
                item['faqs'] = dept_info['faqs']
                item['doctors'] = dept_info['doctors']
                item['specialties'] = dept_info['specialties']
                item['facilities'] = dept_info['facilities']
                if dept_info['description']:
                    item['descriptions'] = [dept_info['description']]
                # Store complete department info
                item['department_info'] = dept_info
        
        elif item['page_type'] == 'doctors_list' or item['page_type'] == 'departments_list':
            # Extract multiple doctors or departments from list pages
            # Extract all doctor names from content
            doctor_patterns = [
                r'Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                r'Prof\.\s+Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                r'Professor\s+Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
            ]
            
            doctors = []
            for pattern in doctor_patterns:
                matches = re.findall(pattern, main_content)
                for match in matches:
                    doctor_name = f"Dr. {match}"
                    if doctor_name not in doctors:
                        doctors.append(doctor_name)
            
            item['doctors'] = doctors[:50]  # Limit to 50 doctors
            
            # Extract department names
            dept_keywords = [
                'Cardiology', 'Neurology', 'Orthopedic', 'Gynecology', 'Urology', 
                'Dermatology', 'Psychiatry', 'Radiology', 'Gastroenterology', 
                'Nephrology', 'Oncology', 'Pediatrics', 'Surgery', 'Medicine',
                'Fetal Medicine', 'Ophthalmology', 'Anesthesia', 'Emergency'
            ]
            
            departments = []
            for dept in dept_keywords:
                if dept.lower() in main_content.lower():
                    departments.append(dept)
            
            item['departments'] = departments
        
        # Extract contact information from all pages
        phone_patterns = [
            r'\+92[\s\-]?\(?\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}',
            r'0\d{2}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}',
            r'\d{4}[\s\-]?\d{7}',
            r'\b(03[0-9]{9})\b'  # Pakistani mobile numbers
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, main_content)
            item['phone_numbers'].extend([match.strip() for match in matches if match.strip()])
        
        # Remove duplicates and clean phone numbers
        item['phone_numbers'] = list(set(item['phone_numbers']))[:10]
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        item['email_addresses'] = list(set(re.findall(email_pattern, main_content)))
        
        # Extract addresses
        address_patterns = [
            r'\d+[^,\n]*(?:Block|Road|Street|Avenue|Lane)[^,\n]*',
            r'[^,\n]*Lahore[^,\n]*',
            r'[^,\n]*Garden Town[^,\n]*'
        ]
        
        addresses = []
        for pattern in address_patterns:
            matches = re.findall(pattern, main_content, re.IGNORECASE)
            addresses.extend([match.strip() for match in matches])
        
        item['addresses'] = list(set(addresses))[:5]
        
        # Extract general services and procedures if not already done
        if not item['services']:
            service_keywords = ['service', 'treatment', 'care', 'consultation', 'therapy']
            sentences = re.split(r'[.!?]+', main_content)
            services = []
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 15 and len(sentence) < 200 and 
                    any(keyword in sentence.lower() for keyword in service_keywords)):
                    services.append(sentence)
                    if len(services) >= 10:
                        break
            item['services'] = services
        
        # Extract FAQs if not already done
        if not item['faqs']:
            faq_patterns = [
                r'(\d+[-.]?\s*[^?]+\?[^?]*)',
                r'([A-Z][^?]{10,}\?[^?]*)'
            ]
            
            faqs = []
            for pattern in faq_patterns:
                matches = re.findall(pattern, main_content)
                for match in matches:
                    if len(match) > 20 and '?' in match:
                        faqs.append(match.strip())
            item['faqs'] = faqs[:10]
        
        # Extract visitor information
        visitor_keywords = ['visitor', 'visiting', 'hours', 'timing', 'appointment', 'admission', 'emergency']
        sentences = re.split(r'[.!?]+', main_content)
        visitor_info = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 20 and len(sentence) < 200 and 
                any(keyword in sentence.lower() for keyword in visitor_keywords)):
                visitor_info.append(sentence)
                if len(visitor_info) >= 5:
                    break
        
        item['visitor_info'] = visitor_info
        
        yield item

        # Follow internal links
        try:
            for link in response.css("a::attr(href)").getall():
                if not link or link.startswith(("mailto:", "tel:", "javascript:", "#", "data:")):
                    continue

                # Convert to absolute URL
                absolute_url = urljoin(response.url, link)

                # Skip if already visited
                if absolute_url in self.visited_urls:
                    continue

                # Only follow links within the domain and avoid images/uploads
                if ("hameedlatifhospital.com" in absolute_url and 
                    not any(pattern in absolute_url.lower() for pattern in [
                        '/wp-content/uploads/',  # WordPress uploads folder
                        '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',  # Image files
                        '.css', '.js', '.ico', '.xml', '.txt',  # Other files
                        '/wp-admin/', '/wp-includes/',  # WordPress admin
                        '?attachment_id=', 'wp-json',  # WordPress API/attachments
                        '/feed/', '/rss/', '/sitemap'  # Feeds and sitemaps
                    ])):
                    yield response.follow(absolute_url, callback=self.parse)
        except Exception as e:
            self.logger.error(f"Error following links from {response.url}: {e}")
