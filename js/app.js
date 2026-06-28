document.addEventListener("DOMContentLoaded", () => {
    configurarNavbar();
});
function configurarNavbar() {

    const navbar = document.querySelector(".navbar");

    window.addEventListener("scroll", () => {

        if (window.scrollY > 80) {

            navbar.classList.add("navbar-scroll");

        } else {

            navbar.classList.remove("navbar-scroll");

        }

    });

}