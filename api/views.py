from asgiref.sync import sync_to_async
import httpx, base64, os
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from annexes.models import GeneratedAnnex
from logs.models import SystemLog
from logs.choices import ActionType


class MockSignAnnexView(APIView):
    def post(self, request, *args, **kwargs):
        # симулиране случайно подписване
        success = random.choice([True, False])
        annex_number = request.data.get('annex_number', 'unknown')

        if success:
            return Response({
                'status': 'success',
                'message': f'Annex {annex_number} signed successfully'
            })
        else:
            return Response({
                'status': 'failure',
                'message': 'Signature failed'
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class SendGeneratedAnnexView(View):
    async def get(self, request, pk):
        annex = await sync_to_async(GeneratedAnnex.objects.select_related('request').get)(pk=pk)
        file_path = os.path.join(settings.MEDIA_ROOT, annex.file_path.name)

        try:
            with open(file_path, 'rb') as f:
                file_bytes = await sync_to_async(f.read)()
            file_content = base64.b64encode(file_bytes).decode('utf-8')
        except FileNotFoundError:
            return await sync_to_async(render)(request, 'api/send_result.html', {
                'status': 'error',
                'message': 'Файлът не е намерен.'
            })

        payload = {
            'annex_number': annex.annex_number,
            'file_base64': file_content,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post('http://localhost:8000/api/mock-sign/', json=payload)
                data = response.json()
                status_result = data.get('status')
                message = data.get('message')
        except Exception as e:
            status_result = 'error'
            message = str(e)

        # запис в лог файла
        await sync_to_async(SystemLog.objects.create)(
            user=request.user,
            action=ActionType.CREATE,
            model_name='AnnexSignature',
            object_id=annex.annex_number,
            description=f"Подписване: {status_result.upper()} – {message}"
        )

        return await sync_to_async(render)(request, 'api/send_result.html', {
            'status': status_result,
            'message': message
        })



