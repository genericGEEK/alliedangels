(function ($) {
  function initConditionalLoop($carousel) {
    const itemCount = $carousel.children().length;

    // read your data-owl-options JSON (theme is using this pattern)
    let options = $carousel.data("owl-options") || {};

    // loop only when more than 2 items
    options.loop = itemCount > 2;

    // If the theme already initialized it, destroy and re-init cleanly
    if ($carousel.hasClass("owl-loaded")) {
      $carousel.trigger("destroy.owl.carousel");
      $carousel.removeClass("owl-loaded owl-hidden");
      $carousel.find(".owl-stage-outer").children().unwrap();
      $carousel.find(".owl-stage").children().unwrap();
    }

    $carousel.owlCarousel(options);
  }

  // run after everything else (theme init included)
  $(window).on("load", function () {
    $(".tevents-page__carousel").each(function () {
      initConditionalLoop($(this));
    });
  });
})(window.jQuery);
