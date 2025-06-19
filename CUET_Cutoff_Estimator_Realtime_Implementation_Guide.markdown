# CUET Cutoff Estimator Realtime Implementation Guide

This guide outlines how to build a web application for estimating Delhi University (DU) CUET cutoffs using Python Django and Supabase, with real-time functionality for instant ranking updates. The platform allows students to submit their CUET scores anonymously, select their category and preferred courses, and view estimated rankings with filters for course and category, all presented in a modern blurred glass UI.

## 1. Project Overview

### Purpose
The application helps DU students estimate potential CUET cutoffs by crowdsourcing score data in real-time. It calculates merit scores based on program-specific CUET subject combinations (refer to [DU_CUET_Subject_Combinations_2025.md](artifact ID: `54425bbb-e776-4eb0-9107-4d2521225d8e`)) and provides a user-friendly interface with live ranking updates.

### Key Features
- **Submission Form**: Students select their category (General, EWS, OBC, SC, ST, Single Girl Child), choose DU courses, and input CUET scores.
- **Anonymous Data Storage**: Submissions are stored with a unique ID, ensuring no personal data is collected.
- **Real-Time Ranking**: Merit scores are computed based on DU’s course requirements, with rankings updated instantly as new submissions arrive.
- **Modern UI**: A blurred glass effect is implemented using CSS for a sleek, responsive design.
- **Data Privacy**: Only a unique ID is stored, with a disclaimer that rankings are estimates.
- **Filters**: Rankings can be filtered by course, category, or both, with live updates.

## 2. Technology Stack

### Django
Django handles backend logic, views, and templates. It integrates with Supabase for data operations and serves the frontend.

### Supabase
Supabase, a PostgreSQL-based backend-as-a-service, supports real-time subscriptions via WebSockets. The `supabase-py` client manages database operations, and the JavaScript client (`@supabase/supabase-js`) enables real-time updates in the browser.

### Frontend
Django templates with HTML, CSS, and JavaScript. CSS implements the blurred glass effect, and JavaScript (with Supabase’s JS client) handles real-time ranking updates.

## 3. Database Schema

Supabase’s PostgreSQL database stores the following tables:

| Table       | Columns                                                                 | Description                                                                 |
|-------------|-------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| submissions | `unique_id` (TEXT, PK), `category` (TEXT), `courses` (TEXT[]), `scores` (JSONB), `created_at` (TIMESTAMP) | Stores anonymous submissions with a unique ID, category, courses, scores, and timestamp. |
| courses     | `course_id` (SERIAL, PK), `course_name` (TEXT), `required_subjects` (TEXT[]) | Lists DU undergraduate programs with required CUET subjects. |

### Real-Time Configuration
- Enable real-time on the `submissions` table in Supabase’s dashboard or via SQL:
  ```sql
  ALTER PUBLICATION supabase_realtime ADD TABLE submissions;
  ```
- Use Row Level Security (RLS) to restrict access:
  ```sql
  ENABLE RLS ON submissions;
  CREATE POLICY "Read-only submissions" ON submissions FOR SELECT USING (true);
  CREATE POLICY "Insert submissions" ON submissions FOR INSERT WITH CHECK (true);
  ```

### Example Data
- **submissions**:
  ```json
  {
    "unique_id": "550e8400-e29b-41d4-a716-446655440000",
    "category": "General",
    "courses": ["B.A. (Hons) English", "B.Com (Hons)"],
    "scores": {"English": 180, "General Test": 190, "Mathematics": 170},
    "created_at": "2025-06-19T19:58:00Z"
  }
  ```
- **courses**:
  ```json
  {
    "course_id": 1,
    "course_name": "B.A. (Hons) English",
    "required_subjects": ["English", "General Test"]
  }
  ```

Populate `courses` with DU programs using data from [DU_CUET_Subject_Combinations_2025.md](artifact ID: `54425bbb-e776-4eb0-9107-4d2521225d8e`):
```sql
INSERT INTO courses (course_name, required_subjects) VALUES
('B.A. (Hons) English', ARRAY['English', 'General Test']),
('B.Sc. (Hons) Physics', ARRAY['Physics', 'Mathematics', 'Chemistry']),
('B.Com (Hons)', ARRAY['Mathematics', 'General Test']);
-- Add all DU courses
```

## 4. Implementation Steps

### 4.1 Set Up the Environment
1. **Install Dependencies**:
   ```bash
   pip install django supabase django-environ
   ```
2. **Create Django Project**:
   ```bash
   django-admin startproject cuet_estimator
   cd cuet_estimator
   python manage.py startapp estimator
   ```
3. **Set Up Supabase**:
   - Create a Supabase project and note the API URL, anon key, and service role key.
   - Create a `.env` file:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_anon_key
     SECRET_KEY=your_django_secret_key
     ```
   - Update `settings.py`:
     ```python
     import environ
     env = environ.Env()
     environ.Env.read_env()
     SECRET_KEY = env('SECRET_KEY')
     ```

### 4.2 Initialize Supabase Client
```python
# estimator/supabase_utils.py
from supabase import create_client
import os

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)
```

### 4.3 Create Submission Form
```python
# estimator/forms.py
from django import forms

CATEGORIES = [
    ('General', 'General'),
    ('EWS', 'Economically Weaker Section'),
    ('OBC', 'Other Backward Classes'),
    ('SC', 'Scheduled Caste'),
    ('ST', 'Scheduled Tribe'),
    ('Single Girl Child', 'Single Girl Child'),
]

class SubmissionForm(forms.Form):
    category = forms.ChoiceField(choices=CATEGORIES)
    courses = forms.MultipleChoiceField(choices=[])  # Populate dynamically
```

Populate course choices:
```python
# estimator/views.py
from .supabase_utils import supabase

def get_course_choices():
    data = supabase.table('courses').select('course_name').execute()
    return [(course['course_name'], course['course_name']) for course in data.data]
```

Template with dynamic score fields:
```html
<!-- estimator/templates/submit.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: linear-gradient(135deg, #1e3c72, #2a5298); font-family: Arial, sans-serif; }
        .glass { backdrop-filter: blur(10px); background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 20px; max-width: 600px; margin: 50px auto; }
        .form-group { margin-bottom: 15px; }
        label { color: #fff; }
        input, select { width: 100%; padding: 10px; border: none; border-radius: 5px; background: rgba(255, 255, 255, 0.2); color: #fff; }
        button { background: #4a90e2; color: #fff; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #357abd; }
    </style>
</head>
<body>
    <div class="glass">
        <h2 style="color: #fff;">Submit Your CUET Scores</h2>
        <form method="post" id="submission-form">
            {% csrf_token %}
            <div class="form-group">
                <label for="category">Category:</label>
                {{ form.category }}
            </div>
            <div class="form-group">
                <label for="courses">Courses:</label>
                {{ form.courses }}
            </div>
            <div id="score-fields">
                <div class="score-entry">
                    <input type="text" name="subject_1" placeholder="Subject (e.g., English)" required>
                    <input type="number" name="score_1" placeholder="Score" min="0" max="200" required>
                </div>
            </div>
            <button type="button" onclick="addScoreField()">Add Subject</button>
            <button type="submit">Submit</button>
        </form>
    </div>
    <script>
        let scoreCount = 1;
        function addScoreField() {
            if (scoreCount < 10) {
                scoreCount++;
                const container = document.getElementById('score-fields');
                const entry = document.createElement('div');
                entry.className = 'score-entry';
                entry.innerHTML = `
                    <input type="text" name="subject_${scoreCount}" placeholder="Subject" required>
                    <input type="number" name="score_${scoreCount}" placeholder="Score" min="0" max="200" required>
                `;
                container.appendChild(entry);
            }
        }
    </script>
</body>
</html>
```

### 4.4 Handle Form Submission
```python
# estimator/views.py
import uuid
from django.shortcuts import render
from .forms import SubmissionForm
from .supabase_utils import supabase

def submit_scores(request):
    form = SubmissionForm()
    form.fields['courses'].choices = get_course_choices()
    if request.method == 'POST':
        category = request.POST.get('category')
        courses = request.POST.getlist('courses')
        scores = {}
        for i in range(1, 11):
            subject = request.POST.get(f'subject_{i}')
            score = request.POST.get(f'score_{i}')
            if subject and score:
                scores[subject] = int(score)
        unique_id = str(uuid.uuid4())
        data = {
            'unique_id': unique_id,
            'category': category,
            'courses': courses,
            'scores': scores,
            'created_at': 'now()'
        }
        response = supabase.table('submissions').insert(data).execute()
        return render(request, 'success.html', {'unique_id': unique_id})
    return render(request, 'submit.html', {'form': form})
```

Success template:
```html
<!-- estimator/templates/success.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: linear-gradient(135deg, #1e3c72, #2a5298); font-family: Arial, sans-serif; }
        .glass { backdrop-filter: blur(10px); background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 20px; max-width: 600px; margin: 50px auto; }
        h2, p { color: #fff; }
        a { color: #4a90e2; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="glass">
        <h2>Submission Successful</h2>
        <p>Your unique ID is: <strong>{{ unique_id }}</strong></p>
        <p>Save this ID to view your rankings in real-time.</p>
        <a href="{% url 'view_rankings' %}">View Rankings</a>
    </div>
</body>
</html>
```

### 4.5 Implement Real-Time Rankings
Use Supabase’s JavaScript client for real-time updates in the rankings view. The backend pre-fetches initial data, and the frontend subscribes to changes.

```python
# estimator/views.py
def view_rankings(request):
    course_choices = get_course_choices()
    context = {'course_choices': course_choices}
    if request.method == 'POST':
        unique_id = request.POST.get('unique_id')
        selected_course = request.POST.get('course')
        selected_category = request.POST.get('category')
        # Fetch user’s submission
        user_data = supabase.table('submissions').select('*').eq('unique_id', unique_id).execute()
        if not user_data.data:
            return render(request, 'error.html', {'message': 'Invalid unique ID'})
        user = user_data.data[0]
        # Fetch initial submissions
        data = supabase.table('submissions').select('*').execute()
        submissions = data.data
        # Fetch course details
        course_data = supabase.table('courses').select('*').eq('course_name', selected_course).execute()
        required_subjects = course_data.data[0]['required_subjects']
        # Calculate initial rankings
        relevant_submissions = [
            s for s in submissions
            if selected_course in s['courses'] and (not selected_category or s['category'] == selected_category)
        ]
        merit_scores = []
        for s in relevant_submissions:
            total = sum(s['scores'].get(subject, 0) for subject in required_subjects)
            merit_scores.append((s['unique_id'], total))
        merit_scores.sort(key=lambda x: x[1], reverse=True)
        user_rank = next((i+1 for i, (uid, _) in enumerate(merit_scores) if uid == unique_id), None)
        context.update({
            'unique_id': unique_id,
            'selected_course': selected_course,
            'selected_category': selected_category,
            'rank': user_rank,
            'total': len(merit_scores),
            'supabase_url': supabase.client_options.rest_url,
            'supabase_key': supabase.client_options.headers['Authorization'].split(' ')[1]
        })
    return render(request, 'rankings.html', context)
```

Rankings template with real-time updates:
```html
<!-- estimator/templates/rankings.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: linear-gradient(135deg, #1e3c72, #2a5298); font-family: Arial, sans-serif; }
        .glass { backdrop-filter: blur(10px); background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 20px; max-width: 600px; margin: 50px auto; }
        .form-group { margin-bottom: 15px; }
        label, h2, h3, p { color: #fff; }
        input, select { width: 100%; padding: 10px; border: none; border-radius: 5px; background: rgba(255, 255, 255, 0.2); color: #fff; }
        button { background: #4a90e2; color: #fff; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #357abd; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
</head>
<body>
    <div class="glass">
        <h2>View Your Rankings</h2>
        <form method="post">
            {% csrf_token %}
            <div class="form-group">
                <label for="unique_id">Unique ID:</label>
                <input type="text" name="unique_id" id="unique_id" required>
            </div>
            <div class="form-group">
                <label for="course">Course:</label>
                <select name="course" id="course" required>
                    {% for value, label in course_choices %}
                        <option value="{{ value }}" {% if value == selected_course %}selected{% endif %}>{{ label }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label for="category">Category (Optional):</label>
                <select name="category" id="category">
                    <option value="">All Categories</option>
                    {% for value, label in form.category.choices %}
                        <option value="{{ value }}" {% if value == selected_category %}selected{% endif %}>{{ label }}</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit">View Rank</button>
        </form>
        <div id="rankings">
            {% if rank %}
                <h3>Your Rank</h3>
                <p>For <span id="course-name">{{ selected_course }}</span> (Category: <span id="category-name">{{ selected_category|default:"All" }}</span>):</p>
                <p>Rank: <span id="rank">{{ rank }}</span> out of <span id="total">{{ total }}</span></p>
                <p><strong>Disclaimer:</strong> These rankings are estimates based on crowdsourced data and may not reflect official DU cutoffs.</p>
            {% endif %}
        </div>
    </div>
    {% if unique_id %}
    <script>
        const supabase = Supabase.createClient('{{ supabase_url }}', '{{ supabase_key }}');
        const requiredSubjects = {{ required_subjects|safe }};
        let submissions = [];

        async function fetchSubmissions() {
            const { data } = await supabase.from('submissions').select('*');
            submissions = data;
            updateRankings();
        }

        function calculateRank() {
            const uniqueId = '{{ unique_id }}';
            const course = document.getElementById('course').value;
            const category = document.getElementById('category').value;
            const relevantSubmissions = submissions.filter(s => 
                s.courses.includes(course) && (!category || s.category === category)
            );
            const meritScores = relevantSubmissions.map(s => ({
                unique_id: s.unique_id,
                score: requiredSubjects.reduce((sum, subj) => sum + (s.scores[subj] || 0), 0)
            }));
            meritScores.sort((a, b) => b.score - a.score);
            const rank = meritScores.findIndex(s => s.unique_id === uniqueId) + 1;
            return { rank, total: meritScores.length };
        }

        function updateRankings() {
            const { rank, total } = calculateRank();
            document.getElementById('rank').textContent = rank || 'N/A';
            document.getElementById('total').textContent = total;
            document.getElementById('course-name').textContent = document.getElementById('course').value;
            document.getElementById('category-name').textContent = document.getElementById('category').value || 'All';
        }

        supabase.channel('submissions').on('postgres_changes', { event: '*', schema: 'public', table: 'submissions' }, payload => {
            if (payload.eventType === 'INSERT') {
                submissions.push(payload.new);
            } else if (payload.eventType === 'UPDATE') {
                const index = submissions.findIndex(s => s.unique_id === payload.new.unique_id);
                if (index !== -1) submissions[index] = payload.new;
            } else if (payload.eventType === 'DELETE') {
                submissions = submissions.filter(s => s.unique_id !== payload.old.unique_id);
            }
            updateRankings();
        }).subscribe();

        fetchSubmissions();

        document.getElementById('course').addEventListener('change', updateRankings);
        document.getElementById('category').addEventListener('change', updateRankings);
    </script>
    {% endif %}
</body>
</html>
```

Error template:
```html
<!-- estimator/templates/error.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: linear-gradient(135deg, #1e3c72, #2a5298); font-family: Arial, sans-serif; }
        .glass { backdrop-filter: blur(10px); background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 20px; max-width: 600px; margin: 50px auto; }
        h2, p { color: #fff; }
        a { color: #4a90e2; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="glass">
        <h2>Error</h2>
        <p>{{ message }}</p>
        <a href="{% url 'view_rankings' %}">Try Again</a>
    </div>
</body>
</html>
```

### 4.6 Configure URLs
```python
# estimator/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_scores, name='submit_scores'),
    path('rankings/', views.view_rankings, name='view_rankings'),
]
```

```python
# cuet_estimator/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('estimator.urls')),
]
```

### 4.7 Enhance UI
- Improved CSS for blurred glass effect and responsiveness:
  ```css
  body {
      background: linear-gradient(135deg, #1e3c72, #2a5298);
      font-family: Arial, sans-serif;
  }
  .glass {
      backdrop-filter: blur(10px);
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 15px;
      padding: 20px;
      max-width: 600px;
      margin: 50px auto;
  }
  @media (max-width: 600px) {
      .glass { margin: 20px; padding: 15px; }
  }
  ```

### 4.8 Real-Time Functionality
- **Supabase Subscriptions**: The JavaScript client subscribes to `submissions` table changes (`INSERT`, `UPDATE`, `DELETE`) using Supabase’s real-time API.
- **Client-Side Updates**: Rankings are recalculated and displayed instantly when new submissions arrive or filters change.
- **Optimization**: Initial data is fetched server-side to reduce client load, and subsequent updates are handled via WebSockets.

### 4.9 Ensure Data Privacy
- Collect only the unique ID; no personal data.
- Enable HTTPS in production.
- Use Supabase RLS to restrict data access:
  ```sql
  CREATE POLICY "Anonymous read" ON submissions FOR SELECT USING (true);
  CREATE POLICY "Anonymous insert" ON submissions FOR INSERT WITH CHECK (true);
  ```

### 4.10 Add Disclaimer
> Disclaimer: These rankings are estimates based on crowdsourced data and may not reflect official DU cutoffs.

## 5. DU Admission Process Integration
The platform uses the subject combinations from [DU_CUET_Subject_Combinations_2025.md](artifact ID: `54425bbb-e776-4eb0-9107-4d2521225d8e`) to calculate merit scores, ensuring alignment with DU’s Common Seat Allocation System (CSAS).

## 6. Challenges and Optimizations
- **Scalability**: For high traffic, use Supabase’s query optimization or cache rankings in Redis.
- **WebSocket Limits**: Monitor Supabase’s connection limits; consider throttling updates for large datasets.
- **Accuracy**: Regularly update the `courses` table with DU’s latest data.
- **Security**: Validate inputs server-side to prevent injection attacks.

## 7. Testing
- **Real-Time Updates**: Submit scores from multiple browsers to verify instant ranking updates.
- **Ranking Accuracy**: Test with sample data to ensure merit scores align with required subjects.
- **UI**: Check responsiveness and blurred glass effect across devices.
- **Privacy**: Confirm no personal data is stored.

## 8. Deployment
- Deploy Django on Heroku, Render, or AWS with Gunicorn.
- Configure Supabase for production with RLS and backups.
- Use a CDN for the Supabase JavaScript client.

## 9. Future Enhancements
- **Historical Trends**: Display past cutoff trends.
- **Push Notifications**: Notify users of significant rank changes.
- **Accessibility**: Add high-contrast modes and screen reader support.

## 10. Conclusion
This guide provides a complete plan to build a real-time CUET Cutoff Estimator using Django and Supabase. The application delivers instant ranking updates, a modern UI, and compliance with DU’s admission process, making it a valuable tool for students.