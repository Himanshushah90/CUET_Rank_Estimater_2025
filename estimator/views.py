from django.shortcuts import render
from .forms import ScoreSubmissionForm
from .supabase_utils import (
    insert_submission, get_courses, get_combinations_for_course,
    get_subjects, get_submission, get_all_submissions
)
import uuid
import json

def submit_scores(request):
    subjects = get_subjects()
    subject_choices = [(s['subject_name'], s['subject_name']) for s in subjects]
    category_choices = [
        ("GEN", "General"),
        ("OBC", "OBC"),
        ("SC", "SC"),
        ("ST", "ST"),
        ("EWS", "EWS"),
    ]
    if request.method == "POST":
        form = ScoreSubmissionForm(request.POST)
        if form.is_valid():
            unique_id = str(uuid.uuid4())
            category = form.cleaned_data["category"]
            include_general_test = form.cleaned_data.get("include_general_test", False)
            # Parse dynamic subject/marks from POST
            scores = {}
            subjects_post = request.POST.getlist("subject")
            marks_post = request.POST.getlist("marks")
            for subj, mark in zip(subjects_post, marks_post):
                if subj and mark:
                    scores[subj] = int(mark)
            # General Test
            if include_general_test and request.POST.get("general_test_score"):
                scores["General Aptitude Test"] = int(request.POST.get("general_test_score"))
            submission_data = {
                "unique_id": unique_id,
                "category": category,
                "scores": scores,
                "include_general_test": include_general_test,
            }
            insert_submission(submission_data)
            return render(request, "estimator/success.html", {"unique_id": unique_id})
    else:
        form = ScoreSubmissionForm()
    return render(request, "estimator/submit.html", {
        "form": form,
        "subject_choices": json.dumps(subject_choices),
        "category_choices": category_choices,
    })

def view_rankings(request):
    context = {}
    if request.method == "POST":
        unique_id = request.POST.get("unique_id")
        user_submission = get_submission(unique_id)
        if not user_submission:
            context["error"] = "Invalid unique ID."
            return render(request, "estimator/rankings.html", context)
        user_scores = user_submission["scores"]
        user_category = user_submission["category"]
        user_included_general_test = user_submission.get("include_general_test", False)
        all_courses = get_courses()
        all_submissions = get_all_submissions()
        subject_list_types = {row["subject_name"]: row["list_type"] for row in get_subjects()}
        results = []
        for course in all_courses:
            combinations = get_combinations_for_course(course["course_id"])
            best_score = None
            best_combo = None
            best_subjects = None
            for combo in combinations:
                merit = get_best_merit_for_combination(
                    user_scores, subject_list_types, combo, user_included_general_test
                )
                if merit is not None:
                    score, subjects_used = merit
                    if best_score is None or score > best_score:
                        best_score = score
                        best_combo = combo["description"]
                        best_subjects = subjects_used
            if best_score is not None:
                # Calculate both category rank and general rank
                scores_for_course = []
                scores_for_course_category = []
                for sub in all_submissions:
                    sub_scores = sub["scores"]
                    sub_included_general_test = sub.get("include_general_test", False)
                    sub_category = sub.get("category", "GEN")
                    for combo in combinations:
                        merit = get_best_merit_for_combination(
                            sub_scores, subject_list_types, combo, sub_included_general_test
                        )
                        if merit is not None:
                            s_score, _ = merit
                            scores_for_course.append((sub["unique_id"], s_score, sub_category))
                            if sub_category == user_category:
                                scores_for_course_category.append((sub["unique_id"], s_score))
                            break
                # General rank (compare with all)
                scores_for_course.sort(key=lambda x: x[1], reverse=True)
                user_general_rank = next((i+1 for i, (uid, _, _) in enumerate(scores_for_course) if uid == unique_id), None)
                # Category rank (compare only with same category)
                scores_for_course_category.sort(key=lambda x: x[1], reverse=True)
                user_category_rank = next((i+1 for i, (uid, _) in enumerate(scores_for_course_category) if uid == unique_id), None)
                # For GEN students, category rank is NA
                if user_category == "GEN":
                    user_category_rank = "NA"
                results.append({
                    "course": course["course_name"],
                    "combination": best_combo,
                    "subjects": best_subjects,
                    "score": best_score,
                    "category_rank": user_category_rank,
                    "general_rank": user_general_rank,
                    "total": len(scores_for_course)
                })
        context["results"] = results
        context["unique_id"] = unique_id
        context["user_category"] = user_category
    return render(request, "estimator/rankings.html", context)

def get_best_merit_for_combination(user_scores, subject_list_types, combination, user_included_general_test):
    req = combination["required_subjects"]
    if isinstance(req, str):
        req = json.loads(req)
    used_subjects = set()
    total_score = 0

    # 1. Mandatory subjects (by name)
    for mand in req.get("mandatory", []):
        if mand not in user_scores:
            return None  # Not eligible
        total_score += user_scores[mand]
        used_subjects.add(mand)

    add = req.get("additional", {})

    # 2. Handle List B (domain) subjects
    if "from" in add or "from_domain" in add:
        key = "from" if "from" in add else "from_domain"
        count = add.get("count") or add.get("domain_count") or 0
        list_type = "B" if add[key] == "LIST_B" else "A"
        available = [s for s in user_scores if subject_list_types.get(s) == list_type and s not in used_subjects]
        if len(available) < count:
            return None
        best_subjects = sorted(available, key=lambda s: user_scores[s], reverse=True)[:count]
        total_score += sum(user_scores[s] for s in best_subjects)
        used_subjects.update(best_subjects)

    # 3. Handle List A (language) subjects
    if "from_language" in add and "language_count" in add:
        count = add["language_count"]
        available = [s for s in user_scores if subject_list_types.get(s) == "A" and s not in used_subjects]
        if len(available) < count:
            return None
        best_subjects = sorted(available, key=lambda s: user_scores[s], reverse=True)[:count]
        total_score += sum(user_scores[s] for s in best_subjects)
        used_subjects.update(best_subjects)

    # 4. Handle specific domain subjects (e.g., Mathematics / Applied Mathematics)
    if "from_domain" in add and isinstance(add["from_domain"], list):
        for domain_subj in add["from_domain"]:
            if domain_subj not in user_scores or domain_subj in used_subjects:
                return None
            total_score += user_scores[domain_subj]
            used_subjects.add(domain_subj)

    # 5. Handle other_count/other subjects
    if "from_other" in add and "other_count" in add:
        count = add["other_count"]
        list_type = "B" if add["from_other"] == "LIST_B" else "A"
        available = [s for s in user_scores if subject_list_types.get(s) == list_type and s not in used_subjects]
        if len(available) < count:
            return None
        best_subjects = sorted(available, key=lambda s: user_scores[s], reverse=True)[:count]
        total_score += sum(user_scores[s] for s in best_subjects)
        used_subjects.update(best_subjects)

    # 6. Handle General Test and other special tests robustly
    needs_general_test = (
        combination.get("combination_type") == "language_and_aptitude"
        or add.get("aptitude_test") is True
    )
    if needs_general_test:
        if not user_included_general_test or "General Aptitude Test" not in user_scores or "General Aptitude Test" in used_subjects:
            return None
        total_score += user_scores["General Aptitude Test"]
        used_subjects.add("General Aptitude Test")

    if add.get("performance_test"):
        if "Performance-Based Test" not in user_scores or "Performance-Based Test" in used_subjects:
            return None
        total_score += user_scores["Performance-Based Test"]
        used_subjects.add("Performance-Based Test")
    if add.get("practical_test"):
        if "Practical-Based Test" not in user_scores or "Practical-Based Test" in used_subjects:
            return None
        total_score += user_scores["Practical-Based Test"]
        used_subjects.add("Practical-Based Test")

    return total_score, list(used_subjects)