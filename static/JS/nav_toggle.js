// Handles opening/closing the mobile hamburger menu.
// Works on every page automatically, no matter how the nav is nested,
// because it always looks for the ".navbar-nav" list that lives inside
// the same <nav> as the button that was clicked.
document.addEventListener('DOMContentLoaded', function () {
    var toggleButtons = document.querySelectorAll('.navbar-toggle');

    toggleButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            var nav = button.closest('nav');
            var menus = nav ? nav.querySelectorAll('.navbar-nav') : [];
            if (!menus.length) return;

            var isOpen = false;
            menus.forEach(function (menu) {
                isOpen = menu.classList.toggle('open');
            });
            button.classList.toggle('open', isOpen);
            button.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
    });

    // Close the open menu automatically if the screen is resized back
    // up to desktop size, so it doesn't stay stuck open.
    window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
            document.querySelectorAll('.navbar-nav.open').forEach(function (menu) {
                menu.classList.remove('open');
            });
            document.querySelectorAll('.navbar-toggle.open').forEach(function (button) {
                button.classList.remove('open');
                button.setAttribute('aria-expanded', 'false');
            });
        }
    });
});