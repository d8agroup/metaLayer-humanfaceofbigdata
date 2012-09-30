(function($){
    var methods = {
        init:function(data){
            var focus_id = data.focus_id;
            var gallery = this;
            if(focus_id != '') {
                gallery.gallery('set_focus', focus_id);
            }
            return gallery;
        },
        set_focus:function(focus_id){
            var gallery = this;
            gallery.gallery('close_focus');
            gallery.find('#gallery').addClass('small');
            gallery.find('#gallery').removeClass('large');
            gallery.find('#focus').addClass('large');
            gallery.find('#focus').removeClass('small');
            setTimeout(function(){
                gallery.find('#focus_image').attr('src', '/static/media/' + focus_id + '_medium.png');
                gallery.find('#focus_image_loading').hide();
                gallery.find('#focus_image').show()
            }, 1000);
            gallery.find('#focus_save').data('image_id');
            gallery.find('#focus_delete').data('image_id');
            gallery.find('#focus_save').click(function(){
                $('#gallery').load('/gallery/' + focus_id + '?action=save', function(){
                    gallery.gallery('close_focus');
                });
            });
            gallery.find('#focus_delete').click(function(){
                $('#gallery').load('/gallery/' + focus_id + '?action=delete', function(){
                    gallery.gallery('close_focus');
                });
            });
            gallery.find('#focus_close').click(function(){
                gallery.gallery('close_focus');
            });
            if (page_image_id != focus_id) {
                gallery.find('#focus_delete').hide();
                gallery.find('#focus_save').hide();
                gallery.find('#focus_close').show();
            }
        },
        close_focus:function(){
            var gallery = this;
            gallery.find('#gallery').addClass('large');
            gallery.find('#gallery').removeClass('small');
            gallery.find('#focus').addClass('small');
            gallery.find('#focus').removeClass('large');
            gallery.find('#focus_image_loading').show();
            gallery.find('#focus_image').hide();
            gallery.find('#focus_save').removeData();
            gallery.find('#focus_delete').removeData();
            gallery.find('#focus_delete').show();
            gallery.find('#focus_save').show();
            gallery.find('#focus_close').hide();
        }
    };

    $.fn.gallery = function( method )
    {
        if ( methods[method] ) return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        else if ( typeof method === 'object' || ! method ) return methods.init.apply( this, arguments );
        else $.error( 'Method ' +  method + ' does not exist on jQuery.gallery' );
    }
})(jQuery);