(function($){
    var methods = {
        init:function(){
            var charts_area = this;
            charts_area.chartsarea('repaint');
            return charts_area;
        },
        repaint:function(){
            var charts_area = this;
            charts_area.html('');
            var questions = $('#the_query').thequery('return_questions');
            var width = (questions.length == 1) ? 500 : 350;
            var height = (questions.length == 1) ? 500 : 350;
            var chart_class = (questions.length == 1) ? 'one_up' : 'two_up';
            for (var x=0; x<questions.length; x++) {
                var post_data = {
                    csrfmiddlewaretoken:$.cookie('csrftoken'),
                    facet_name:questions[x].facet_name
                };
                $.post('/get_graph_data', post_data, function(data){
                    var graph_data = data.graph_data;
                    var graph_id = guid();
                    var graph_html = $('<div class="chart one '+chart_class+'" style="width:'+width+'px;height:'+height+'px;"><p class="title">' + graph_data[0].key + '</p><svg id="vis_' + graph_id + '"></svg></div>');
                    charts_area.append(graph_html);
                    nv.addGraph(function() {
                        var chart = nv.models.pieChart()
                            .x(function(d) { return d.label })
                            .y(function(d) { return d.value })
                            .showLabels(false)
                            .width(width)
                            .height(height)
                            .donut(true);

                        d3.select('#vis_' + graph_id)
                            .datum(graph_data)
                            .transition().duration(1200)
                            .call(chart);

                        return chart;
                    });
                });
            }
            return charts_area;
        }
    };

    $.fn.chartsarea = function( method )
    {
        if ( methods[method] ) return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        else if ( typeof method === 'object' || ! method ) return methods.init.apply( this, arguments );
        else $.error( 'Method ' +  method + ' does not exist on jQuery.chartsarea' );
    }
})(jQuery);