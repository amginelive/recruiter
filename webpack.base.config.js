const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const ExtractTextPlugin = require('extract-text-webpack-plugin');


const extractSass = new ExtractTextPlugin({filename: '[name].[contenthash].css', allChunks: true, disable: process.env.NODE_ENV !== "production"});

module.exports = {
    context: __dirname,
    entry: {
        init: '.frontend/assets/js/chat.jsx'
    },
    output: {
        path: path.resolve('.frontend/static.prod/'),
        filename: '[name].js',
        publicPath: '/static/'
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        extractSass
    ],
    module: {
        rules: [
        {
            test: /\.jsx?$/,
            use: 'babel-loader',
            exclude: [/node_modules/]
        },
        {
            test: /\.scss$/,
            use: extractSass.extract({
                use: [{
                    loader: "css-loader"
                }, {
                    loader: "sass-loader"
                }],
                // use style-loader in development
                fallback: "style-loader"
            })
        }
        ]
    }
};
