import logging

from asgiref.sync import sync_to_async
import httpx, base64, os
from django.conf import settings
from django.shortcuts import render
from django.utils.timezone import now

from loan_requests.choices import RequestStatus
from loan_requests.models import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from annexes.models import GeneratedAnnex
from api.models import SignatureLog
from logs.models import SystemLog
from logs.choices import ActionType
import logging
import traceback


class MockSignAnnexView(APIView):
    def post(self, request, *args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.info(f">>> MOCK SIGN - REQUEST DATA: {request.data}")

        try:
            annex_number = request.data.get("annex_number")
            file_base64 = request.data.get("file_base64")

            if not annex_number or not file_base64:
                logger.warning(">>> Missing 'annex_number' or 'file_base64'")
                return Response(
                    {
                        "status": "failure",
                        "message": "Липсва 'annex_number' или 'file_base64' в заявката.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.info(f">>> Signing annex {annex_number}")
            success = True  # Hardcoded to always succeed for testing

            if success:
                return Response(
                    {
                        "status": "success",
                        "message": f"Анекс {annex_number} е подписан успешно.",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "status": "failure",
                        "message": f"Анекс {annex_number} не е подписан!",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            logger.error(">>> EXCEPTION in mock sign API:")
            logger.error(traceback.format_exc())
            return Response({
                "status": "failure",
                "message": "Internal server error in mock API.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@method_decorator(login_required, name="dispatch")
class SendGeneratedAnnexView(View):
    async def get(self, request, pk):
        logger = logging.getLogger(__name__)

        def get_annex_and_check_permission():
            annex = GeneratedAnnex.objects.select_related("request").get(pk=pk)
            if annex.request.maker != request.user and not request.user.is_superuser:
                return annex, False
            return annex, True

        annex, has_permission = await sync_to_async(get_annex_and_check_permission)()

        if not has_permission:
            return await sync_to_async(render)(request, "api/send_result.html", {
                "status": "error",
                "message": "Нямате права да изпратите този анекс за подписване.",
            })

        # Проверка за вече подписан
        latest_log = await sync_to_async(
            SignatureLog.objects.filter(
                annex_number=annex.annex_number,
                request=annex.request,
                is_signed_successfully=True,
            ).order_by("-sent_at").first
        )()

        if latest_log:
            return await sync_to_async(render)(request, "api/send_result.html", {
                "status": "info",
                "message": f"Анекс №{annex.annex_number} вече е подписан успешно.",
            })

        if annex.is_sent and not request.GET.get("confirm"):
            return await sync_to_async(render)(request, "api/confirm_resend.html", {
                "annex": annex,
                "sent_at": annex.sent_at,
                "send_attempts": annex.send_attempts,
            })

        try:
            file_path = os.path.join(settings.MEDIA_ROOT, annex.file_path.name)
            with open(file_path, "rb") as f:
                file_bytes = await sync_to_async(f.read)()
            file_content = base64.b64encode(file_bytes).decode("utf-8")
        except FileNotFoundError:
            logger.error(f"[ERROR] Файлът липсва: {annex.file_path}")
            return await sync_to_async(render)(request, "api/send_result.html", {
                "status": "error",
                "message": "Файлът не е намерен.",
            })

        payload = {
            "annex_number": annex.annex_number,
            "file_base64": file_content,
        }

        try:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(settings.SIGNING_API_URL, json=payload, timeout=30)
                    logger.info(f">>> Response status: {response.status_code}")
                    logger.info(f">>> Response content: {response.text}")
                except httpx.RequestError as e:
                    logger.error(f">>> HTTPX RequestError: {e}")
                    status_result = "error"
                    message = f"Грешка при извикване на API: {str(e)}"
                    is_success = False
                    return await sync_to_async(render)(request, "api/send_result.html", {
                        "status": status_result,
                        "message": message,
                    })

                # Now that we have a response, try to parse JSON
                try:
                    data = response.json() if response.content else {}
                    logger.info(f">>> Parsed JSON: {data}")
                    status_result = data.get("status", "error")
                    message = str(data.get("message") or "").strip()
                    is_success = status_result == "success"
                except Exception as e:
                    logger.error(f">>> JSON decode error: {str(e)}")
                    status_result = "error"
                    message = f"Грешка при обработка на отговора от API: {str(e)}"
                    is_success = False

                if not message:
                    message = "Няма съобщение от сървъра."

                if is_success:
                    current_status = await sync_to_async(
                        Request.objects.filter(pk=annex.request.pk)
                        .values_list("status", flat=True).first
                    )()
                    if current_status != RequestStatus.SIGNED:
                        logger.info(f">>> Updating status of request {annex.request.pk} to SIGNED")
                        await sync_to_async(
                            lambda: Request.objects.filter(pk=annex.request.pk)
                            .update(status=RequestStatus.SIGNED, signing_date=now())
                        )()
                else:
                    logger.warning(f"[SEND] Подписване неуспешно: status={status_result} | message={message}")
        except Exception as e:
            status_result = "error"
            message = f"Изключение при извикване на API: {str(e)}"
            is_success = False
            logger.error(f"[SEND] Exception during API call: {str(e)}")

        logger.info(f"[SEND] Logging signature and system log for annex {annex.annex_number}")

        await sync_to_async(SignatureLog.objects.create)(
            user=request.user,
            annex_number=annex.annex_number,
            file_sent=annex.file_path,
            status=status_result,
            response_message=message,
            is_signed_successfully=is_success,
            request=annex.request,
        )

        annex.is_sent = True
        annex.sent_at = now()
        annex.send_attempts += 1
        await sync_to_async(annex.save)()

        await sync_to_async(SystemLog.objects.create)(
            user=request.user,
            action=ActionType.CREATE,
            model_name="AnnexSignature",
            object_id=annex.annex_number,
            description=f"Подписване: {status_result.upper()} – {message}",
        )

        return await sync_to_async(render)(request, "api/send_result.html", {
            "status": status_result,
            "message": message,
        })




