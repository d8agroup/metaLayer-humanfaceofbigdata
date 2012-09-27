(function($){
    $.fn.question = function(){
        var question = this;
        question.addClass('ui-state-default');
        question.mouseenter(function(){
            $(this).addClass('ui-state-active');
        });
        question.mouseleave(function(){
            $(this).removeClass('ui-state-active');
        });
        question.draggable({revert:true, helper:"clone"});
        return question;
    }
})(jQuery);