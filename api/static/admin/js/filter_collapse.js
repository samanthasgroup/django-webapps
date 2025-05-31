document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#changelist-filter details[open]').forEach(function(el) {
        el.removeAttribute('open');
    });
});
