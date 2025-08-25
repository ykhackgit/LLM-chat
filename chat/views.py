import json
import time
import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import ChatMessage

OLLAMA_API = "https://companies-triangle-cove-performing.trycloudflare.com/"   # change if tunneling
V2TPU_API=" https://toolbox-bracket-cuba-grows.trycloudflare.com/"

a=True
def chat_view(request):
    return render(request, "chat.html")


def get_history(request):
    """Return full chat history from DB."""
    history = ChatMessage.objects.order_by("created_at")
    data = []
    for msg in history:
        data.append({
            "role": msg.role,
            "content": msg.content,
            "file": msg.file.url if msg.file else None,
            "created_at": msg.created_at.strftime("%H:%M:%S"),
        })
    return JsonResponse({"history": data})


@csrf_exempt
def send_message(request):
    if request.method == "POST":
       
            data = request.POST.dict()
            model = data.get("model", "llama3")
            message = data.get("message", "")

            uploaded_file = request.FILES.get("file")

            # store user msg in DB
            user_msg = ChatMessage.objects.create(
                role="user", content=message, file=uploaded_file
            )

            # prepare history for Ollama
            history = [
                {"role": m.role, "content": m.content}
                for m in ChatMessage.objects.exclude(content__isnull=True).order_by("created_at")
            ]

            payload_ollama = {"model": model, "messages": history, "stream": True}
           


            # def stream():
            #     first_token_time = None
            #     start = time.time()
            #     token_count = 0
            #     bot_reply = ""

            #     with requests.post(f"{OLLAMA_API}/api/chat", json=payload, stream=True) as r:
            #         for line in r.iter_lines():
            #             if line:
            #                 j = json.loads(line.decode("utf-8"))
            #                 content = j.get("message", {}).get("content", "")
            #                 if content:
            #                     token_count += 1
            #                     bot_reply += content
            #                     if first_token_time is None:
            #                         first_token_time = time.time() - start
            #                     yield content

            #     # save assistant reply
            #     ChatMessage.objects.create(role="assistant", content=bot_reply)

            #     total_time = time.time() - start
            #     tps = token_count / total_time if token_count else 0
            #     stats = f"\n\n---\n⏱ First token: {first_token_time:.2f}s | TPS: {tps:.2f} | Tokens: {token_count} | Time: {total_time:.2f}s"
            #     yield stats

            # return StreamingHttpResponse(stream(), content_type="text/plain")


            def generate():
                # payload = {"model": "llama3", "messages": [{"role": "user", "content": "Hello"}]}
                start = time.time()
                bot_reply = ""

                with requests.post(f"{ OLLAMA_API if a ==True else V2TPU_API}/api/chat", json= payload_ollama , stream=True) as r:
                    for line in r.iter_lines():
                        if line:
                            j = json.loads(line.decode("utf-8"))
                            content = j.get("message", {}).get("content", "")
                            if content:
                                bot_reply += content
                                # Send token immediately
                                yield content  

                # (optional) final stats
                yield f"\n\n---\nReply finished in {time.time() - start:.2f}s"

            return StreamingHttpResponse(generate(), content_type="text/plain")

      

    return JsonResponse({"error": "Invalid request"}, status=400)
