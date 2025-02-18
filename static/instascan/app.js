var app = new Vue({
  delimiters: ['[[', ']]'],
  el: '#app_instascan',
  data: {
    scanner: null,
    activeCameraId: null,
    cameras: [],
    scans: [],
    lastScan: ''
  },
  mounted: function () {
    var self = this;
    self.scanner = new Instascan.Scanner({ video: document.getElementById('preview'), scanPeriod: 5, mirror: false });
    self.scanner.addListener('scan', function (content, image) {
      self.scans.unshift({ date: +(Date.now()), content: content });
      self.lastScan = content;
      self.$emit('escaneado');
      chequeaEstado('dni-frontc', 'canvasDniFront', 'dni-backc', 'canvasDniBack', 'identificacion', content, 'idNegocio');
    });
    Instascan.Camera.getCameras().then(function (cameras) {
      self.cameras = cameras;
      if (cameras.length > 0) {
        self.activeCameraId = cameras[0].id;
        self.scanner.start(cameras[0]);
      } else {
        console.error('No cameras found.');
      }
    }).catch(function (e) {
      console.error(e);
    });
  },
  methods: {
    formatName: function (name) {
      return name || '(unknown)';
    },
    selectCamera: function (camera) {
      this.activeCameraId = camera.id;
      this.scanner.start(camera);
    }
  }
});
