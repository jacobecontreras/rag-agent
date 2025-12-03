// Sidebar navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page-content');

    function showPage(pageId) {
        // Hide all pages
        pages.forEach(page => page.classList.remove('active'));

        // Show selected page
        const selectedPage = document.getElementById(pageId + '-page');
        if (selectedPage) {
            selectedPage.classList.add('active');
        }

        // Initialize KML viewer when navigating to it
        if (pageId === 'kml-viewer') {
            if (!window.kmlViewer) {
                window.kmlViewer = new KMLViewer();
            }
            window.kmlViewer.init();
        }

        // Initialize Settings when navigating to it
        if (pageId === 'settings') {
            if (!window.settings) {
                window.settings = new Settings();
            }
        }
    }

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));

            // Add active class to clicked link
            this.classList.add('active');

            // Get the page data attribute
            const page = this.getAttribute('data-page');

            // Show the selected page
            showPage(page);
        });
    });
});