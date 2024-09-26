const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    client: {
        overlay: false,
    },
  },
  // configureWebpack: {
  //   plugins: [
  //     new webpack.DefinePlugin({
  //       __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
  //     })
  //   ]
  // }
})
