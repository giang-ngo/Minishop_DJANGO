from django import forms
from .models import Account, UserProfile


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Create Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username',
                  'email', 'phone_number', 'password']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['phone_number'].widget.attrs[
            'placeholder'] = 'Phone Number (Optional)'
        for key, value in self.fields.items():
            value.widget.attrs.update({'class': 'input'})

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Password does not match!')

        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'Invalid': {
                                       'Images files only'}}, widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2',
                  'city', 'state', 'country', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class VerifyOTPForm(forms.Form):
    otp = forms.CharField(max_length=6)
    new_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'New Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned_data = super(VerifyOTPForm, self).clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match!')

        return cleaned_data


class UpdateRecoveryPhoneNumberForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['recovery_phone_number']

    def __init__(self, *args, **kwargs):
        super(UpdateRecoveryPhoneNumberForm, self).__init__(*args, **kwargs)
        self.fields['recovery_phone_number'].widget.attrs['placeholder'] = 'Recovery Phone Number'
        for key, value in self.fields.items():
            value.widget.attrs.update({'class': 'input'})

    def clean_recovery_phone_number(self):
        phone_number = self.cleaned_data.get('recovery_phone_number')
        # Format Vietnamese phone number (e.g., "+84" country code)
        if not phone_number.startswith('+84'):
            phone_number = '+84' + phone_number.lstrip('0')
        return phone_number


class VerifyRecoveryPhoneForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True)

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if len(otp) != 6 or not otp.isdigit():
            raise forms.ValidationError('Invalid OTP.')
        return otp


class RequestPasswordResetForm(forms.Form):
    recovery_phone_number = forms.CharField(max_length=20)

    def clean_recovery_phone_number(self):
        recovery_phone_number = self.cleaned_data['recovery_phone_number']
        # Loại bỏ khoảng trắng hoặc ký tự không phải số
        recovery_phone_number = ''.join(
            filter(str.isdigit, recovery_phone_number))

        # Định dạng số điện thoại Việt Nam
        if recovery_phone_number.startswith('0'):
            recovery_phone_number = '84' + recovery_phone_number[1:]
        elif recovery_phone_number.startswith('84'):
            # Không làm gì vì số đã đúng định dạng
            pass
        elif recovery_phone_number.startswith('+84'):
            # Remove the '+' sign
            recovery_phone_number = recovery_phone_number[1:]
        else:
            raise forms.ValidationError(
                'Số điện thoại không hợp lệ. Vui lòng nhập số bắt đầu bằng 0 hoặc 84.')

        # Thêm dấu '+' để định dạng thành số quốc tế
        recovery_phone_number = '+' + recovery_phone_number

        # Kiểm tra xem số điện thoại đã tồn tại trong cơ sở dữ liệu hay chưa
        if not Account.objects.filter(recovery_phone_number=recovery_phone_number).exists():
            raise forms.ValidationError(
                'Số điện thoại khôi phục không tồn tại.')

        return recovery_phone_number


class VerifyOTPForPasswordResetForm(forms.Form):
    otp = forms.CharField(max_length=6)
    new_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'New Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned_data = super(VerifyOTPForPasswordResetForm, self).clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match!')

        return cleaned_data
