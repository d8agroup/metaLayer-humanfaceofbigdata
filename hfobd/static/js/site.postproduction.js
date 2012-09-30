(function($){
    $.fn.postproduction = function(){
        var post_production = this;
        post_production.find('#post_production_tab').click(function(){
            var tab = $(this);
            var content = tab.parents('#post_production').find('#post_production_content');
            if (content.is(':visible')){
                content.slideUp();
                tab.html('Save & Share &#x25B2;');
            }
            else{
                content.slideDown();
                tab.html('Save & Share &#x25BC;');
            }
        });
        post_production.find('#save_and_share_button').click(function(){
            var button = $(this);
            var data = { left:{}, right:{} };

            //left images
            var left_chart = $('#chart_area_one .chart');
            if (left_chart.html() > ''){
                data.left['main_question'] = $('#chart_area_one .question_container .title').html();
                data.left['main_chart'] = jqplotToImg(left_chart);
                data.left['filters'] = [];
                var filters = $('#chart_area_one .filter_container');
                for (var x=0; x<filters.length; x++) {
                    var filter_container = $(filters[x]);
                    if (!filter_container.is('.in_use'))
                        continue;
                    data.left['filters'][data.left['filters'].length] = {
                        facet_name:filter_container.data('facet_name'),
                        facet_value:filter_container.data('facet_value'),
                        display_name:filter_container.data('display_name'),
                        chart:jqplotToImg(filter_container.find('.chart_container'))
                    }
                }
            }

            //right images
            var right_chart = $('#chart_area_two .chart');
            if (right_chart.html() > ''){
                data.right['main_question'] = $('#chart_area_two .question_container .title').html();
                data.right['main_chart'] = jqplotToImg(right_chart);
                data.right['filters'] = [];
                var filters = $('#chart_area_two .filter_container');
                for (var x=0; x<filters.length; x++) {
                    var filter_container = $(filters[x]);
                    if (!filter_container.is('.in_use'))
                        continue;
                    data.right['filters'][data.right['filters'].length] = {
                        facet_name:filter_container.data('facet_name'),
                        facet_value:filter_container.data('facet_value'),
                        display_name:filter_container.data('display_name'),
                        chart:jqplotToImg(filter_container.find('.chart_container'))
                    }
                }
            }

            var post_data = button.parents('form').serializeArray();
            post_data[post_data.length] = {name:'data', value:JSON.stringify(data) };

            $.post('/save_and_share', post_data, function(guid){
                window.open("http://"+window.location.hostname+'/static/media/'+guid+'.png');
                $('#post_production form input[type=text]').val('');
                $('#post_production_tab').click();
            });
        });
        return post_production;
    }
})(jQuery);