// Phone number formatting for admin panel
document.addEventListener('DOMContentLoaded', function() {
    // Find all phone format fields
    const phoneFields = document.querySelectorAll('.phone-format');
    
    phoneFields.forEach(function(field) {
        field.addEventListener('input', function() {
            // Remove all non-digits
            let value = this.value.replace(/\D/g, '');
            
            // Limit to 10 digits
            if (value.length > 10) {
                value = value.slice(0, 10);
            }
            
            // Format as (XXX) XXX-XXXX
            if (value.length >= 6) {
                value = `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
            } else if (value.length >= 3) {
                value = `(${value.slice(0, 3)}) ${value.slice(3)}`;
            }
            
            // Update the field value
            this.value = value;
        });
        
        // Also format on paste
        field.addEventListener('paste', function(e) {
            // Small delay to let paste complete
            setTimeout(() => {
                this.dispatchEvent(new Event('input'));
            }, 10);
        });
    });
});
