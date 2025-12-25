from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_('Foydalanuvchi nomi yoki Email'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('username yoki email@example.com')
        })
    )
    password = forms.CharField(
        label=_('Parol'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('********')
        })
    )
    remember_me = forms.BooleanField(
        label=_('Meni eslab qol'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': True})


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label=_('Email manzil'),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('email@example.com')
        })
    )
    first_name = forms.CharField(
        label=_('Ism'),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ismingiz')
        })
    )
    last_name = forms.CharField(
        label=_('Familiya'),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Familiyangiz')
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Foydalanuvchi nomi')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Bu email manzil allaqachon ro\'yxatdan o\'tgan.'))
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
        
        return user


class ProfileUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(
        label=_('Tug\'ilgan sana'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    bio = forms.CharField(
        label=_('O\'zim haqimda'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('O\'zingiz haqingizda qisqacha...')
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'profile'):
            self.fields['birth_date'].initial = self.instance.profile.birth_date
            self.fields['bio'].initial = self.instance.profile.bio
            self.fields['gender'] = forms.ChoiceField(
                label=_('Jins'),
                choices=UserProfile.GENDER_CHOICES,
                required=False,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                initial=self.instance.profile.gender
            )
            self.fields['city'] = forms.CharField(
                label=_('Shahar'),
                required=False,
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                initial=self.instance.profile.city
            )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            # Update user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            if hasattr(self, 'cleaned_data'):
                if 'birth_date' in self.cleaned_data:
                    profile.birth_date = self.cleaned_data['birth_date']
                if 'bio' in self.cleaned_data:
                    profile.bio = self.cleaned_data['bio']
                if 'gender' in self.cleaned_data:
                    profile.gender = self.cleaned_data['gender']
                if 'city' in self.cleaned_data:
                    profile.city = self.cleaned_data['city']
                profile.save()
        
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_('Joriy parol'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label=_('Yangi parol'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label=_('Yangi parolni tasdiqlash'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )