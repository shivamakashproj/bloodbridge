document.addEventListener('DOMContentLoaded', () => {

    // ========================
    // PRELOADER
    // ========================
    const preloader = document.getElementById('preloader');
    if (preloader) {
        preloader.classList.add('hidden');
        preloader.style.display = 'none';
    }

    // ========================
    // FLOATING PARTICLES
    // ========================
    const particlesContainer = document.getElementById('particles');
    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        const size = Math.random() * 6 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 8 + 6) + 's';
        particle.style.animationDelay = (Math.random() * 5) + 's';
        particlesContainer.appendChild(particle);
    }

    // ========================
    // TYPING EFFECT
    // ========================
    const typedTextElement = document.getElementById('typed-text');
    const phrases = [
        'Every Drop Counts.',
        'Save a Life Today.',
        'Be Someone\'s Hero.',
        'Donate Blood, Give Life.',
        'India Needs You.'
    ];
    let phraseIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typingSpeed = 80;

    function typeEffect() {
        const currentPhrase = phrases[phraseIndex];

        if (isDeleting) {
            typedTextElement.innerHTML = currentPhrase.substring(0, charIndex - 1);
            charIndex--;
            typingSpeed = 40;
        } else {
            typedTextElement.innerHTML = currentPhrase.substring(0, charIndex + 1);
            charIndex++;
            typingSpeed = 80;
        }

        // Add gradient styling
        typedTextElement.style.background = 'linear-gradient(45deg, #FF4444, #DC143C, #8B0000)';
        typedTextElement.style.webkitBackgroundClip = 'text';
        typedTextElement.style.webkitTextFillColor = 'transparent';
        typedTextElement.style.backgroundClip = 'text';

        if (!isDeleting && charIndex === currentPhrase.length) {
            typingSpeed = 2000; // Pause at end
            isDeleting = true;
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            phraseIndex = (phraseIndex + 1) % phrases.length;
            typingSpeed = 500; // Pause before new phrase
        }

        setTimeout(typeEffect, typingSpeed);
    }

    typeEffect();

    // ========================
    // NAVBAR SCROLL EFFECT
    // ========================
    const navbar = document.getElementById('mainNavbar');
    const backToTop = document.getElementById('backToTop');
    let lastScrollY = 0;

    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;

        if (currentScrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Back to top button visibility
        if (currentScrollY > 400) {
            backToTop.classList.add('active');
        } else {
            backToTop.classList.remove('active');
        }

        lastScrollY = currentScrollY;
    });

    // ========================
    // SMOOTH SCROLLING
    // ========================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') {
                window.scrollTo({ top: 0, behavior: 'smooth' });
                return;
            }

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                // Close mobile menu if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                    document.querySelector('.navbar-toggler').click();
                }

                const navbarHeight = navbar.offsetHeight;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - navbarHeight;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ========================
    // SCROLL REVEAL ANIMATIONS
    // ========================
    const revealElements = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right');

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('active');
            observer.unobserve(entry.target);
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px'
    });

    revealElements.forEach(el => revealObserver.observe(el));

    // ========================
    // COUNTER ANIMATION
    // ========================
    const counterElements = document.querySelectorAll('.counter');
    let countersAnimated = new Set();

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            if (countersAnimated.has(entry.target)) return;

            countersAnimated.add(entry.target);
            animateCounter(entry.target);
        });
    }, { threshold: 0.5 });

    counterElements.forEach(el => counterObserver.observe(el));

    function animateCounter(element) {
        const target = +element.getAttribute('data-target');
        const duration = 2500;
        const startTime = performance.now();

        function easeOutQuart(t) {
            return 1 - Math.pow(1 - t, 4);
        }

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easedProgress = easeOutQuart(progress);
            const currentValue = Math.floor(easedProgress * target);

            element.innerText = currentValue.toLocaleString('en-IN') + '+';

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.innerText = target.toLocaleString('en-IN') + '+';
            }
        }

        requestAnimationFrame(update);
    }

    // ========================
    // TILT EFFECT ON CARDS
    // ========================
    const tiltCards = document.querySelectorAll('.tilt-card');

    tiltCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / 15;
            const rotateY = (centerX - x) / 15;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });

    // ========================
    // BLOOD CARD CLICK EFFECT
    // ========================
    const bloodCards = document.querySelectorAll('.blood-card');

    bloodCards.forEach(card => {
        card.addEventListener('click', () => {
            // Remove active from all
            bloodCards.forEach(c => c.classList.remove('card-active'));
            // Add active to clicked
            card.classList.toggle('card-active');

            // Ripple effect
            const ripple = document.createElement('div');
            ripple.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                background: rgba(220, 20, 60, 0.2);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                animation: cardRipple 0.6s ease-out forwards;
            `;
            card.style.position = 'relative';
            card.style.overflow = 'hidden';
            card.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Add cardRipple keyframes dynamically
    const style = document.createElement('style');
    style.textContent = `
        @keyframes cardRipple {
            0% { width: 0; height: 0; opacity: 1; }
            100% { width: 300px; height: 300px; opacity: 0; }
        }
        .card-active {
            border-color: var(--red-primary) !important;
            box-shadow: 0 0 30px rgba(220, 20, 60, 0.3) !important;
        }
    `;
    document.head.appendChild(style);

    // ========================
    // FORM VALIDATION (Bootstrap native)
    // ========================
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', event => {
            if (!contactForm.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                contactForm.classList.add('was-validated');
                contactForm.style.animation = 'shake 0.5s ease';
                setTimeout(() => { contactForm.style.animation = ''; }, 500);
            }
        });
    }

    // ========================
    // CONFETTI EFFECT
    // ========================
    function createConfetti() {
        const colors = ['#DC143C', '#FF4444', '#ff6b6b', '#ffffff', '#ffd700'];
        const confettiCount = 50;

        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                width: ${Math.random() * 10 + 5}px;
                height: ${Math.random() * 10 + 5}px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                top: 50%;
                left: 50%;
                border-radius: ${Math.random() > 0.5 ? '50%' : '0'};
                z-index: 10000;
                pointer-events: none;
                animation: confettiFall ${Math.random() * 2 + 1}s ease-out forwards;
                transform: translate(${Math.random() * 600 - 300}px, ${Math.random() * -600 - 100}px) rotate(${Math.random() * 720}deg);
            `;
            document.body.appendChild(confetti);
            setTimeout(() => confetti.remove(), 3000);
        }

        // Add confetti keyframes
        if (!document.getElementById('confetti-style')) {
            const confettiStyle = document.createElement('style');
            confettiStyle.id = 'confetti-style';
            confettiStyle.textContent = `
                @keyframes confettiFall {
                    0% { 
                        opacity: 1;
                        transform: translate(0, 0) rotate(0deg) scale(1);
                    }
                    100% { 
                        opacity: 0;
                        transform: translate(var(--tx, 100px), var(--ty, 400px)) rotate(720deg) scale(0);
                    }
                }
            `;
            document.head.appendChild(confettiStyle);
        }
    }

    // ========================
    // ACTIVE NAV LINK HIGHLIGHT
    // ========================
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            if (window.scrollY >= sectionTop) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });

    // ========================
    // MOUSE CURSOR GLOW (Desktop)
    // ========================
    if (window.innerWidth > 768) {
        const cursorGlow = document.createElement('div');
        cursorGlow.style.cssText = `
            position: fixed;
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(220, 20, 60, 0.08) 0%, transparent 70%);
            pointer-events: none;
            z-index: 9998;
            transform: translate(-50%, -50%);
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(cursorGlow);

        document.addEventListener('mousemove', (e) => {
            cursorGlow.style.left = e.clientX + 'px';
            cursorGlow.style.top = e.clientY + 'px';
        });
    }
});
