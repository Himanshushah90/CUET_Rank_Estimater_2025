from django import forms

CATEGORY_CHOICES = [
    ("GEN", "General"),
    ("OBC", "OBC"),
    ("SC", "SC"),
    ("ST", "ST"),
    ("EWS", "EWS"),
]

class ScoreSubmissionForm(forms.Form):
    category = forms.ChoiceField(label="Category", choices=CATEGORY_CHOICES, required=True)
    include_general_test = forms.BooleanField(label="Include General Test", required=False)