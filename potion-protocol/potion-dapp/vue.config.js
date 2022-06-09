module.exports = {
  publicPath: "./",
  pluginOptions: {
    webpackBundleAnalyzer: {
      openAnalyzer: false,
      analyzerMode: "static",
    },
  },
  configureWebpack: (config) => {
    config.module.rules = [
      {
        test: /\.worker\.(js|ts)$/i,
        use: [
          {
            loader: "comlink-loader",
            options: {
              singleton: true,
            },
          },
          {
            loader: "ts-loader",
            options: {
              compilerOptions: {
                target: "ES5",
              },
            },
          },
        ],
      },
      ...config.module.rules,
    ];
  },
  chainWebpack: (config) => {
    config.plugin("html").tap((args) => {
      args[0].title = "Potion Protocol";
      return args;
    });
    config.module.rule("ts").exclude.add(/\.worker\.ts$/i);
  },
};
