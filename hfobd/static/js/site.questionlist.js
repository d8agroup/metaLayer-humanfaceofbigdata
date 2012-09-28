(function($){
    $.fn.questionlist = function() {
        var question_list = this;
        this.find('ul').hoverscroll({ width:1024, height:70, arrows:false});
        this.find('.question').question();
        return question_list;
    }
})(jQuery);