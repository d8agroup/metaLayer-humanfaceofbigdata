(function($){
    var methods = {
        init:function(){
            var charts_area = this;
            charts_area.chartsarea('repaint');
            return charts_area;
        },
        repaint:function(){
            var colors = ['#12D0FF', '#11C6F3', '#10BCE8', '#0FB3DC']
            var charts_area = this;
            charts_area.find('#charts').html('');
            var questions = $('#the_query').thequery('return_questions');
            var width, height, chart_class;
            if (questions.length < 2) {
                width = 500;
                height = 500;
                chart_class = "one_up";
                charts_area.find('#filters_container').hide();
            }
            else {
                width = 350;
                height = 350;
                chart_class = "two_up";
                charts_area.find('#filters_container').show();
            }
            for (var x=0; x<questions.length; x++) {
                var post_data = {
                    csrfmiddlewaretoken:$.cookie('csrftoken'),
                    facet_name:questions[x].facet_name
                };
                $.post('/get_graph_data', post_data, function(data){
                    var graph_data = data.graph_data;
                    var graph_id = guid();
                    var graph_html = $('<div class="chart one '+chart_class+'" style="width:'+width+'px;height:'+height+'px;"><p class="title">' + graph_data[0].key + '</p><svg id="vis_' + graph_id + '"></svg></div>');
                    charts_area.find('#charts').append(graph_html);
                    nv.addGraph(function() {
                        var chart = nv.models.pieChart()
                            .x(function(d) { return d.label })
                            .y(function(d) { return d.value })
                            .showLabels(true)
                            .showLegend(false)
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