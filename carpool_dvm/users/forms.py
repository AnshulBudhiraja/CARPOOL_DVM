from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Driver

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
        fields = ('car_model', 'plate_number', 'max_passengers_car', 'license_number')

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
            )
        return user
