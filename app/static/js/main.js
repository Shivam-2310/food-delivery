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
    
    // ADD TO CART BUTTON HANDLER (AJAX)
    function updateCartBadge(count) {
        var badge = document.getElementById('cart-badge');
        if (!badge) return;
        if (count && count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.textContent = '';
            badge.style.display = 'none';
        }
    }

    function showInlineAlert(container, message, type) {
        try {
            var alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-' + (type || 'success') + ' alert-dismissible fade show mt-2';
            alertDiv.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
            container.appendChild(alertDiv);
            setTimeout(function(){
                var bsAlert = new bootstrap.Alert(alertDiv);
                bsAlert.close();
            }, 3000);
        } catch (e) {
            console.log(message);
        }
    }

    document.querySelectorAll('.add-to-cart').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();

            var itemId = this.getAttribute('data-item-id');
            if (!itemId) return;

            var quantityInput = (this.closest('.card-body') || this.closest('.card')).querySelector('.quantity-input');
            var quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;

            var url = '/customer/add_to_cart/' + encodeURIComponent(itemId) + '?quantity=' + encodeURIComponent(quantity);

            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            }).then(function(res){
                return res.json().then(function(data){
                    return { status: res.status, data: data };
                });
            }).then(function(result){
                if (result.status >= 200 && result.status < 300 && result.data && result.data.ok) {
                    updateCartBadge(result.data.cart_count);
                    var container = button.closest('.card-body') || document.body;
                    showInlineAlert(container, result.data.message, 'success');
                } else {
                    var message = (result && result.data && result.data.message) ? result.data.message : 'FAILED TO ADD ITEM TO CART.';
                    var container = button.closest('.card-body') || document.body;
                    showInlineAlert(container, message, 'warning');
                }
            }).catch(function(err){
                var container = button.closest('.card-body') || document.body;
                showInlineAlert(container, 'NETWORK ERROR. PLEASE TRY AGAIN.', 'danger');
            });
        });
    });
});
