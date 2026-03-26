# views.py
from django.http import JsonResponse
from .rag import answer_question

def chat_view(request):
    query = request.GET.get("q", "")
    if not query:
        return JsonResponse({"response": "Por favor envía una pregunta usando ?q=..."})

    response = answer_question(query)
    return JsonResponse({"response": response})