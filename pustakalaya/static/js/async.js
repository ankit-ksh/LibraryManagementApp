function loadMainBlockContent(url) {
    // animation
    document.querySelector('main').innerHTML = '<p style="margin: 1000px;">loading.....</p>';

    // Fetch the content of the page asynchronously
    fetch(url)
        .then(response => response.text())
        .then(html => {
            // Update the main block with the fetched content
            document.querySelector('main').innerHTML = html;
        })
        .catch(error => {
            console.error('Error fetching page:', error);
        });
}


// toggle classess such as for the icons
function toggleClasses(element, class1, class2) {
    element.classList.toggle(class1);
    element.classList.toggle(class2);
}