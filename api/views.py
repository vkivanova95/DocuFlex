from asgiref.sync import sync_to_async
import httpx, base64, os
from django.conf import settings
from django.shortcuts import render
from django.utils.timezone import now

# from loan_requests.choices import RequestStatus
# from loan_requests.models import Request
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
import random
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from annexes.models import GeneratedAnnex
from api.models import SignatureLog
from logs.models import SystemLog
from logs.choices import ActionType


# class MockSignAnnexView(APIView):
#     def post(self, request, *args, **kwargs):
#         # симулиране случайно подписване
#         success = random.choice([True, False])
#         annex_number = request.data.get("annex_number", "unknown")
#
#         if success:
#             return Response(
#                 {
#                     "status": "success",
#                     "message": f"Анекс {annex_number} е подписан успешно.",
#                 }
#             )
#         else:
#             return Response(
#                 {
#                     "status": "failure",
#                     "message": f"Анекс {annex_number} не е подписан!",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


# При използване на MockSignAnnexView via HTTP — заявката не се изпълнява в Azure, грешка RemoteProtocolError:
# Server disconnected without sending a response. Затова се замества с функцията, за да се симулира подписването на анекс в реална среда.
def mock_sign_annex(annex_number, file_base64):
    if not annex_number or not file_base64:
        return {
            "status": "failure",
            "message": "Липсва 'annex_number' или 'file_base64'.",
        }

    success = random.choice([True, False])

    if success:
        return {
            "status": "success",
            "message": f"Анекс {annex_number} е подписан успешно.",
        }
    else:
        return {"status": "failure", "message": f"Анекс {annex_number} не е подписан!"}


@method_decorator(login_required, name="dispatch")
class SendGeneratedAnnexView(View):
    async def get(self, request, pk):
        def get_annex_and_check_permission():
            annex = GeneratedAnnex.objects.select_related("request").get(pk=pk)
            if annex.request.maker != request.user and not request.user.is_superuser:
                return annex, False
            return annex, True

        annex, has_permission = await sync_to_async(get_annex_and_check_permission)()

        if not has_permission:
            return await sync_to_async(render)(
                request,
                "api/send_result.html",
                {
                    "status": "error",
                    "message": "Нямате права да изпратите този анекс за подписване.",
                },
            )

        # Проверка дали вече има успешно подписване
        latest_log = await sync_to_async(
            SignatureLog.objects.filter(
                annex_number=annex.annex_number,
                request=annex.request,
                is_signed_successfully=True,
            )
            .order_by("-sent_at")
            .first
        )()

        if latest_log:
            return await sync_to_async(render)(
                request,
                "api/send_result.html",
                {
                    "status": "info",
                    "message": f"Анекс №{annex.annex_number} по заявка №{annex.request.request_number} вече е подписан успешно и не може да бъде изпращан повторно.",
                },
            )

        # Ако неуспешен или няма лог – иска потвърждение
        if annex.is_sent and not request.GET.get("confirm"):
            return await sync_to_async(render)(
                request,
                "api/confirm_resend.html",
                {
                    "annex": annex,
                    "sent_at": annex.sent_at,
                    "send_attempts": annex.send_attempts,
                },
            )

        # зареждане и изпращане на файла
        file_path = os.path.join(settings.MEDIA_ROOT, annex.file_path.name)
        try:
            with open(file_path, "rb") as f:
                file_bytes = await sync_to_async(f.read)()
            file_content = base64.b64encode(file_bytes).decode("utf-8")
        except FileNotFoundError:
            return await sync_to_async(render)(
                request,
                "api/send_result.html",
                {"status": "error", "message": "Файлът не е намерен."},
            )

        payload = {
            "annex_number": annex.annex_number,
            "file_base64": file_content,
        }

        try:
            data = await sync_to_async(mock_sign_annex)(
                annex.annex_number, file_content
            )
            status_result = data.get("status", "error")
            message = data.get("message", "Няма съобщение.")
            is_success = status_result == "success"

            # Промяна на статус на заявката, ако е успешно
            if is_success and annex.request.status != "Подписан":
                req = annex.request
                req.status = "Подписан"
                req.signing_date = now()
                await sync_to_async(req.save)()

        except Exception as e:
            status_result = "error"
            message = str(e)
            is_success = False

        # Запис в SignatureLog
        await sync_to_async(SignatureLog.objects.create)(
            user=request.user,
            annex_number=annex.annex_number,
            file_sent=annex.file_path,
            status=status_result,
            response_message=message,
            is_signed_successfully=is_success,
            request=annex.request,
        )

        # Обновяване на `GeneratedAnnex`
        annex.is_sent = True
        annex.sent_at = now()
        annex.send_attempts += 1
        await sync_to_async(annex.save)()

        # Лог в SystemLog
        await sync_to_async(SystemLog.objects.create)(
            user=request.user,
            action=ActionType.CREATE,
            model_name="AnnexSignature",
            object_id=annex.annex_number,
            description=f"Подписване: {status_result.upper()} – {message}",
        )

        return await sync_to_async(render)(
            request,
            "api/send_result.html",
            {"status": status_result, "message": message},
        )
