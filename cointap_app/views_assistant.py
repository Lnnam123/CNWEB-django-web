from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
import time
from .models import UserAccount, AIConversation, AIChatMessage
from .services_ai import generate_ai_financial_response

def ai_assistant_view(request):
    """
    Giao diện Trợ lý Cố vấn Tài chính Thông minh CoinTap AI.
    Hỗ trợ đa phiên trò chuyện (Multi-session), lưu trữ lịch sử hỏi đáp và gợi ý thông minh.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    conversations = AIConversation.objects.filter(user=user).order_by('-updated_at')

    # Chọn phiên active
    session_id = request.GET.get('session')
    active_conversation = None

    if session_id:
        active_conversation = AIConversation.objects.filter(session_id=session_id, user=user).first()

    if not active_conversation and conversations.exists():
        active_conversation = conversations.first()

    messages = []
    if active_conversation:
        messages = active_conversation.messages.all().order_by('created_at')

    suggested_prompts = [
        "Tổng chi tiêu tháng này của tôi đã vượt hạn mức chưa?",
        "Sao tháng này chi tiêu của tôi lại tăng vọt so với tháng trước vậy?",
        "Mỗi ngày tôi nên tiêu tối đa bao nhiêu tiền?",
        "Mẹo cắt giảm các khoản chi vặt không cần thiết",
        "Xem chi tiết các giao dịch gần đây nhất",
    ]

    return render(request, 'cointap/assistant/chat.html', {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'messages': messages,
        'suggested_prompts': suggested_prompts,
    })


def ai_new_session_view(request):
    """
    Khởi tạo phiên hội thoại mới với CoinTap AI.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    new_session_id = f"session_{int(time.time() * 1000)}"

    conv = AIConversation.objects.create(
        session_id=new_session_id,
        user=user,
        title="Cuộc trò chuyện mới",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    # Tin nhắn mở đầu từ AI
    AIChatMessage.objects.create(
        conversation=conv,
        user=user,
        content=f"Chào {user.full_name}! Mình là Trợ lý tài chính CoinTap AI 🤖. Bạn cần mình phân tích ngân sách, tư vấn hạn mức chi tiêu hay giải đáp thắc mắc tài chính nào hôm nay?",
        is_user=False,
        created_at=timezone.now()
    )

    return redirect(f"/ai-assistant/?session={new_session_id}")


def ai_delete_session_view(request, session_id):
    """
    Xóa một phiên trò chuyện AI.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = UserAccount.objects.get(user_id=user_id)
    conv = get_object_or_404(AIConversation, session_id=session_id, user=user)
    conv.delete()

    return redirect('ai_assistant')


def ai_chat_api(request):
    """
    Endpoint AJAX nhận câu hỏi từ người dùng và trả về phản hồi thông minh của AI.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)

    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Chưa đăng nhập'}, status=401)

    user = UserAccount.objects.get(user_id=user_id)

    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
        session_id = data.get('session_id', '').strip()
    except Exception:
        return JsonResponse({'error': 'Dữ liệu không hợp lệ'}, status=400)

    if not prompt:
        return JsonResponse({'error': 'Nội dung tin nhắn trống'}, status=400)

    # Tìm hoặc tạo phiên trò chuyện
    conv = None
    if session_id:
        conv = AIConversation.objects.filter(session_id=session_id, user=user).first()

    if not conv:
        session_id = f"session_{int(time.time() * 1000)}"
        conv = AIConversation.objects.create(
            session_id=session_id,
            user=user,
            title=prompt[:60],
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
    else:
        # Cập nhật tiêu đề phiên nếu tiêu đề là mặc định
        if conv.title == "Cuộc trò chuyện mới":
            conv.title = prompt[:60]
        conv.updated_at = timezone.now()
        conv.save()

    # 1. Lưu tin nhắn của Người dùng
    user_msg = AIChatMessage.objects.create(
        conversation=conv,
        user=user,
        content=prompt,
        is_user=True,
        created_at=timezone.now()
    )

    # 2. Tạo phản hồi từ CoinTap AI
    ai_response_text = generate_ai_financial_response(prompt, user)

    # 3. Lưu tin nhắn của AI
    ai_msg = AIChatMessage.objects.create(
        conversation=conv,
        user=user,
        content=ai_response_text,
        is_user=False,
        created_at=timezone.now()
    )

    return JsonResponse({
        'status': 'success',
        'session_id': conv.session_id,
        'session_title': conv.title,
        'user_message': {
            'id': user_msg.message_id,
            'content': user_msg.content,
            'time': user_msg.created_at.strftime('%H:%M - %d/%m'),
        },
        'ai_message': {
            'id': ai_msg.message_id,
            'content': ai_msg.content,
            'time': ai_msg.created_at.strftime('%H:%M - %d/%m'),
        }
    })

