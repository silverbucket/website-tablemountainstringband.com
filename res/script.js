document.addEventListener('DOMContentLoaded', function() {
    // click to copy
    const copyText = document.getElementById("copy-text");
    if (copyText) {
        copyText.addEventListener("click", (e) => {
            e.currentTarget.select();
            document.execCommand("copy");
            const textIsCopied = document.getElementById("text-is-copied");
            textIsCopied.classList.remove('is-hidden');
        });
    }

    // card toggle
    const cardToggles = document.getElementsByClassName('card-toggle');
    if (cardToggles) {
        for (let i = 0; i < cardToggles.length; i++) {
            cardToggles[i].addEventListener('click', (e) => {
                e.currentTarget.parentElement.childNodes[3].classList.toggle('is-hidden-mobile');
            });
        }
    }

    // Get all language toggle elements
    const langToggles = document.querySelectorAll('.lang-toggle');
    if (langToggles) {
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
    }
}); 

document.addEventListener('onbeforeunload', function() {
    fetch('/logout', {
        method: 'GET',
    });
});