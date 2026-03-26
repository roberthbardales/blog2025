# import re
# import requests
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from applications.entrada.models import Entry
# from .models import EntryChunk

# # Modelo embeddings ligero
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # 🔹 limpiar HTML
# def clean_html(raw_html):
#     clean = re.compile('<.*?>')
#     return re.sub(clean, '', raw_html)

# # 🔹 dividir texto en chunks pequeños
# def chunk_text(text, max_length=100):
#     words = text.split()
#     chunks = []
#     current_chunk = []
#     for word in words:
#         current_chunk.append(word)
#         if len(current_chunk) >= max_length:
#             chunks.append(" ".join(current_chunk))
#             current_chunk = []
#     if current_chunk:
#         chunks.append(" ".join(current_chunk))
#     return chunks

# # 🔹 generar embedding
# def get_embedding(text):
#     return model.encode(text).tolist()

# # 🔹 indexar posts del blog
# def index_entries():
#     EntryChunk.objects.all().delete()  # limpiar antes de indexar
#     entries = Entry.objects.filter(public=True)

#     for entry in entries:
#         print(f"Procesando Entry {entry.id}...")
#         clean_content = clean_html(entry.content)

#         # solo contenido real, sin metadatos
#         full_text = clean_content

#         chunks = chunk_text(full_text)
#         for chunk in chunks:
#             embedding = get_embedding(chunk)
#             EntryChunk.objects.create(
#                 entry=entry,
#                 content=chunk,
#                 embedding=embedding
#             )
#     print("Indexación completa 🚀")

# # 🔹 similitud coseno
# def cosine_similarity(a, b):
#     a = np.array(a)
#     b = np.array(b)
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# # 🔹 buscar chunks más relevantes
# def search_similar_chunks(query, top_k=2):
#     query_embedding = get_embedding(query)
#     chunks = EntryChunk.objects.all()
#     results = []
#     for chunk in chunks:
#         similarity = cosine_similarity(query_embedding, chunk.embedding)
#         results.append((similarity, chunk))
#     results.sort(key=lambda x: x[0], reverse=True)
#     return results[:top_k]

# # 🔹 generar respuesta con TinyLlama (estrictamente del blog)
# def answer_question(query):
#     results = search_similar_chunks(query, top_k=2)
#     if not results:
#         return "No encontré esa información en el blog."

#     # filtrar contenido vacío y unir los chunks
#     context = "\n\n".join([chunk.content for _, chunk in results if chunk.content.strip() != ""])

#     # limitar tamaño del contexto
#     context = context[:1000]

#     # verificar que la pregunta tenga relación con los chunks
#     keywords = query.lower().split()
#     if not any(word in context.lower() for word in keywords):
#         return "No encontré esa información en el blog"

#     # prompt estricto
#     prompt = f"""
# Eres un asistente que RESPONDE SOLO con información extraída del contenido del blog.
# No inventes información ni detalles que no estén en el contexto.
# Si la respuesta no está en el contexto, di exactamente: "No encontré esa información en el blog".

# Contexto:
# {context}

# Pregunta:
# {query}
# """

#     # llamada a TinyLlama
#     res = requests.post(
#         "http://localhost:11434/api/generate",
#         json={
#             "model": "tinyllama",
#             "prompt": prompt,
#             "stream": False
#         }
#     )

#     return res.json()["response"]