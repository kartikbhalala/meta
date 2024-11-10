$(document).ready(function() {
  // Handle clicks on main menu items with sub-menus
  $(".menu > ul > li").click(function (e) {
      e.stopPropagation(); // Prevents the event from bubbling up the DOM tree
      // Remove 'active' from siblings and close any open sub-menus
      $(this).siblings().removeClass("active").find("ul").slideUp();
      // Toggle 'active' class on the clicked item and toggle its sub-menu
      $(this).toggleClass("active").find("ul").slideToggle();
  });

  // Handle clicks on the sidebar collapse/expand button
  $(".menu-btn").click(function () {
      $(".sidebar").toggleClass("active");
      $(".main-content").toggleClass("sidebar-collapsed");
  });
});


