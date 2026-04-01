document.addEventListener('DOMContentLoaded', function() {
    // Randomize filmstrip photo order, then reset scroll to start
    const photoScroll = document.querySelector('.photo-scroll');
    if (photoScroll) {
        const items = [...photoScroll.children];
        for (let i = items.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            photoScroll.appendChild(items[j]);
            items[j] = items[i];
        }
        photoScroll.scrollLeft = 0;
    }

    // Language toggle
    const langBtns = document.querySelectorAll('.lang-btn');
    langBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            langBtns.forEach(b => b.classList.remove('is-active'));
            this.classList.add('is-active');
            const lang = this.dataset.lang;
            document.body.classList.toggle('lang-cz', lang === 'cz');
        });
    });

    // Auto-detect language for tipping page
    if (document.querySelector('.tip-page')) {
        const userLang = navigator.language || navigator.userLanguage || '';
        if (userLang.startsWith('cs') || userLang.startsWith('sk')) {
            document.body.classList.add('lang-cz');
            langBtns.forEach(b => {
                b.classList.toggle('is-active', b.dataset.lang === 'cz');
            });
        }
    }

    // Expandable tip method panels
    document.querySelectorAll('.tip-method[data-expand]').forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.dataset.expand;
            const detail = document.getElementById(targetId);
            if (!detail) return;

            // Close other open panels
            document.querySelectorAll('.tip-detail.is-open').forEach(d => {
                if (d.id !== targetId) d.classList.remove('is-open');
            });

            detail.classList.toggle('is-open');
            const arrow = this.querySelector('.method-arrow i');
            if (arrow) {
                arrow.classList.toggle('fa-angle-down', !detail.classList.contains('is-open'));
                arrow.classList.toggle('fa-angle-up', detail.classList.contains('is-open'));
            }
        });
    });

    // Copy to clipboard
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const target = this.closest('.detail-value').querySelector('.copy-target');
            if (!target) return;
            const text = target.textContent.trim();

            navigator.clipboard.writeText(text).then(() => {
                const icon = this.querySelector('i');
                icon.classList.remove('fa-clipboard');
                icon.classList.add('fa-check');
                this.classList.add('copied');
                setTimeout(() => {
                    icon.classList.remove('fa-check');
                    icon.classList.add('fa-clipboard');
                    this.classList.remove('copied');
                }, 2000);
            });
        });
    });

    // Lightbox for gallery items and filmstrip
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
        const lightboxImg = lightbox.querySelector('img');

        // Gallery page items (anchor tags)
        document.querySelectorAll('.gallery-item').forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                lightboxImg.src = this.href;
                lightboxImg.alt = this.querySelector('img').alt;
                lightbox.classList.add('is-open');
            });
        });

        // Filmstrip items (divs with img inside)
        document.querySelectorAll('.photo-scroll-item').forEach(item => {
            item.style.cursor = 'pointer';
            item.addEventListener('click', function() {
                const img = this.querySelector('img');
                if (!img) return;
                lightboxImg.src = img.src;
                lightboxImg.alt = img.alt;
                lightbox.classList.add('is-open');
            });
        });

        lightbox.addEventListener('click', function() {
            this.classList.remove('is-open');
            lightboxImg.src = '';
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && lightbox.classList.contains('is-open')) {
                lightbox.classList.remove('is-open');
                lightboxImg.src = '';
            }
        });
    }
});
