document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('orderModal');
  const openBtn = document.getElementById('openOrderModal');
  const closeBtn = document.getElementById('closeOrderModal');
  const createBtn = document.getElementById('createOrder');
  const form = document.getElementById('orderForm');

  console.log('[order.js] loaded', {
    modal,
    openBtn,
    closeBtn,
    createBtn,
    form,
  });

  if (!modal || !openBtn || !closeBtn || !createBtn || !form) {
    console.warn('order.js: thiếu phần tử DOM');
    return;
  }

  // --- 1. Mở modal ---
  openBtn.addEventListener('click', function () {
    const fields = ['shape', 'size', 'paper', 'material', 'laminate', 'quantity'];

    fields.forEach(function (field) {
      const src = document.querySelector('[name="' + field + '"]');
      const dest = form.elements[field];
      if (src && dest) {
        dest.value = src.value;
      }

      const labelSpan = document.getElementById('modal' + field.charAt(0).toUpperCase() + field.slice(1));
      if (labelSpan && src?.options) {
        const selected = src.options[src.selectedIndex]?.text || '';
        labelSpan.textContent = selected;

        const row = document.getElementById('modal' + field.charAt(0).toUpperCase() + field.slice(1) + 'Row');
        if (row) {
          row.classList.toggle('hidden', !selected);
        }
      }
    });

    // Hiển thị số lượng và thành tiền
    const unitPrice = Number(modal.dataset.servicePrice || 0);
    const quantity = Number(form.elements['quantity'].value || 1);
    document.getElementById('modalQuantity').textContent = quantity;
    document.getElementById('modalSubtotal').textContent = (unitPrice * quantity).toLocaleString() + ' đ';

    modal.classList.remove('hidden');
  });

  // --- 2. Đóng modal ---
  closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.add('hidden');
  });

  // --- 3. Gửi AJAX tạo đơn ---
  createBtn.addEventListener('click', function () {
    const unitPrice = Number(modal.dataset.servicePrice || 0);
    const quantity = Number(form.elements['quantity'].value || 1);
    const totalPrice = unitPrice * quantity;

    const formData = new FormData(form);
    formData.append('total_price', totalPrice);
    formData.append('quantity', quantity);

    // Thêm thông tin dịch vụ
    formData.append('service_id', modal.dataset.serviceId);

    fetch(`/orders/create/${modal.dataset.serviceId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': form.elements['csrfmiddlewaretoken'].value,
      },
      body: formData,
    })
      .then((r) => r.json())
      .then((json) => {
        if (json.success) {
          window.location.href = json.redirect_url;
        } else {
          alert(json.error || 'Đã xảy ra lỗi khi tạo đơn.');
        }
      })
      .catch((err) => {
        console.error('Order AJAX error:', err);
        alert('Lỗi kết nối máy chủ.');
      });
  });
});
