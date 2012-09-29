(function($){
    var methods = {
        init:function(){
            var chart_area = this;
            chart_area.find('.filters').filters();
            chart_area.chartarea('apply_question_droppable');
            chart_area.chartarea('repaint');
            chart_area.find('.close_button').click(function(){
                $(this).parents('.chart_area_container').chartarea('clear');
            });
            return chart_area;
        },
        repaint:function(){
            var chart_area = this;
            if ($('.question_container .title').length == 0){
                chart_area.removeClass('has_data');
                chart_area.find('.filters_list').html(
                    '<div class="filter_container"><p class="title"></p><div class="chart_container"></div><div class="close_button_container"><img src="/static/images/button_close.png" class="close_button"/></div></div>'+
                    '<div class="filter_container"><p class="title"></p><div class="chart_container"></div><div class="close_button_container"><img src="/static/images/button_close.png" class="close_button"/></div></div>'+
                    '<div class="filter_container"><p class="title"></p><div class="chart_container"></div><div class="close_button_container"><img src="/static/images/button_close.png" class="close_button"/></div></div>'
                );
                chart_area.find('.filters').filters();
            }
            else {
                chart_area.addClass('has_data');
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

                var filter_container = chart_area.find('.filter_container');
                var filters = [];
                for (var x=0; x<filter_container.length; x++) {
                    var facet_name = $(filter_container[x]).data('facet_name');
                    var display_name = $(filter_container[x]).data('display_name');
                    var facet_value = $(filter_container[x]).data('facet_value');
                    if (display_name == null || facet_name == null)
                        continue;
                    filters[filters.length] = {
                        facet_name:facet_name,
                        display_name:display_name,
                        facet_value:facet_value
                    }
                }

                var search_data = JSON.stringify({questions:questions, filters:filters});

                var post_data = {
                    csrfmiddlewaretoken:$.cookie('csrftoken'),
                    search_data:search_data,
                    chart_area_id:chart_area.attr('id')
                };
                $.post('/get_graph_data3', post_data, function(data){
                    for(var x=0; x<charts[data.chart_area_id].length; x++){
                        charts[data.chart_area_id][x].destroy();
                    }
                    $('#' + data.chart_area_id + ' .chart').html('<svg></svg>');
                    $('#' + data.chart_area_id + ' .filters').filters('update_filters', { filters:data.filters, chart_area_id:data.chart_area_id});
                    if (data.graph_type == 'pie') {
                        charts[data.chart_area_id][charts[data.chart_area_id].length] = jQuery.jqplot(data.chart_area_id + ' .chart',
                            [data.graph_data.values],
                            {
                                title: ' ',
                                legend: { show:false },
                                seriesDefaults: {
                                    renderer: jQuery.jqplot.DonutRenderer,
                                    rendererOptions: {
                                        sliceMargin:4,
                                        showDataLabels: true,
                                        dataLabels:data.graph_data.labels
                                    },
                                    highlighter: {
                                        show: false,
                                        formatString:'',
                                        tooltipLocation:'s',
                                        useAxesFormatters:false
                                    }
                                },
                                seriesColors:data.graph_colors,
                                grid:{
                                    background:'#1D2228',
                                    borderWidth:0,
                                    shadow:false
                                }
                            }

                        );
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
            chart_area.find('.questions_and_chart').droppable({
                accept:'.question',
                drop:function(event, ui){
                    var droppable = $(this).find('.question_container');
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
        },
        clear:function(){
            var chart_area = this;
            chart_area.find('.questions_list').html('<li><div class="question_container"></div></li>');
            chart_area.find('.chart').html('');
            chart_area.find('.chart_container').html('');
            chart_area.chartarea('apply_question_droppable');
            chart_area.chartarea('repaint');
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