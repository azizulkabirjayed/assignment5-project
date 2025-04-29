document.addEventListener('DOMContentLoaded', function () {
    const currentPath = window.location.pathname.replace(/\/$/, ''); // Remove trailing slash

    // Highlight active links in primary navbar
    const primaryNavLinks = document.querySelectorAll('.primary-nav ul li a');
    primaryNavLinks.forEach(link => {
        const linkPath = link.getAttribute('href').replace(/\/$/, ''); // Remove trailing slash
        if (currentPath === linkPath) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
    });

    // Highlight active links in secondary navbar
    const secondaryNavLinks = document.querySelectorAll('.secondary-nav ul li a');
    secondaryNavLinks.forEach(link => {
        const linkPath = link.getAttribute('href').replace(/\/$/, ''); // Remove trailing slash
        if (currentPath === linkPath) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
    });

    // Highlight active links in base nav (for base.html compatibility)
    const navLinks = document.querySelectorAll('nav ul li a');
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href').replace(/\/$/, ''); // Remove trailing slash
        if (currentPath === linkPath) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
            link.style.backgroundColor = '#555'; // Maintain base.html styling
        }
    });
});

