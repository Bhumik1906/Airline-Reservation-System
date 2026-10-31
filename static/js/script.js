/**
 * SkyBook Airlines - Client-Side JavaScript
 * Simple, clean, and beginner-friendly scripts for interactivity and validation.
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Seat Selection Logic (Booking Page)
    initSeatSelection();

    // 2. Flight Search Form Validations
    initSearchValidation();

    // 3. Auto-dismiss alerts after 5 seconds
    initAutoDismissAlerts();
});

/**
 * Handles interactive seat selection on the booking page.
 */
function initSeatSelection() {
    const seatButtons = document.querySelectorAll('.seat-btn:not(.booked)');
    const seatInput = document.getElementById('selectedSeatInput');
    const seatDisplay = document.getElementById('selectedSeatDisplay');
    const confirmBtn = document.getElementById('confirmBookingBtn');

    if (!seatButtons.length || !seatInput) return;

    seatButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Remove selection from previous seat
            seatButtons.forEach(btn => btn.classList.remove('selected'));

            // Select clicked seat
            this.classList.add('selected');
            const seatCode = this.getAttribute('data-seat');

            // Update input and display text
            seatInput.value = seatCode;
            if (seatDisplay) {
                seatDisplay.textContent = seatCode;
                seatDisplay.classList.remove('text-muted');
                seatDisplay.classList.add('text-primary', 'fw-bold');
            }

            // Enable confirmation button
            if (confirmBtn) {
                confirmBtn.removeAttribute('disabled');
            }
        });
    });
}

/**
 * Validates that source and destination are not identical in the search form.
 */
function initSearchValidation() {
    const searchForms = document.querySelectorAll('.flight-search-form');

    searchForms.forEach(form => {
        form.addEventListener('submit', function (event) {
            const sourceSelect = form.querySelector('select[name="source"]');
            const destSelect = form.querySelector('select[name="destination"]');

            if (sourceSelect && destSelect) {
                const sourceVal = sourceSelect.value.trim().toLowerCase();
                const destVal = destSelect.value.trim().toLowerCase();

                if (sourceVal && destVal && sourceVal === destVal) {
                    event.preventDefault();
                    alert('Source and destination cannot be the same city. Please select different cities.');
                }
            }
        });
    });
}

/**
 * Auto-dismisses Bootstrap alert notifications after 5 seconds.
 */
function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alertEl => {
        setTimeout(() => {
            // Check if bootstrap is available
            if (window.bootstrap && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alertEl);
                bsAlert.close();
            } else {
                alertEl.style.transition = 'opacity 0.5s ease';
                alertEl.style.opacity = '0';
                setTimeout(() => alertEl.remove(), 500);
            }
        }, 5000);
    });
}

/**
 * Demo Helper: Quick fill for demo login credentials during viva/testing.
 */
function fillCredentials(email, password) {
    const emailField = document.getElementById('loginEmail');
    const passwordField = document.getElementById('loginPassword');
    if (emailField && passwordField) {
        emailField.value = email;
        passwordField.value = password;
    }
}
