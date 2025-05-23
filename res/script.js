document.addEventListener('DOMContentLoaded', function() {
    // Get all language toggle elements
    const langToggles = document.querySelectorAll('.lang-toggle');
    
    // Add click event listeners to each toggle
    langToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            // Remove active class from all toggles
            langToggles.forEach(t => t.classList.remove('is-active'));
            
            // Add active class to clicked toggle
            this.classList.add('is-active');
            
            // Get the language from the class (en or cz)
            const lang = this.classList.contains('lang-en') ? 'en' : 'cz';
            
            // Show/hide content based on language
            document.querySelectorAll('.lang-en-content').forEach(el => {
                el.classList.toggle('is-hidden', lang !== 'en');
            });
            
            document.querySelectorAll('.lang-cz-content').forEach(el => {
                el.classList.toggle('is-hidden', lang !== 'cz');
            });
        });
    });
}); 