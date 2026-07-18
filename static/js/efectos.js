
<script>
	window.sr = ScrollReveal();

  sr.reveal('.navbar', {
	duration: 500,
	origin: 'bottom'
  });

  sr.reveal('.aprende', {
	duration: 500,
	origin: 'top',
	distance: '300px'
  });

  sr.reveal('.portada', {
	duration: 750,
	origin: 'left',
	distance: '300px'
  });
  sr.reveal('.entrada', {
	duration: 750,
	origin: 'right',
	distance: '300px',
	viewFactor: 0.2
  });

  sr.reveal('.xd', {
	duration: 1000,
	origin: 'bottom'
  });

  sr.reveal('#testimonial', {
	duration: 1000,
	origin: 'left',
	distance: '300px',
	viewFactor: 0.2
  });

  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
	anchor.addEventListener('click', function (e) {
	  e.preventDefault();

	  document.querySelector(this.getAttribute('href')).scrollIntoView({
		behavior: 'smooth'
	  });
	});
  });
  </script>