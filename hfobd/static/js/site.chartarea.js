(function($){
    var methods = {
        init:function(){
            var chart_area = this;
            chart_area.chartarea('apply_question_droppable');
            chart_area.chartarea('repaint');
            return chart_area;
        },
        repaint:function(){
            var chart_area = this;
            if ($('.question_container .title').length == 0){
                chart_area.find('.chart').html('<svg></svg>');
            }
            else {
                var question_containers = chart_area.find('.question_container');
                var questions = [];
                for (var x=0; x<question_containers.length; x++) {
                    var facet_name = $(question_containers[x]).data('facet_name');
                    var display_name = $(question_containers[x]).data('display_name');
                    if (display_name == null || facet_name == null)
                        continue;
                    questions[questions.length] = {
                        facet_name:facet_name,
                        display_name:display_name
                    }
                }

                var search_data = JSON.stringify({questions:questions});

                var post_data = {
                    csrfmiddlewaretoken:$.cookie('csrftoken'),
                    search_data:search_data,
                    chart_area_id:chart_area.attr('id')
                };
                $.post('/get_graph_data2', post_data, function(data){
                    $('#' + data.chart_area_id + ' .chart').html('<svg></svg>');
                    if (data.graph_type == 'pie') {
                        nv.addGraph(function() {
                            var chart = nv.models.pieChart()
                                .x(function(d) { return d.label })
                                .y(function(d) { return d.value })
                                .color(data.graph_colors)
                                .showLabels(true)
                                .showLegend(false)
                                .width(350)
                                .height(350)
                                .donut(true);

                            d3.select('#' + data.chart_area_id + ' .chart svg')
                                .datum(data.graph_data)
                                .transition().duration(1200)
                                .call(chart);

                            return chart;
                        });
                    }
                    else {
                        nv.addGraph(function() {
                            var chart = nv.models.multiBarHorizontalChart()
                                .x(function(d) { return d.label })
                                .y(function(d) { return d.value })
                                //.margin({top: 5, right: 0, bottom: 0, left: 10})
                                .showLegend(false)
                                .showValues(false)
                                .tooltips(true)
                                .showControls(false);

                            d3.select('#' + data.chart_area_id + ' .chart svg')
                                .datum(data.graph_data)
                                .transition().duration(500)
                                .call(chart);

                            nv.utils.windowResize(chart.update);

                            return chart;
                        });
                    }
                });

            }




            return chart_area;
        },
        apply_question_droppable:function(){
            var chart_area = this;
            chart_area.find('.question_container').droppable({
                accept:'.question',
                drop:function(event, ui){
                    var droppable = $(this);
                    var draggable = ui.draggable;
                    var facet_name = draggable.data('facet_name');
                    var display_name = draggable.data('display_name');
                    var html = $("<p class='title'>"+display_name+"</p>");
                    droppable.html(html);
                    droppable.data('facet_name', facet_name);
                    droppable.data('display_name', display_name);
                    chart_area.chartarea('repaint');
                }
            });
            return chart_area;
        }
    };

    $.fn.chartarea = function( method )
    {
        if ( methods[method] ) return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        else if ( typeof method === 'object' || ! method ) return methods.init.apply( this, arguments );
        else $.error( 'Method ' +  method + ' does not exist on jQuery.chartarea' );
    }
})(jQuery);