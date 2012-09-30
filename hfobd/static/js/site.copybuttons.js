(function($){
    $.fn.copybuttons = function(){
        var copy_buttons = this;
        copy_buttons.find('#copy_right_button').click(function(){
            if ($('#chart_area_one .question_container .title').length > 0){
                var data = $('#chart_area_one').chartarea('return_data');
                $('#chart_area_two').chartarea('build_from_data', data);
            }
        });
        copy_buttons.find('#copy_left_button').click(function(){
            if ($('#chart_area_two .question_container .title').length > 0){
                var data = $('#chart_area_two').chartarea('return_data');
                $('#chart_area_one').chartarea('build_from_data', data);
            }
        });
        return copy_buttons;
    }
})(jQuery);