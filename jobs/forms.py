from django import forms
from django.forms import inlineformset_factory
from .models import Job, JobApplication, JobImage, Category, Payment

# Payment initiation form
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'phone_number']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Amount (KES)',
                'step': '0.01'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mpesa phone number'
            }),
        }


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'category', 'location', 
            'urgency', 'budget_min', 'budget_max', 'deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Fix leaking kitchen faucet'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the job in detail...'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Nairobi, Westlands'
            }),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
            'budget_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Select a category"


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['message', 'proposed_rate']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell the customer why you\'re the right person for this job...'
            }),
            'proposed_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }
        labels = {
            'message': 'Cover Message',
            'proposed_rate': 'Your Proposed Rate (KES)'
        }
        help_texts = {
            'proposed_rate': 'Optional: Your proposed hourly rate or total cost for this job'
        }


class JobSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search jobs...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location...'
        })
    )
    
    urgency = forms.ChoiceField(
        choices=[('', 'All Urgency Levels')] + Job.URGENCY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )