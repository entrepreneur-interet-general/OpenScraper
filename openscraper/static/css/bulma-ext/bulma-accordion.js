(function () {
'use strict';

const MOUSE_EVENTS = ['click', 'touchstart'];

document.addEventListener( 'DOMContentLoaded', function () {
  var accordions = document.querySelectorAll('.accordions');
  [].forEach.call(accordions, function(accordion) {
    var items = accordion.querySelectorAll('.accordion');
    [].forEach.call(items, function(item) {
      MOUSE_EVENTS.forEach((event) => {
        item.querySelector('.toggle, [data-action="toggle"]').addEventListener(event, e => {
          e.preventDefault();
          if (!item.classList.contains('is-active')) {
            let activeItem = accordion.querySelector('.accordion.is-active');
            if (activeItem) {
              activeItem.classList.remove('is-active');
            }
            item.classList.add('is-active');
          } else {
            item.classList.remove('is-active');
          }
        });
      });
    });
  });
});

}());
