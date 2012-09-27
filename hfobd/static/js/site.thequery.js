(function($){
    var methods = {
        init:function(){
            var the_query = this;
            the_query.thequery('apply_question_droppable');
            the_query.thequery('apply_query_question_trash_droppable');
            return the_query;
        },
        apply_question_droppable:function(){
            var the_query = this;
            the_query.find('.query_question_drop_container').droppable({
                accept:'.question, .query_qestion',
                activeClass:'active',
                hoverClass:'hover',
                drop:function(event, ui){
                    var draggable = ui.draggable;
                    var facet_name = draggable.data('facet_name');
                    var display_name = draggable.data('display_name');
                    var html = $("<div class='query_question ui-state-default corner_large'><p class='display_name'>"+display_name+"</p></div>");
                    html.data('facet_name', facet_name);
                    html.data('display_name', display_name);
                    $(this).html(html);
                    html.draggable({ revert:true });
                }
            });
            return the_query
        },
        apply_query_question_trash_droppable:function(){
            var the_query = this;
            the_query.find('#query_question_trash').droppable({
                accept:'.query_question',
                drop:function(event, ui){
                    ui.draggable.remove();
                }
            });
            return the_query;
        }
    };

    $.fn.thequery = function( method )
    {
        if ( methods[method] ) return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        else if ( typeof method === 'object' || ! method ) return methods.init.apply( this, arguments );
        else $.error( 'Method ' +  method + ' does not exist on jQuery.thequery' );
    }
})(jQuery);