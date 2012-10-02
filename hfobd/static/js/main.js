var ML = ML || {};

ML.Globe = {
    save: function() {
        window.open(this.globe.renderer.domElement.toDataURL('image/png'), 'HFOBD-Globe');
    },

    init: function(container) {
        this.globe = new DAT.Globe(document.getElementById(container), this.color_func);
        this.data = null;
    },

    color_func: function(x) {
//        var c = new THREE.Color();
//        c.setHSV( Math.max( Math.min( ( 0.6 - ( x * 0.5 ) ), 1.0), 0.0), 1.0, 1.0 );
//        return c;
        return new THREE.Color([
            0xFF0000, 0x00FF00, 0x0000FF, 0xF0F000, 0x60060, 0xFF7000, 0x905030, 0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF,0xFFFFFF
        ][x]);
    },

    render_with_data:function(data) {
        TWEEN.start();
        this.globe.addData(data, {format: 'legend'});
        this.globe.createPoints();
        this.globe.animate();
    },

    render: function() {
        this.get_data();
    },

    _render: function() {
        TWEEN.start();
        for (i = 0; i < this.data.length; i++) {
            this.globe.addData(this.data[i][1], {format: 'magnitude', name: this.data[i][0], animated: false});
        }
        this.globe.createPoints();
        this.globe.animate();
    },

    get_data: function() {
        var self = this;
        $.getJSON('/hfobd.json', function(data) {
            self.data = data;
            self._render();
        });
    }
};
