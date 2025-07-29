from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class UsuarioCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite seu nome de usuário',
            'autocomplete': 'username'
        }),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s]+$',
                message='Nome de usuário pode conter apenas letras, números e espaços.'
            )
        ],
        help_text='Pode conter letras, números e espaços.'
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Digite seu email', 
            'autocomplete': 'email'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Digite sua senha', 
            'autocomplete': 'new-password'
        }), 
        help_text='Sua senha deve conter pelo menos 8 caracteres.'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Confirme sua senha', 
            'autocomplete': 'new-password'
        }), 
        help_text='Digite a mesma senha novamente para confirmação.'
    )

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = ' '.join(username.split())
            if Usuario.objects.filter(username=username).exists():
                raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está em uso.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.acesso = False  # Usando o campo customizado
        if commit:
            user.save()
        return user

class UsuarioLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite seu usuário',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite sua senha',
            'autocomplete': 'current-password'
        })
    ) 