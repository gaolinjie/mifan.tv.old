(function($){
   $.fn.extend({
    	//返回顶部
    	returntop: function(){
    		if(!this[0]){
				return;
			}
			var backToTopEle = this.click( function() {
				$("html, body").animate({
					scrollTop: 0
				}, 500);
			});
			var timeDelay = null;
			var backToTopFun = function() {	
				var docScrollTop = $(document).scrollTop();
				var winowHeight = $(window).height();
				(docScrollTop > 0)? backToTopEle.css("bottom","200px"): backToTopEle.css("bottom","-200px");
				//IE6下的定位
				if ($.browser.msie && ($.browser.version == "6.0") && !$.support.style) {
					backToTopEle.hide();
					clearTimeout(timeDelay);
					timeDelay = setTimeout(function(){
						backToTopEle.show();
						clearTimeout(timeDelay);
					},1000);
					backToTopEle.css("top", docScrollTop + winowHeight - 125);
				}
			};
			$(window).bind("scroll", backToTopFun);
    	}
})
})(jQuery);
