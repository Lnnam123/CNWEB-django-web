/**
 * CoinTap Interactive JavaScript Engine & Animation Suite
 * Tuân thủ triết lý Anthropic Frontend-Design Skill:
 * - Động lực học tinh tế, dứt khoát, không gây rối mắt.
 * - Hiệu ứng đếm số tài chính (Fintech Odometer Count-Up) mượt mà.
 * - Thanh đo ngân sách nạp động (Progress Bar Fill).
 * - Trợ lý AI với bong bóng phản hồi sinh động và điểm nhảy (Bouncing Dots).
 */

// Hàm chuẩn hóa định dạng tiền tệ Việt Nam (Ví dụ: 2543000 -> 2.543.000)
window.formatVND = (num) => {
  if (num === null || num === undefined || isNaN(num)) return '0';
  const isNegative = Number(num) < 0;
  const absInt = Math.round(Math.abs(Number(num)));
  const formatted = absInt.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return isNegative ? `-${formatted}` : formatted;
};

document.addEventListener('DOMContentLoaded', () => {
  // 1. Đồng hồ thời gian thực ở Header (Có Live Pulse Dot)
  const clockEl = document.getElementById('liveClock');
  if (clockEl) {
    const updateClock = () => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('vi-VN', { hour12: false });
      const dateStr = now.toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit' });
      clockEl.innerHTML = `<span class="live-dot"></span> <span>${dateStr} • ${timeStr}</span>`;
    };
    updateClock();
    setInterval(updateClock, 1000);
  }

  // 2. Sidebar Toggle (Thu gọn / Mở rộng Sidebar & Lưu trạng thái)
  const sidebar = document.querySelector('.app-sidebar');
  const toggleButtons = document.querySelectorAll('#sidebarToggle, #sidebarHeaderToggle, #sidebarHeaderToggleAdmin');
  const brandLogos = document.querySelectorAll('#brandLogoLink, #brandLogoLinkAdmin');
  
  if (sidebar) {
    const updateToggleIcons = (collapsed) => {
      document.querySelectorAll('#sidebarHeaderToggle .material-symbols-outlined, #sidebarHeaderToggleAdmin .material-symbols-outlined').forEach(icon => {
        icon.textContent = collapsed ? 'chevron_right' : 'chevron_left';
      });
    };

    const applySidebarState = (collapsed) => {
      if (collapsed) {
        sidebar.classList.add('collapsed');
        document.documentElement.classList.add('sidebar-is-collapsed');
      } else {
        sidebar.classList.remove('collapsed');
        document.documentElement.classList.remove('sidebar-is-collapsed');
      }
      updateToggleIcons(collapsed);
      localStorage.setItem('cointap_sidebar_collapsed', collapsed ? 'true' : 'false');
      
      // Kích hoạt redraw Chart.js sau khi transition co/dãn sidebar hoàn tất (260ms)
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
      }, 260);
    };

    // Khởi tạo trạng thái đã lưu từ localStorage
    const savedCollapsed = localStorage.getItem('cointap_sidebar_collapsed') === 'true';
    if (savedCollapsed && window.innerWidth > 768) {
      applySidebarState(true);
    } else {
      updateToggleIcons(false);
    }

    // Tạo lớp phủ mờ (Backdrop) khi mở menu trên di động
    let backdrop = document.querySelector('.sidebar-backdrop');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.className = 'sidebar-backdrop';
      document.body.appendChild(backdrop);
    }

    const closeMobileSidebar = () => {
      if (sidebar && sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        backdrop.classList.remove('active');
        document.body.classList.remove('sidebar-open-mobile');
      }
    };

    backdrop.addEventListener('click', closeMobileSidebar);

    // Gán sự kiện click cho toàn bộ nút toggle (ở Topbar và ở Sidebar Header)
    toggleButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (window.innerWidth <= 768) {
          const willOpen = !sidebar.classList.contains('open');
          sidebar.classList.toggle('open', willOpen);
          backdrop.classList.toggle('active', willOpen);
          document.body.classList.toggle('sidebar-open-mobile', willOpen);
        } else {
          const isCurrentlyCollapsed = sidebar.classList.contains('collapsed');
          applySidebarState(!isCurrentlyCollapsed);
        }
      });
    });

    // Tự động đóng sidebar mobile khi bấm vào link chuyển trang
    sidebar.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
          closeMobileSidebar();
        }
      });
    });

    // Khi sidebar đang thu gọn, click vào logo sẽ mở rộng lại menu (giống web_admin)
    brandLogos.forEach(logoLink => {
      logoLink.addEventListener('click', (e) => {
        if (sidebar.classList.contains('collapsed') && window.innerWidth > 768) {
          e.preventDefault();
          applySidebarState(false);
        }
      });
    });
  }

  // 3. Tự động đóng Toast messages sau 4s
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(toast => {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(60px) scale(0.9)';
      toast.style.transition = 'all 0.35s ease';
      setTimeout(() => toast.remove(), 350);
    }, 4000);
  });

  // 4. Modal Helpers (Mở và Đóng Modal với hiệu ứng Pop)
  window.openModal = (modalId) => {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeModal = (modalId) => {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  };

  // Đóng modal khi click vào nền mờ (Backdrop)
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  });

  // 5. Định dạng số tiền khi nhập vào input (Auto thousand separator with dots)
  document.querySelectorAll('.input-currency').forEach(input => {
    input.addEventListener('input', (e) => {
      let val = e.target.value.replace(/[^0-9]/g, '');
      if (val) {
        e.target.value = window.formatVND(parseInt(val, 10));
      } else {
        e.target.value = '';
      }
    });
  });

  // 6. Hiệu ứng đếm số tài chính Odometer (Fintech Counter-Up Animation)
  const animateNumberCounters = () => {
    const counterElements = document.querySelectorAll('.pulse-val, .count-up');
    counterElements.forEach(el => {
      const text = el.innerText || el.textContent;
      // Tìm số nguyên hoặc số thập phân trong chuỗi
      const match = text.match(/([+-]?)([0-9.,]+)/);
      if (!match) return;

      const prefix = match[1] || '';
      // Loại bỏ dấu chấm, phẩy phân cách hàng nghìn
      const rawNumber = parseFloat(match[2].replace(/\./g, '').replace(/,/g, ''));
      if (isNaN(rawNumber) || rawNumber === 0) return;

      const suffix = text.includes('₫') ? ' ₫' : (text.includes('%') ? '%' : '');
      const duration = 1000; // 1 giây
      const startTime = performance.now();

      const easeOutQuart = (t) => 1 - Math.pow(1 - t, 4);

      const updateCounter = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentVal = Math.round(easeOutQuart(progress) * rawNumber);

        el.innerHTML = `${prefix}${window.formatVND(currentVal)}<span style="font-size: 1.1rem; color: var(--text-muted); font-weight: 500;">${suffix}</span>`;

        if (progress < 1) {
          requestAnimationFrame(updateCounter);
        } else {
          el.innerHTML = `${prefix}${window.formatVND(rawNumber)}<span style="font-size: 1.1rem; color: var(--text-muted); font-weight: 500;">${suffix}</span>`;
        }
      };

      requestAnimationFrame(updateCounter);
    });
  };

  // Kích hoạt đếm số khi trang tải xong
  animateNumberCounters();

  // 7. Hiệu ứng nạp thanh đo tiến độ ngân sách (Progress Meter Fill Transition)
  const animateBudgetMeters = () => {
    const meterFills = document.querySelectorAll('.meter-fill');
    meterFills.forEach(fill => {
      const targetWidth = fill.style.width;
      fill.style.width = '0%';
      setTimeout(() => {
        fill.style.width = targetWidth;
      }, 100);
    });
  };
  animateBudgetMeters();

  // 8. Trợ lý AI Chat (Gửi câu hỏi, bong bóng nảy và Bouncing Dots Indicator)
  const chatForm = document.getElementById('aiChatForm');
  const chatMessagesContainer = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sessionIdInput = document.getElementById('chatSessionId');

  if (chatForm && chatMessagesContainer && chatInput) {
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const prompt = chatInput.value.trim();
      if (!prompt) return;

      const sessionId = sessionIdInput ? sessionIdInput.value : '';

      // Hiển thị tin nhắn của User với hiệu ứng nảy nhẹ
      const userBubble = document.createElement('div');
      userBubble.className = 'chat-bubble user';
      userBubble.style.animation = 'fadeInUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
      userBubble.textContent = prompt;
      chatMessagesContainer.appendChild(userBubble);
      chatInput.value = '';
      chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

      // Hiển thị bong bóng typing indicator của AI kèm hiệu ứng ba chấm động (Bouncing Dots)
      const typingBubble = document.createElement('div');
      typingBubble.className = 'chat-bubble ai';
      typingBubble.style.animation = 'fadeInUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
      typingBubble.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem; color: var(--text-secondary);">
          <span>CoinTap AI đang phân tích dữ liệu</span>
          <div class="typing-dots">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
        </div>
      `;
      chatMessagesContainer.appendChild(typingBubble);
      chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

      try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch('/api/ai-chat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({
            prompt: prompt,
            session_id: sessionId
          })
        });

        const data = await response.json();
        if (data.status === 'success') {
          let formattedContent = data.ai_message.content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n• /g, '<br>• ')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');

          typingBubble.innerHTML = formattedContent;

          if (sessionIdInput && !sessionIdInput.value) {
            sessionIdInput.value = data.session_id;
            window.history.pushState({}, '', `/ai-assistant/?session=${data.session_id}`);
          }
        } else {
          typingBubble.innerHTML = `<span style="color:#e11d48;">Lỗi: ${data.error || 'Không thể tạo câu trả lời'}</span>`;
        }
      } catch (err) {
        typingBubble.innerHTML = '<span style="color:#e11d48;">Lỗi kết nối tới máy chủ. Vui lòng thử lại.</span>';
      }

      chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    });

    document.querySelectorAll('.prompt-suggestion-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        chatInput.value = pill.getAttribute('data-prompt');
        chatForm.dispatchEvent(new Event('submit'));
      });
    });
  }
});

// Hàm hỗ trợ ẩn/hiện mật khẩu (Show/Hide Password)
window.togglePasswordVisibility = function(btn) {
  if (!btn) return;
  const container = btn.closest('.password-input-group') || btn.parentElement;
  if (!container) return;
  const input = container.querySelector('input');
  const icon = btn.querySelector('.material-symbols-outlined') || btn.querySelector('span');
  if (!input) return;

  if (input.type === 'password') {
    input.type = 'text';
    if (icon) icon.textContent = 'visibility_off';
    btn.setAttribute('aria-label', 'Ẩn mật khẩu');
    btn.setAttribute('title', 'Ẩn mật khẩu');
  } else {
    input.type = 'password';
    if (icon) icon.textContent = 'visibility';
    btn.setAttribute('aria-label', 'Hiện mật khẩu');
    btn.setAttribute('title', 'Hiện mật khẩu');
  }
};
