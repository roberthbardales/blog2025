from applications.home.models import Home

def home_contact(request):
    try:
        home = Home.objects.latest('created')
        phone = home.phone
        correo = home.contact_email
    except Home.DoesNotExist:
        phone = ''
        correo = ''

    return {
        'phone': phone,
        'correo': correo,
    }
