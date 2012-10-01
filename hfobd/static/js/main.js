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
            0xbe1111, 0xb6b4b5, 0x9966cc, 0x15adff, 0x3e66a3, 0x216288, 0xff7e7e, 0xff1f13,
            0xc0120b, 0x5a1301, 0xffcc02, 0xedb113, 0x9fce66, 0x0c9a39, 0xfe9872, 0x7f3f98,
            0xf26522, 0x2bb673, 0xd7df23, 0xe6b23a, 0x7ed3f7
        ][x]);
    },

    render_with_data:function(data) {
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
