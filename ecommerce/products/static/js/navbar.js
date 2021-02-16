const navSlide = () => {
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.nav-links');
    const navLinks = document.querySelectorAll('.nav-links li');

    burger.addEventListener('click', () => {

        nav.classList.toggle('nav-active');

        navLinks.forEach((link, index) => {
            if(link.style.animation) {
                link.style.animation = '';
            }
            else {
                link.style.webkitAnimation = `navLinkFade ease 0.5s forwards ${index / 7 + 0.3}s`;
                console.log(link.style.animation);
            }
        });

        burger.classList.toggle('toggle');
    
    });
}

navSlide();