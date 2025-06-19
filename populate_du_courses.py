import os
import environ
from supabase import create_client, Client
from collections import Counter

# Load environment variables
env = environ.Env()
environ.Env.read_env()
SUPABASE_URL = env('SUPABASE_URL')
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNkZW9wb3RucHV1cGlzd3h1Z2xjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDM0NTExMCwiZXhwIjoyMDY1OTIxMTEwfQ.sX0jfSRULcVEp7xJxScPi5v1oW8ad1gDRl-FiFMH-IA'

# Debug environment variables
print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY (first 10 chars): {SUPABASE_KEY[:10]}...")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client initialized successfully")
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    exit(1)

# List A and List B subjects
LIST_A = [
    'English', 'Hindi', 'Assamese', 'Bengali', 'Gujarati', 'Kannada', 'Malayalam',
    'Marathi', 'Odia', 'Punjabi', 'Tamil', 'Telugu', 'Urdu', 'Sanskrit'
]
LIST_B = [
    'Accountancy / Book Keeping', 'Agriculture', 'Anthropology',
    'Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Business Studies',
    'Chemistry', 'Environmental Science', 'Computer Science / Information Practices',
    'Economics / Business Economics', 'Fine Arts/Visual Arts/Commercial Arts',
    'Geography / Geology', 'History', 'Home Science',
    'Knowledge Tradition-Practices in India', 'Mass Media / Mass Communication',
    'Mathematics / Applied Mathematics', 'Performing Arts - (Dance, Drama and Music)',
    'Physical Education (Yoga, Sports)', 'Physics', 'Political Science',
    'Psychology', 'Sociology'
]

# Add pseudo-subjects for tests (use 'B' to avoid constraint violation)
PSEUDO_SUBJECTS = [
    {'subject_name': 'General Aptitude Test', 'list_type': 'TEST', 'is_specific': False},
    {'subject_name': 'Performance-Based Test', 'list_type': 'TEST', 'is_specific': False},
    {'subject_name': 'Practical-Based Test', 'list_type': 'TEST', 'is_specific': False},
]

# COURSES list (performance_test_weight uses None, not "None")
COURSES = [
    # Language-based Honours
    ('B.A. (Hons.) English', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': ['English'], 'additional': {'count': 3, 'from': 'LIST_B'}}, 'description': 'English from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': ['English'], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'English and one Language from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    ('B.A. (Hons.) Hindi', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': ['Hindi'], 'additional': {'count': 3, 'from': 'LIST_B'}}, 'description': 'Hindi from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': ['Hindi'], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Hindi and one Language from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    ('B.A. (Hons.) Bengali', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': ['Bengali'], 'additional': {'count': 3, 'from': 'LIST_B'}}, 'description': 'Bengali from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': ['Bengali'], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Bengali and one Language from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'language_and_domain', 'priority': 3, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': 'Considered only if seats remain vacant after I & II'},
        {'type': 'dual_language_and_domain', 'priority': 4, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': 'Considered only if seats remain vacant after I & II'}
    ]),
    # Science-based Honours
    ('B.Sc. (Hons.) Physics', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Chemistry', 'Mathematics / Applied Mathematics'], 'additional': {}}, 'description': 'Physics + Chemistry + Mathematics/Applied Mathematics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'fixed', 'priority': 2, 'required_subjects': {'mandatory': ['Physics', 'Chemistry', 'Computer Science / Information Practices'], 'additional': {}}, 'description': 'Physics + Chemistry + Computer Science/Informatics Practices', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    ('B.Sc. (Hons.) Chemistry', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Chemistry', 'Physics', 'Biology/ Biological Studies/ Biotechnology /Biochemistry'], 'additional': {}}, 'description': 'Chemistry + Physics + Biology/Biological Studies/Biotechnology/Biochemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'fixed', 'priority': 2, 'required_subjects': {'mandatory': ['Chemistry', 'Physics', 'Mathematics / Applied Mathematics'], 'additional': {}}, 'description': 'Chemistry + Physics + Mathematics/Applied Mathematics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # Commerce
    ('B.Com. (Hons.)', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': ['Mathematics / Applied Mathematics'], 'other_count': 2, 'from_other': 'LIST_B'}}, 'description': 'Any one Language from List A + Mathematics/Applied Mathematics + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': ['Accountancy / Book Keeping'], 'other_count': 2, 'from_other': 'LIST_B'}}, 'description': 'Any one Language from List A + Accountancy/Book Keeping + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # Performance-based
    ('B.A. (Hons.) in Music: Vocal/Instrumental Sitar/ Sarod/ Guitar/ Violin/ Santoor', True, 0.5, [
        {'type': 'performance', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': ['Performing Arts - (Dance, Drama and Music)'], 'other_count': 2, 'from_other': 'LIST_B'}}, 'description': 'Any one Language from List A + Performing Arts from List B + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'},
        {'type': 'performance', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': ['Performing Arts - (Dance, Drama and Music)'], 'other_count': 1, 'from_other': 'LIST_B'}}, 'description': 'Any two Languages from List A + Performing Arts from List B + Any one subject from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'},
        {'type': 'performance', 'priority': 3, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'},
        {'type': 'performance', 'priority': 4, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'}
    ]),
    # B.A. (Hons.) Economics
    ('B.A. (Hons.) Economics', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.A. (Hons.) Journalism
    ('B.A. (Hons.) Journalism', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.A. (Hons.) Psychology
    ('B.A. (Hons.) Psychology', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.A. (Hons.) Social Work
    ('B.A. (Hons.) Social Work', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.A. (Hons.) Philosophy
    ('B.A. (Hons.) Philosophy', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.A. (Hons.) Multi Media and Mass Communication (with aptitude test)
    ('B.A. (Hons.) Multi Media and Mass Communication', False, None, [
        {'type': 'language_and_aptitude', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': ['Mass Media / Mass Communication'], 'other_count': 0, 'from_other': []}}, 'description': 'Any one Language from List A + Mass Media/Mass Communication from List B + Section III of CUET (General Aptitude Test)', 'requires_aptitude_test': True, 'requires_performance_test': False, 'proration_note': 'Proration applies'},
        {'type': 'language_and_aptitude', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 0, 'from_domain': [], 'other_count': 0, 'from_other': []}}, 'description': 'Any one Language from List A + Section III of CUET (General Aptitude Test)', 'requires_aptitude_test': True, 'requires_performance_test': False, 'proration_note': 'Proration applies'}
    ]),
    # B.A. (Hons.) in Music: Hindustani Music (Performance-based)
    ('B.A. (Hons.) in Music: Hindustani Music', True, 0.5, [
        {'type': 'performance', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': ['Performing Arts - (Dance, Drama and Music)'], 'other_count': 2, 'from_other': 'LIST_B'}}, 'description': 'Any one Language from List A + Performing Arts from List B + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'},
        {'type': 'performance', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': ['Performing Arts - (Dance, Drama and Music)'], 'other_count': 1, 'from_other': 'LIST_B'}}, 'description': 'Any two Languages from List A + Performing Arts from List B + Any one subject from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'},
        {'type': 'performance', 'priority': 3, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'},
        {'type': 'performance', 'priority': 4, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'}
    ]),
    # B.A. (Hons.) Applied Psychology
    ('B.A. (Hons.) Applied Psychology', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.A. (Hons.) Business Economics (BBE) (with aptitude test)
    ('B.A. (Hons.) Business Economics (BBE)', False, None, [
        {'type': 'language_and_aptitude', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': 'LIST_B', 'other_count': 1, 'from_other': 'LIST_B'}}, 'description': 'Any one Language from List A + Any one subject from List B + SECTION III of CUET (General Aptitude Test)', 'requires_aptitude_test': True, 'requires_performance_test': False, 'proration_note': 'Proration applies'}
    ]),
    # B.Voc. Banking Operations (Vocational)
    ('B.Voc. Banking Operations', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'language_and_aptitude', 'priority': 3, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': 'LIST_B', 'other_count': 1, 'from_other': 'LIST_B'}}, 'description': 'Any one Language from List A + Any one subject from List B + SECTION III of CUET (General Aptitude Test)', 'requires_aptitude_test': True, 'requires_performance_test': False, 'proration_note': 'Proration applies'}
    ]),
    # B.Sc. (Hons.) Botany (Science, fixed)
    ('B.Sc. (Hons.) Botany', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Chemistry', 'Physics'], 'additional': {}}, 'description': 'Biology/Biological Studies/Biotechnology/Biochemistry + Chemistry + Physics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Zoology (Science, fixed)
    ('B.Sc. (Hons.) Zoology', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Chemistry', 'Physics'], 'additional': {}}, 'description': 'Biology/Biological Studies/Biotechnology/Biochemistry + Chemistry + Physics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Computer Science (Science, fixed)
    ('B.Sc. (Hons.) Computer Science', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Mathematics / Applied Mathematics', 'Any one Language from List A', 'Any two subjects from List B'], 'additional': {}}, 'description': 'Any one Language from List A + Mathematics/Applied Mathematics + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # Bachelor of Fine Arts (Practical-based)
    ('Bachelor of Fine Arts', True, 0.5, [
        {'type': 'practical', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'aptitude_test': True}}, 'description': 'Any one Language from List A + General Aptitude Test (Section III) + Practical-Based Test', 'requires_aptitude_test': True, 'requires_performance_test': False, 'requires_practical_test': True, 'proration_note': 'CUET score (50%) + Practical-based test (50%)'}
    ]),
    # B.Sc. (Hons.) Mathematics
    ('B.Sc. (Hons.) Mathematics', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': ['Mathematics / Applied Mathematics'], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Mathematics/Applied Mathematics + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': ['Mathematics / Applied Mathematics'], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Mathematics/Applied Mathematics + Any one subject from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Statistics
    ('B.Sc. (Hons.) Statistics', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': ['Mathematics / Applied Mathematics'], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Mathematics/Applied Mathematics + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'dual_language_and_domain', 'priority': 2, 'required_subjects': {'mandatory': ['Mathematics / Applied Mathematics'], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Mathematics/Applied Mathematics + Any one subject from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Electronics
    ('B.Sc. (Hons.) Electronics', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Chemistry'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Chemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'fixed', 'priority': 2, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Computer Science / Information Practices'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Computer Science/Informatics Practices', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Food Technology
    ('B.Sc. (Hons.) Food Technology', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Chemistry', 'Physics'], 'additional': {}}, 'description': 'Biology/Biological Studies/Biotechnology/Biochemistry + Chemistry + Physics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'fixed', 'priority': 2, 'required_subjects': {'mandatory': ['Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Chemistry', 'Mathematics / Applied Mathematics'], 'additional': {}}, 'description': 'Biology/Biological Studies/Biotechnology/Biochemistry + Chemistry + Mathematics/Applied Mathematics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Home Science
    ('B.Sc. (Hons.) Home Science', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Microbiology
    ('B.Sc. (Hons.) Microbiology', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Chemistry', 'Physics'], 'additional': {}}, 'description': 'Biology/Biological Studies/Biotechnology/Biochemistry + Chemistry + Physics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Polymer Science
    ('B.Sc. (Hons.) Polymer Science', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Chemistry', 'Mathematics / Applied Mathematics'], 'additional': {}}, 'description': 'Physics + Chemistry + Mathematics/Applied Mathematics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Instrumentation
    ('B.Sc. (Hons.) Instrumentation', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Chemistry'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Chemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'fixed', 'priority': 2, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Computer Science / Information Practices'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Computer Science/Informatics Practices', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Environmental Science
    ('B.Sc. (Hons.) Environmental Science', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Chemistry', 'Physics'], 'additional': {}}, 'description': 'Biology/Biological Studies/Biotechnology/Biochemistry + Chemistry + Physics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Biomedical Science
    ('B.Sc. (Hons.) Biomedical Science', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Chemistry', 'Biology/ Biological Studies/ Biotechnology /Biochemistry'], 'additional': {}}, 'description': 'Physics + Chemistry + Biology/Biological Studies/Biotechnology/Biochemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Geology
    ('B.Sc. (Hons.) Geology', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Chemistry', 'Mathematics / Applied Mathematics'], 'additional': {}}, 'description': 'Physics + Chemistry + Mathematics/Applied Mathematics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'fixed', 'priority': 2, 'required_subjects': {'mandatory': ['Physics', 'Chemistry', 'Geography / Geology'], 'additional': {}}, 'description': 'Physics + Chemistry + Geography/Geology', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'fixed', 'priority': 3, 'required_subjects': {'mandatory': ['Physics', 'Chemistry', 'Biology/ Biological Studies/ Biotechnology /Biochemistry'], 'additional': {}}, 'description': 'Physics + Chemistry + Biology/Biological Studies/Biotechnology/Biochemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Anthropology
    ('B.Sc. (Hons.) Anthropology', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Chemistry', 'Physics'], 'additional': {}}, 'description': 'Biology/Biological Studies/Biotechnology/Biochemistry + Chemistry + Physics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Hons.) Biochemistry
    ('B.Sc. (Hons.) Biochemistry', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Chemistry', 'Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Physics'], 'additional': {}}, 'description': 'Chemistry + Biology/Biological Studies/Biotechnology/Biochemistry + Physics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'fixed', 'priority': 2, 'required_subjects': {'mandatory': ['Chemistry', 'Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Mathematics / Applied Mathematics'], 'additional': {}}, 'description': 'Chemistry + Biology/Biological Studies/Biotechnology/Biochemistry + Mathematics/Applied Mathematics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Prog.) Life Science
    ('B.Sc. (Prog.) Life Science', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Chemistry', 'Biology/ Biological Studies/ Biotechnology /Biochemistry'], 'additional': {}}, 'description': 'Physics + Chemistry + Biology/Biological Studies/Biotechnology/Biochemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Prog.) Physical Science with Chemistry
    ('B.Sc. (Prog.) Physical Science with Chemistry', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Chemistry'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Chemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Prog.) Physical Science with Electronics
    ('B.Sc. (Prog.) Physical Science with Electronics', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Chemistry'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Chemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'fixed', 'priority': 2, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Computer Science / Information Practices'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Computer Science/Informatics Practices', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Prog.) Physical Science with Computer Science/Informatics Practices
    ('B.Sc. (Prog.) Physical Science with Computer Science/Informatics Practices', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Chemistry'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Chemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''},
        {'type': 'fixed', 'priority': 2, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Computer Science / Information Practices'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Computer Science/Informatics Practices', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Prog.) Applied Life Science
    ('B.Sc. (Prog.) Applied Life Science', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Biology/ Biological Studies/ Biotechnology /Biochemistry', 'Chemistry', 'Physics'], 'additional': {}}, 'description': 'Biology/Biological Studies/Biotechnology/Biochemistry + Chemistry + Physics', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Prog.) Applied Physical Sciences with Analytical Methods in Chemistry & Biochemistry
    ('B.Sc. (Prog.) Applied Physical Sciences with Analytical Methods in Chemistry & Biochemistry', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Chemistry'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Chemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Prog.) Applied Physical Sciences with Industrial Chemistry
    ('B.Sc. (Prog.) Applied Physical Sciences with Industrial Chemistry', False, None, [
        {'type': 'fixed', 'priority': 1, 'required_subjects': {'mandatory': ['Physics', 'Mathematics / Applied Mathematics', 'Chemistry'], 'additional': {}}, 'description': 'Physics + Mathematics/Applied Mathematics + Chemistry', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. (Pass) Home Science
    ('B.Sc. (Pass) Home Science', False, None, [
        {'type': 'language_and_domain', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': False, 'proration_note': ''}
    ]),
    # B.Sc. Physical Education, Health Education and Sports (PE, HE & S) (Performance-based)
    ('B.Sc. Physical Education, Health Education and Sports (PE, HE & S)', True, 0.5, [
        {'type': 'performance', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': ['Physical Education (Yoga, Sports)'], 'other_count': 2, 'from_other': 'LIST_B'}}, 'description': 'Any one Language from List A + Physical Education from List B + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'},
        {'type': 'performance', 'priority': 2, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': ['Physical Education (Yoga, Sports)'], 'other_count': 1, 'from_other': 'LIST_B'}}, 'description': 'Any two Languages from List A + Physical Education from List B + Any one subject from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'},
        {'type': 'performance', 'priority': 3, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 3, 'from_domain': 'LIST_B'}}, 'description': 'Any one Language from List A + Any three subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'},
        {'type': 'performance', 'priority': 4, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 2, 'from_language': 'LIST_A', 'domain_count': 2, 'from_domain': 'LIST_B'}}, 'description': 'Any two Languages from List A + Any two subjects from List B', 'requires_aptitude_test': False, 'requires_performance_test': True, 'proration_note': 'CUET score (50%) + Performance-based test (50%)'}
    ]),
    # Bachelor of Management Studies (BMS) (with aptitude test)
    ('Bachelor of Management Studies (BMS)', False, None, [
        {'type': 'language_and_aptitude', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'domain_count': 1, 'from_domain': 'LIST_B', 'other_count': 1, 'from_other': 'LIST_B'}}, 'description': 'Any one Language from List A + Any one subject from List B + SECTION III of CUET (General Aptitude Test)', 'requires_aptitude_test': True, 'requires_performance_test': False, 'proration_note': 'Proration applies'}
    ]),
    # Bachelor of Elementary Education
    ('Bachelor of Elementary Education', False, None, [
        {'type': 'language_and_aptitude', 'priority': 1, 'required_subjects': {'mandatory': [], 'additional': {'language_count': 1, 'from_language': 'LIST_A', 'aptitude_test': True}}, 'description': 'Any one Language from List A + General Aptitude Test (Section III)', 'requires_aptitude_test': True, 'requires_performance_test': False, 'proration_note': ''}
    ]),
]

# Debug: Check for duplicate course names
course_names = [course_name for course_name, _, _, _ in COURSES]
duplicates = {name: count for name, count in Counter(course_names).items() if count > 1}
if duplicates:
    print("Duplicate course names found:", duplicates)
    exit(1)
else:
    print("No duplicate course names found")

# Debug: Validate combination types
valid_combination_types = ['language_and_domain', 'dual_language_and_domain', 'performance', 'language_and_aptitude', 'practical', 'fixed']
combo_types = set()
for _, _, _, combos in COURSES:
    for combo in combos:
        combo_types.add(combo['type'])
invalid_types = combo_types - set(valid_combination_types)
if invalid_types:
    print("Invalid combination types found:", invalid_types)
    exit(1)
else:
    print("All combination types are valid:", combo_types)

# Insert subjects
for subject in LIST_A:
    try:
        supabase.table('subjects').upsert({
            'subject_name': subject,
            'list_type': 'A',
            'is_specific': True
        }, on_conflict=['subject_name']).execute()
        print(f"Inserted/Updated subject: {subject}")
    except Exception as e:
        print(f"Error inserting subject: {subject}: {e}")

for subject in LIST_B:
    try:
        supabase.table('subjects').upsert({
            'subject_name': subject,
            'list_type': 'B',
            'is_specific': True
        }, on_conflict=['subject_name']).execute()
        print(f"Inserted/Updated subject: {subject}")
    except Exception as e:
        print(f"Error inserting subject: {subject}: {e}")

for subject in PSEUDO_SUBJECTS:
    try:
        supabase.table('subjects').upsert(subject, on_conflict=['subject_name']).execute()
        print(f"Inserted/Updated subject: {subject['subject_name']}")
    except Exception as e:
        print(f"Error inserting subject: {subject['subject_name']}: {e}")

# Insert courses and get their IDs
def get_course_id(name):
    try:
        res = supabase.table('courses').select('course_id').eq('course_name', name).execute()
        if res.data:
            return res.data[0]['course_id']
        return None
    except Exception as e:
        print(f"Error fetching course_id for {name}: {e}")
        return None

for course_name, has_perf, perf_weight, combos in COURSES:
    try:
        supabase.table('courses').upsert({
            'course_name': course_name,
            'has_performance_test': has_perf,
            'performance_test_weight': perf_weight
        }, on_conflict=['course_name']).execute()
        print(f"Inserted/Updated course: {course_name}")
    except Exception as e:
        print(f"Error inserting course: {course_name}: {e}")

# Insert combinations for each course
for course_name, _, _, combos in COURSES:
    course_id = get_course_id(course_name)
    if not course_id:
        print(f"Course not found: {course_name}")
        continue
    for combo in combos:
        try:
            supabase.table('course_combinations').upsert({
                'course_id': course_id,
                'combination_type': combo['type'],
                'priority': combo['priority'],
                'required_subjects': combo['required_subjects'],
                'description': combo['description']
            }, on_conflict=['combination_id', 'priority']).execute()
            print(f"Inserted/Updated combination for {course_name}: {combo['description']}")
        except Exception as e:
            print(f"Error inserting combination for {course_name}: {e}")

print("All subjects, courses, and combinations inserted!")