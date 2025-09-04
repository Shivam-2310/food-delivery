/**
 * JUSTEAT - MAIN JAVASCRIPT FILE
 */

document.addEventListener('DOMContentLoaded', function() {
    // INITIALIZE TOOLTIPS
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // QUANTITY INPUT HANDLERS
    document.querySelectorAll('.quantity-control').forEach(function(control) {
        control.querySelector('.quantity-decrease').addEventListener('click', function() {
            var input = this.parentNode.querySelector('input');
            var value = parseInt(input.value);
            if (value > 1) {
                input.value = value - 1;
            }
        });
        
        control.querySelector('.quantity-increase').addEventListener('click', function() {
            var input = this.parentNode.querySelector('input');
            var value = parseInt(input.value);
            input.value = value + 1;
        });
    });
    
    // SEARCH FORM ENHANCEMENTS
    var searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            // GET EMPTY FIELDS
            var emptyFields = Array.from(searchForm.querySelectorAll('input, select')).filter(function(element) {
                return element.name && element.value === '' && element.type !== 'submit';
            });
            
            // REMOVE EMPTY FIELDS FROM SUBMISSION
            emptyFields.forEach(function(field) {
                field.disabled = true;
            });
            
            // AFTER FORM IS SUBMITTED, RE-ENABLE FIELDS
            setTimeout(function() {
                emptyFields.forEach(function(field) {
                    field.disabled = false;
                });
            }, 100);
        });
    }
    
    // CONFIRMATION DIALOGS
    document.querySelectorAll('.confirm-action').forEach(function(button) {
        button.addEventListener('click', function(event) {
            if (!confirm(this.getAttribute('data-confirm-message') || 'ARE YOU SURE YOU WANT TO PROCEED?')) {
                event.preventDefault();
            }
        });
    });
    
    // TOGGLE PASSWORD VISIBILITY
    document.querySelectorAll('.toggle-password').forEach(function(button) {
        button.addEventListener('click', function() {
            var passwordInput = document.getElementById(this.getAttribute('data-target'));
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                passwordInput.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });
    
    // FILE INPUT PREVIEW
    document.querySelectorAll('.custom-file-input').forEach(function(input) {
        input.addEventListener('change', function() {
            var preview = document.getElementById(this.getAttribute('data-preview'));
            var label = document.querySelector('label[for="' + this.id + '"]');
            
            if (this.files && this.files[0]) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
                reader.readAsDataURL(this.files[0]);
                label.innerText = this.files[0].name;
            } else {
                preview.src = '';
                preview.style.display = 'none';
                label.innerText = 'CHOOSE FILE';
            }
        });
    });
    
    // STAR RATING INTERACTION
    document.querySelectorAll('.rating-input').forEach(function(input) {
        input.addEventListener('change', function() {
            var id = this.getAttribute('id');
            var value = this.getAttribute('value');
            var ratingDisplay = document.getElementById('rating-display');
            
            if (ratingDisplay) {
                ratingDisplay.innerText = value + ' ' + (value > 1 ? 'STARS' : 'STAR');
            }
        });
    });
    
    // ADD TO CART BUTTON HANDLER FOR FEATURED ITEMS
    document.querySelectorAll('.add-to-cart').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            
            var itemId = this.getAttribute('data-item-id');
            var itemName = this.getAttribute('data-item-name');
            var itemPrice = this.getAttribute('data-item-price');
            
            if (!itemId) {
                console.error('Item ID not found');
                return;
            }
            
            // GET QUANTITY FROM THE QUANTITY INPUT (DEFAULT TO 1 IF NOT FOUND)
            var quantityInput = this.closest('.card-body').querySelector('.quantity-input');
            var quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;
            
            // REDIRECT TO ADD TO CART ROUTE
            var addToCartUrl = '/customer/add_to_cart/' + itemId + '?quantity=' + quantity;
            window.location.href = addToCartUrl;
        });
    });
});
