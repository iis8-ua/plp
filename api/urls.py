"""Rutas exactas de api/api.yaml (sin barra final)."""

from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('withdraw', views.withdraw, name='withdraw'),
    path('balance', views.balance, name='balance'),
    path('pay', views.pay, name='pay'),
    path('refunds/request', views.refund_request, name='refund-request'),
    path('refunds/accept', views.refund_accept, name='refund-accept'),
    path('refunds/reject', views.refund_reject, name='refund-reject'),
    path('refunds', views.refunds, name='refunds'),
    path('companies/add', views.company_add, name='company-add'),
    path('companies/delete', views.company_delete, name='company-delete'),
    path('companies/reactivate', views.company_reactivate, name='company-reactivate'),
    path('companies', views.companies, name='companies'),
    path('payments', views.payments, name='payments'),
    path('ticket/add', views.ticket_add, name='ticket-add'),
    path('ticket/delete', views.ticket_delete, name='ticket-delete'),
    path('ticket/update', views.ticket_update, name='ticket-update'),
    path('ticket/message', views.ticket_message, name='ticket-message'),
    path('ticket/assign', views.ticket_assign, name='ticket-assign'),
    path('tickets', views.tickets, name='tickets'),
    path('technicians', views.technicians, name='technicians'),
    path('profile', views.profile, name='profile'),
    path('profile/password', views.profile_password, name='profile-password'),
]
