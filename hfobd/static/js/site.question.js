(function($){
    $.fn.question = function(){
        var question = this;
        question.mouseenter(function(){
            $(this).addClass('hover');
        });
        question.mouseleave(function(){
            $(this).removeClass('hover');
        });
        question.draggable({revert:true, helper:"clone"});
        return question;
    }
})(jQuery);