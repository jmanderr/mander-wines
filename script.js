/* ===========================
   Mander Wines — Script
   =========================== */

document.addEventListener('DOMContentLoaded', () => {

    // --- Shared flag to suppress exit popup (set by age denial) ---
    let suppressExitPopup = false;

    // --- Page Loader ---
    const loader = document.getElementById('page-loader');
    if (loader) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                loader.classList.add('loaded');
            }, 600);
        });
    }

    // --- Age Gate ---
    const ageGate = document.getElementById('age-gate');
    if (ageGate) {
        const verified = sessionStorage.getItem('mander-age-verified');
        if (verified === 'true') {
            ageGate.classList.add('hidden');
        } else {
            document.body.style.overflow = 'hidden';
        }
    }

    const ageYes = document.getElementById('age-yes');
    const ageNo = document.getElementById('age-no');
    const ageDenied = document.getElementById('age-denied');
    const ageContent = document.getElementById('age-content');

    if (ageYes) {
        ageYes.addEventListener('click', () => {
            sessionStorage.setItem('mander-age-verified', 'true');
            ageGate.classList.add('hidden');
            document.body.style.overflow = '';
        });
    }

    if (ageNo) {
        ageNo.addEventListener('click', () => {
            if (ageContent) ageContent.style.display = 'none';
            if (ageDenied) ageDenied.classList.add('show');
            suppressExitPopup = true;
            sessionStorage.setItem('mander-exit-shown', 'true');
        });
    }

    // --- Navbar scroll effect ---
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 60);
        });
    }

    // --- Mobile menu ---
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    const mobileNav = document.querySelector('.mobile-nav');

    if (mobileBtn) {
        mobileBtn.addEventListener('click', () => {
            mobileBtn.classList.toggle('active');
            mobileNav.classList.toggle('open');
        });

        document.querySelectorAll('.mobile-nav a').forEach(link => {
            link.addEventListener('click', () => {
                mobileBtn.classList.remove('active');
                mobileNav.classList.remove('open');
            });
        });
    }

    // --- Scroll animations ---
    const animatedEls = document.querySelectorAll('[data-animate]');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

    animatedEls.forEach(el => observer.observe(el));

    // --- Lazy image fade-in ---
    document.querySelectorAll('img[loading="lazy"]').forEach(img => {
        if (img.complete) { img.classList.add('loaded'); }
        else { img.addEventListener('load', () => img.classList.add('loaded')); }
    });

    // --- Success Modal ---
    function showSuccessModal(heading, message) {
        let modal = document.getElementById('successModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'successModal';
            modal.className = 'success-modal';
            document.body.appendChild(modal);
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('show');
                    document.body.style.overflow = '';
                    // Clean URL
                    history.replaceState(null, '', window.location.pathname);
                }
            });
        }
        modal.innerHTML = `
            <div class="success-modal-card">
                <div class="success-modal-icon">&#10003;</div>
                <h2>${heading}</h2>
                <p>${message}</p>
                <p style="font-size: 0.85em; opacity: 0.75; margin-top: 12px;">Please check your junk or spam folder if you don't see our email.</p>
                <p class="success-modal-signature"><em>&mdash; The Mander Wines Team</em></p>
                <button class="btn btn-gold success-modal-close">Close</button>
            </div>
        `;
        modal.querySelector('.success-modal-close').addEventListener('click', () => {
            modal.classList.remove('show');
            document.body.style.overflow = '';
            history.replaceState(null, '', window.location.pathname);
        });
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    // --- Brevo: Add contact via form endpoint (no API key needed) ---
    const BREVO_FORM_URL = 'https://84a926b8.sibforms.com/serve/MUIFANhgfdhQosz6DR5X1fDq9ZXNhHrhu4XC6hmox5_TrfpuXFQgs6PuGGZjN0Ol3hD6ug2J6mF7HNdSwuaXH0XtWYsONB5AEN6l5D4yjylE26-fBkSgtwccmrrg3nftczhMk8jUo4LYbi5jfJeFBk8_hGLnG9QVJu8yWOCXvvNtjz3zA8QMyvaFlnXS9WulmWuOEiPi18P8VIHYjg==';
    const BREVO_CONTACT_GENERAL_URL = 'https://84a926b8.sibforms.com/serve/MUIFAK0xSajTBAOiErpt4km8f71QjgbAJjoHQeekgmP7TZ0crcJcK15DArF2INIKZbHnCHtrJbC3XFi37hkg6NFfs2uKQWkxwiMvVUOX1QMnz6GuZNQKxMEIFFXazDJa7qQkSJRM5YGtUGEgCV-koovPogikqXnmE3XJE79qE78zgk-TdSal9FQ-RgHK-7WkhMxp4-935F3XyrKiqA==';
    const BREVO_CONTACT_WHOLESALE_URL = 'https://84a926b8.sibforms.com/serve/MUIFANokkPnUToJUAmQLX2kOBDckvZK3XDxXBA__K3y2oyL4malKDrFalxu2PqP86nK4qjLZxqWhfKqumb4iTQcqbY25LVLONEKubjgBUluXMuZ2J7f4mVDGDE0UML7u-SuPN9JMgQDnUsz187ogdZsrn4eZi0-YKSV0YalHqDD6EDnoaOn4S46oZuCF41lO3MQAH9oQYVUHup6ffA==';

    function addToBrevo(email, name, formUrl) {
        const formData = new URLSearchParams();
        formData.append('EMAIL', email);
        formData.append('FIRSTNAME', name || '');
        formData.append('email_address_check', '');
        formData.append('locale', 'en');
        fetch(formUrl || BREVO_FORM_URL, {
            method: 'POST',
            body: formData,
            mode: 'no-cors'
        });
    }

    // --- Journey signup form ---
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(signupForm);
            // Send to FormSubmit for your notification
            fetch(signupForm.action, { method: 'POST', body: formData });
            // Add to Brevo mailing list (auto-reply handled by Brevo Automation)
            addToBrevo(formData.get('email'), formData.get('name'));
            signupForm.reset();
            showSuccessModal('Welcome to the Mander Family', 'Thank you for joining the Mander Wines circle. You\'re now on our list for first access to new releases, cellar updates, and news on our upcoming brick-and-mortar home.');
        });
    }

    // --- Newsletter form ---
    const nlForm = document.getElementById('newsletter-form');
    if (nlForm) {
        nlForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(nlForm);
            // Send to FormSubmit for your notification
            fetch(nlForm.action, { method: 'POST', body: formData });
            // Add to Brevo mailing list (auto-reply handled by Brevo Automation)
            addToBrevo(formData.get('email'), '');
            nlForm.reset();
            showSuccessModal('Welcome to the Mander Family', 'Thank you for joining the Mander Wines circle. You\'re now on our list for first access to new releases, cellar updates, and news on our upcoming brick-and-mortar home.');
        });
    }

    // --- Contact form ---
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(contactForm);
            const subject = formData.get('subject');
            // Send to FormSubmit for your notification
            fetch(contactForm.action, { method: 'POST', body: formData });
            // Add to Brevo list for auto-reply (wholesale vs general)
            const brevoUrl = subject === 'Wholesale & Trade' ? BREVO_CONTACT_WHOLESALE_URL : BREVO_CONTACT_GENERAL_URL;
            addToBrevo(formData.get('email'), formData.get('name'), brevoUrl);
            contactForm.reset();
            showSuccessModal('Thank You for Reaching Out', 'We\'ve received your message and will be in touch within 24\u201348 hours.');
        });
    }

    // --- Scroll to Top Button ---
    const scrollBtn = document.createElement('button');
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.innerHTML = '&#8593;';
    scrollBtn.setAttribute('aria-label', 'Scroll to top');
    document.body.appendChild(scrollBtn);

    window.addEventListener('scroll', () => {
        scrollBtn.classList.toggle('visible', window.scrollY > 400);
    });

    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // --- Cookie Consent Banner ---
    if (!localStorage.getItem('mander-cookies-accepted')) {
        const banner = document.createElement('div');
        banner.className = 'cookie-banner';
        banner.innerHTML = `
            <div class="cookie-banner-inner">
                <p>We use cookies to enhance your experience and analyze site traffic. By continuing to use this site, you consent to our use of cookies in accordance with our <a href="privacy.html">Privacy Policy</a>.</p>
                <button class="btn btn-gold cookie-accept">Accept</button>
            </div>
        `;
        document.body.appendChild(banner);
        setTimeout(() => banner.classList.add('show'), 500);

        banner.querySelector('.cookie-accept').addEventListener('click', () => {
            localStorage.setItem('mander-cookies-accepted', 'true');
            banner.classList.remove('show');
            setTimeout(() => banner.remove(), 400);
        });
    }

    // --- Exit Intent Popup ---
    if (!sessionStorage.getItem('mander-exit-shown')) {
        let exitTriggered = false;

        document.addEventListener('mouseout', (e) => {
            if (exitTriggered || suppressExitPopup) return;
            if (e.clientY < 5 && e.relatedTarget === null) {
                exitTriggered = true;
                sessionStorage.setItem('mander-exit-shown', 'true');

                let exitModal = document.createElement('div');
                exitModal.className = 'exit-modal';
                exitModal.innerHTML = `
                    <div class="exit-modal-card">
                        <button class="exit-modal-close" aria-label="Close">&times;</button>
                        <span class="label" style="color: var(--gold); margin-bottom: 12px;">Before You Go</span>
                        <h2>Don't Miss a Pour</h2>
                        <p>Join our inner circle for first access to limited releases, cellar updates, and news on our upcoming brick-and-mortar home.</p>
                        <form class="exit-form" id="exit-form" action="https://formsubmit.co/info@manderwines.com" method="POST">
                            <input type="hidden" name="_subject" value="A Seat at the Table: Welcome to Mander Wines">
                            <input type="hidden" name="_captcha" value="false">
                            <input type="hidden" name="_next" value="">
                            <input type="text" name="_honey" style="display:none">
                            <input type="email" name="email" placeholder="Email Address" required>
                            <button type="submit" class="btn btn-gold">Join the Journey</button>
                        </form>
                        <div class="exit-success" id="exit-success">
                            <p>Welcome to the Mander Family.</p>
                            <p style="font-size: 0.85em; opacity: 0.75; margin-top: 8px;">Please check your junk or spam folder if you don't see our email.</p>
                        </div>
                    </div>
                `;
                document.body.appendChild(exitModal);
                setTimeout(() => exitModal.classList.add('show'), 10);

                // Close button
                exitModal.querySelector('.exit-modal-close').addEventListener('click', () => {
                    exitModal.classList.remove('show');
                    setTimeout(() => exitModal.remove(), 400);
                });

                // Click outside to close
                exitModal.addEventListener('click', (e) => {
                    if (e.target === exitModal) {
                        exitModal.classList.remove('show');
                        setTimeout(() => exitModal.remove(), 400);
                    }
                });

                // Form submit
                const exitForm = document.getElementById('exit-form');
                exitForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    const formData = new FormData(exitForm);
                    fetch(exitForm.action, { method: 'POST', body: formData });
                    // Add to Brevo mailing list (auto-reply handled by Brevo Automation)
                    addToBrevo(formData.get('email'), '');
                    exitForm.style.display = 'none';
                    document.getElementById('exit-success').classList.add('show');
                    setTimeout(() => {
                        exitModal.classList.remove('show');
                        setTimeout(() => exitModal.remove(), 400);
                    }, 2000);
                });
            }
        });
    }

    // --- Smooth Page Transitions ---
    document.querySelectorAll('a[href]').forEach(link => {
        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('http') || href.startsWith('tel:') || link.target === '_blank') return;
        link.addEventListener('click', (e) => {
            e.preventDefault();
            document.body.classList.add('page-transition-out');
            setTimeout(() => { window.location = href; }, 400);
        });
    });

    // --- Parallax Scrolling ---
    if (window.matchMedia('(min-width: 901px)').matches) {
        const parallaxTargets = [
            { el: document.querySelector('.cinematic-bg img'), speed: 0.12 },
            { el: document.querySelector('.cellar-hero-bg img'), speed: 0.12 },
            { el: document.querySelector('.journey-bg-v2 img'), speed: 0.12 },
            { el: document.querySelector('.story-image-col img'), speed: 0.08 },
        ].filter(p => p.el);

        if (parallaxTargets.length) {
            window.addEventListener('scroll', () => {
                parallaxTargets.forEach(({ el, speed }) => {
                    const section = el.closest('section');
                    if (!section) return;
                    const rect = section.getBoundingClientRect();
                    if (rect.bottom > 0 && rect.top < window.innerHeight) {
                        el.style.transform = `translateY(${-rect.top * speed}px) scale(1.05)`;
                    }
                });
            }, { passive: true });
        }
    }

    // --- Lazy image fade-in ---
    document.querySelectorAll('img[loading="lazy"]').forEach(img => {
        if (img.complete) { img.classList.add('loaded'); }
        else { img.addEventListener('load', () => img.classList.add('loaded')); }
    });

    // --- Share: Copy Link ---
    document.querySelectorAll('.share-copy').forEach(btn => {
        btn.addEventListener('click', () => {
            navigator.clipboard.writeText(btn.dataset.url);
            btn.classList.add('copied');
            btn.title = 'Copied!';
            setTimeout(() => {
                btn.classList.remove('copied');
                btn.title = 'Copy Link';
            }, 2000);
        });
    });

});
