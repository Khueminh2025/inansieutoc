// static/core/js/order.js

document.addEventListener('DOMContentLoaded', function () {
  // --- 1. Lấy các phần tử cần thiết ---
  var modal = document.getElementById('orderModal');
  var openBtn = document.getElementById('openOrderModal');
  var closeBtn = document.getElementById('closeOrderModal');
  var createBtn = document.getElementById('createOrder');
  var form = document.getElementById('orderForm');

  console.log('[order.js] loaded', {
    modal,
    openBtn,
    closeBtn,
    createBtn,
    form,
  });

  // Nếu thiếu phần tử chính thì dừng
  if (!modal || !openBtn || !closeBtn || !createBtn || !form) {
    console.warn('order.js: thiếu phần tử DOM', {
      modal,
      openBtn,
      closeBtn,
      createBtn,
      form,
    });
    return;
  }

  // --- 2. Mở modal ---
openBtn.addEventListener('click', function () {
  const fields = ['shape', 'size', 'paper', 'material', 'laminate', 'quantity'];

  fields.forEach(function (field) {
    const src = document.querySelector('[name="' + field + '"]');
    const dest = form.elements[field];
    if (src && dest) {
      dest.value = src.value;
    }

    // Lấy label của select option để hiển thị
    const labelSpan = document.getElementById('modal' + field.charAt(0).toUpperCase() + field.slice(1));
   if (labelSpan && src?.options) {
  const selected = src.options[src.selectedIndex]?.text || '';
  labelSpan.textContent = selected;

  // Ẩn hoặc hiện dòng <li> tương ứng
  const row = document.getElementById('modal' + field.charAt(0).toUpperCase() + field.slice(1) + 'Row');
  if (row) {
    if (selected && selected !== '') {
      row.classList.remove('hidden');
    } else {
      row.classList.add('hidden');
    }
  }
}
  });

  // Cập nhật số lượng và thành tiền
  const unitPrice = Number(modal.dataset.servicePrice || 0);
  const quantity = Number(form.elements['quantity'].value || 1);
  document.getElementById('modalQuantity').textContent = quantity;
  document.getElementById('modalSubtotal').textContent = (unitPrice * quantity).toLocaleString() + ' đ';

  modal.classList.remove('hidden');
});

  // --- 3. Đóng modal ---
  closeBtn.addEventListener('click', function () {
    modal.classList.add('hidden');
  });

  modal.addEventListener('click', function (e) {
    if (e.target === modal) {
      modal.classList.add('hidden');
    }
  });

  // --- 4. Gửi AJAX tạo đơn ---
  createBtn.addEventListener('click', function () {
    const unitPrice = Number(modal.dataset.servicePrice || 0);
    const quantity = Number(form.elements['quantity'].value || 1);
    const totalPrice = unitPrice * quantity;

    const formData = new FormData(form);
    formData.append('total_price', totalPrice);
    formData.append('quantity', quantity);
    formData.append('service_slug', modal.dataset.serviceSlug);

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
          window.location = json.redirect_url;
        } else {
          alert(json.error || 'Lỗi tạo đơn.');
        }
      })
      .catch((err) => {
        console.error('Order AJAX error:', err);
        alert('Lỗi kết nối máy chủ.');
      });
  });
}); // ✅ ĐÓNG ĐÚNG DOMContentLoaded!
