(function($){
    $.fn.questionlist = function() {
        var question_list = this;
        this.find('ul').hoverscroll({ width:$(document).width(), height:70, arrows:false});
        this.find('.question').question();
        return question_list;
    }
})(jQuery);