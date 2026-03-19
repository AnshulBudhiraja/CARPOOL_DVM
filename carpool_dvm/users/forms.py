from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Driver
from django.contrib.auth.hashers import check_password

class UserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField()
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')



class DriverSetUpForm(forms.ModelForm):

    class Meta:
        model = Driver
        fields = ('car_model', 'plate_number', 'max_passengers_car', 'license_number' , 'driver_password')

    def save(self, commit=True):
        #dont commit to database yet
        user = super().save(commit=False)

        if commit:
            user.save()

            Driver.objects.create(
                user = user,
                license_number = self.cleaned_data.get('license_number'),
                car_model=self.cleaned_data.get('car_model'),
                plate_number=self.cleaned_data.get('plate_number'),
                max_passengers = self.cleaned_data.get('max_passengers'),
                driver_password = self.cleaned_data.get('driver_password')
            )
        return user


class DriverLoginForm(forms.Form):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'username',
            'class': 'form-control'
        })
    )
    driver_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Driver Password',
            'class': 'form-control'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        d_pass = cleaned_data.get("driver_password")

        if username and d_pass:
            # 1. Search for the user
            user = User.objects.filter(username=username).first()
            driver = Driver.objects.filter(user = user).first()
            
            # 2. Check if the user has a driver profile
            if not user.is_driver or not driver:
                raise forms.ValidationError("This account is not registered as a driver.")

            # 3. Check the driver-specific password
            if d_pass != driver.driver_password:
                raise forms.ValidationError("Incorrect driver password.")
            self.user = user
            self.driver = driver

        return cleaned_data
