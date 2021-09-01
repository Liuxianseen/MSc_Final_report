<template>
  <van-pull-refresh v-model="isLoading" @refresh="onRefresh">
    <van-tabs v-model="active">
      <van-tab title="标签 1">
        <van-image
          fit="contain"
          src="https://img01.yzcdn.cn/vant/cat.jpeg"
        />
      </van-tab>
      <van-tab title="标签 2">
        <van-image
          fit="contain"
          src="https://img01.yzcdn.cn/vant/cat.jpeg"
        />
      </van-tab>
      <van-tab title="标签 3">
        <van-image
          fit="contain"
          src="https://img01.yzcdn.cn/vant/cat.jpeg"
        />
      </van-tab>
      <van-tab title="标签 4">
        <van-image
          fit="contain"
          src="https://img01.yzcdn.cn/vant/cat.jpeg"
        />
      </van-tab>
    </van-tabs>
  </van-pull-refresh>
</template>

<script>
  export default {
  data() {
    return {
      count: 0,
      isLoading: false,
    };
  },
  methods: {
    onRefresh() {
      location.reload();
    },
  },
};
</script>
