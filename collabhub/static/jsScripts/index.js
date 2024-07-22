// Typer
var typed = new Typed(".typer", {
  strings: ["Connect", "Create", "Collaborate"],
  typeSpeed: 100,
  backSpeed: 100,
  loop: true,
  loopCount: Infinity,
  showCursor: true,
  cursorChar: "|",
  autoInsertCss: true,
});

//Counters
var elements = document.querySelectorAll(".scroll-counter");

elements.forEach(function (item) {
  // Add new attributes to the elements with the '.scroll-counter' HTML class
  item.counterAlreadyFired = false;
  item.counterSpeed = item.getAttribute("data-counter-time") / 45;
  item.counterTarget = +item.innerText;
  item.counterCount = 0;
  item.counterStep = item.counterTarget / item.counterSpeed;

  item.updateCounter = function () {
    item.counterCount = item.counterCount + item.counterStep;
    item.innerText = Math.ceil(item.counterCount);

    if (item.counterCount < item.counterTarget) {
      setTimeout(item.updateCounter, item.counterSpeed);
    } else {
      item.innerText = item.counterTarget;
    }
  };
});

// Function to determine if an element is visible in the web page
var isElementVisible = function isElementVisible(el) {
  var scroll = window.scrollY || window.pageYOffset;
  var boundsTop = el.getBoundingClientRect().top + scroll;
  var viewport = {
    top: scroll,
    bottom: scroll + window.innerHeight,
  };
  var bounds = {
    top: boundsTop,
    bottom: boundsTop + el.clientHeight,
  };
  return (
    (bounds.bottom >= viewport.top && bounds.bottom <= viewport.bottom) ||
    (bounds.top <= viewport.bottom && bounds.top >= viewport.top)
  );
};

// Funciton that will get fired uppon scrolling
var handleScroll = function handleScroll() {
  elements.forEach(function (item, id) {
    if (true === item.counterAlreadyFired) return;
    if (!isElementVisible(item)) return;
    item.updateCounter();
    item.counterAlreadyFired = true;
  });
};

// Fire the function on scroll
window.addEventListener("scroll", handleScroll);

function scrolltoelement(elementclass) {
  return function () {
    const targetElement = document.querySelector(`.${elementclass}`);
    const offset = 100; // Adjust this value as needed
    const elementPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
    const offsetPosition = elementPosition - offset;
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  }
}
document.getElementById('features-btn').addEventListener('click', scrolltoelement("features-section"));
document.getElementById('howitworks-btn').addEventListener('click', scrolltoelement("howitworks-section"));
document.getElementById('contactus-btn').addEventListener('click', scrolltoelement("footer"));

