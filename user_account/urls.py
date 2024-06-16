from django.urls import path
from .import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),


    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/',
         views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/', views.reset_password, name='reset_password'),

    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/',
         views.order_detail, name='order_detail'),

    # do mình dùng ở đây là tài khoản Twilio thử nghiệm nên bị giới hạn số điện thoại bạn có thể sử dụng phiên bản trả phí để có thể xác thực otp với bất kì số điện thoại nào

    # url thêm phone otp
    path('update_recovery_phone/', views.update_recovery_phone_number,
         name='update_recovery_phone'),
    path('verify_recovery_phone/', views.verify_recovery_phone,
         name='verify_recovery_phone'),

    # url reset password bằng otp
    path('verify-otp-for-password-reset/', views.verify_otp_for_password_reset,
         name='verify_otp_for_password_reset'),
]
