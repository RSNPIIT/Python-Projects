document.addEventListener('DOMContentLoaded', () => {
    // 1. Sleek Input Focus Effects
    const formInputs = document.querySelectorAll('input[type="text"], input[type="password"], input[type="file"]');
    
    formInputs.forEach(input => {
        // Light up the input parent form container slightly on focus
        input.addEventListener('focus', () => {
            input.closest('form').style.borderColor = 'var(--primary)';
            input.closest('form').style.boxShadow = '0 0 15px rgba(99, 102, 241, 0.1)';
        });

        input.addEventListener('blur', () => {
            input.closest('form').style.borderColor = 'rgba(255, 255, 255, 0.05)';
            input.closest('form').style.boxShadow = 'none';
        });
    });

    // 2. Animated Loading Feedback on Button Clicks
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('input[type="submit"]');
            
            // Check text / password fields for the login form before submitting
            if (form.getAttribute('action').includes('login')) {
                const username = form.querySelector('input[name="username"]').value.trim();
                const password = form.querySelector('input[name="password"]').value.trim();
                
                if (!username || !password) {
                    e.preventDefault();
                    alert('Please fill in both fields before trying to break the matrix.');
                    return;
                }
            }

            // Check file inputs for upload forms before submitting
            if (form.getAttribute('enctype') === 'multipart/form-data') {
                const fileInput = form.querySelector('input[type="file"]');
                if (!fileInput.files.length) {
                    e.preventDefault();
                    alert('Please select a valid file to upload first!');
                    return;
                }
            }

            // Visual feedback: Change button state to show processing
            if (submitBtn) {
                const originalValue = submitBtn.value;
                submitBtn.disabled = true;
                submitBtn.value = "PROCESSING...";
                submitBtn.style.background = 'var(--accent)';
                submitBtn.style.cursor = 'not-allowed';
                
                // Fallback to re-enable button if something prevents navigation
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.value = originalValue;
                    submitBtn.style.background = 'var(--primary)';
                    submitBtn.style.cursor = 'pointer';
                }, 10000);
            }
        });
    });

    // 3. Dynamic File Input Visual feedback
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', () => {
            if (input.files.length > 0) {
                const fileName = input.files[0].name;
                // Highlight input background to indicate a staged file
                input.style.borderColor = 'var(--accent)';
                input.style.background = 'rgba(56, 189, 248, 0.05)';
                console.log(`File staged for upload: ${fileName}`);
            }
        });
    });
});