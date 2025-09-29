document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('discountModal');
    const selectBtn = document.getElementById('selectDiscountsBtn');
    const saveBtn = document.getElementById('saveDiscounts');
    const closeBtn = document.querySelector('.modal .close');
    const hiddenField = document.querySelector('input[name="available_discounts"]');
    const selectedCountSpan = document.getElementById('selectedDiscountCount');

    function updateSelectedCount() {
        const checked = document.querySelectorAll('.discount-checkbox:checked');
        selectedCountSpan.textContent = checked.length;
    }

    selectBtn.addEventListener('click', function() {
        modal.classList.add('show');
    });

    function closeModal() {
        modal.classList.remove('show');
    }

    closeBtn.addEventListener('click', closeModal);
    
    saveBtn.addEventListener('click', function() {
        const checked = document.querySelectorAll('.discount-checkbox:checked');
        const selectedIds = Array.from(checked).map(cb => cb.value);
        hiddenField.value = selectedIds.join(',');
        updateSelectedCount();
        closeModal();
    });

    // Close modal if clicked outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Initialize selected count
    updateSelectedCount();
});