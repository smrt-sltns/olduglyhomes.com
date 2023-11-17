
document.addEventListener('DOMContentLoaded', function () {
    var opts = {
      lines: 13, // The number of lines to draw
      length: 38, // The length of each line
      width: 52, // The line thickness
      radius: 45, // The radius of the inner circle
      scale: 0.3,  // Scales overall size of the spinner
      corners: 0.7, // Corner roundness (0..1)
      speed: 2.2, // Rounds per second
      rotate: 0, // The rotation offset
      animation: 'spinner-line-fade-quick', // The CSS animation name for the lines
      direction: 1, // 1: clockwise, -1: counterclockwise
      color: '#ffffff', // CSS color or array of colors
      fadeColor: 'transparent', // CSS color or array of colors
      top: '50%', // Top position relative to parent
      left: '50%', // Left position relative to parent
      shadow: '0 0 1px transparent', // Box-shadow for the lines
      zIndex: 2000000000, // The z-index (defaults to 2e9)
      className: 'spinner', // The CSS class to assign to the spinner
      position: 'absolute', // Element positioning
    };
    var loaderContainer = document.getElementById('loaderContainer');
    var loader = new Spinner(opts).spin(document.getElementById('loader'));

    // Attach click event to all <a> tags with class 'loader-link'
    var links = document.querySelectorAll('.hideCommentBtn');

    links.forEach(function (link) {
      link.addEventListener('click', function (event) {
        // Prevent the default behavior of the link
        

        // Show the loader
        loaderContainer.style.display = 'block';

        // Simulate some asynchronous task (e.g., AJAX call)
        setTimeout(function () {
          // Delay the navigation until the loader is displayed
          window.onbeforeunload = function () {
              window.location.href = event.target.href;
          };
      }, 300); 
      });
    });
  });
  