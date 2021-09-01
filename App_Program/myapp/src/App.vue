<template>
  <div id="app">
    <van-pull-refresh v-model="isLoading" @refresh="onRefresh">
      <div>
        <div title="fig 1" style="display:block">
          <img id="fig1" 
          />
        </div>
        <div title="fig 2">
          <img id="fig2" style="display:none"
          />
        </div>
        <div title="fig 3">
          <img id="fig3" style="display:none"
          />
        </div>
        <div title="fig 4">
          <img id="fig4" style="display:none"
          />
        </div>
      </div>
    </van-pull-refresh>
    <van-cell-group style="margin-top:100px;">
    <van-field v-model="ip" label="Server IP" placeholder="please input server ip and port" />
  </van-cell-group>
  <div style="margin-top:20px;">
      <div style="width:50%;padding:0;margin:0;float:left;box-sizing:border-box;"><button id = "connect" v-on:click="connect()">connect</button></div>     
      <div style="width:50%;padding:0;margin:0;float:left;box-sizing:border-box;"><button v-on:click="next()">next</button>
      </div>
  </div>
  </div>

</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

img{
    display: block;
    width: 100%;
    height: 100%;
    padding-top:50%
}


#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
<script>
  export default {
  data() {
    return {
      count: 0,
      isLoading: false,
      ip:''
    };
  },
  methods: {
    onRefresh() {
      location.reload();
    },
    connect(){
      document.getElementById("fig1").style.display="block";
      document.getElementById("fig1").src='http://' + this.$data.ip + '/1.jpg';
      document.getElementById("fig4").style.display="none";
      document.getElementById("connect").disabled="disabled";
    },
    next(){
      if(this.$data.ip == ''){
        alert('please input server ip');
        return;
      }
      this.$data.count = (this.$data.count + 1) % 4;
      if(this.$data.count == 0){
        document.getElementById("fig1").style.display="block";
        document.getElementById("fig1").src='http://' + this.$data.ip + '/1.jpg?' + Math.random();
        document.getElementById("fig4").style.display="none";
      }
      if(this.$data.count == 1){
        document.getElementById("fig1").style.display="none";
        document.getElementById("fig2").style.display="block";
        document.getElementById("fig2").src='http://' + this.$data.ip + '/2.jpg?' + Math.random();
      }
      if(this.$data.count == 2){
        document.getElementById("fig2").style.display="none";
        document.getElementById("fig3").style.display="block";
        document.getElementById("fig3").src='http://' + this.$data.ip + '/3.jpg?' + Math.random();
      }
      if(this.$data.count == 3){
        document.getElementById("fig3").style.display="none";
        document.getElementById("fig4").style.display="block";
        document.getElementById("fig4").src='http://' + this.$data.ip + '/4.jpg?' + Math.random();
      }      
    }
  },
};
</script>