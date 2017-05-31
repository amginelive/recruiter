const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');


const extractSass = new ExtractTextPlugin({filename: '[name].[contenthash].css', allChunks: true, disable: process.env.NODE_ENV !== "production"});

module.exports = {
    context: __dirname,
    entry: {
        chat: './frontend/assets/js/index.jsx'
    },
    output: {
        path: path.resolve('./dist/'),
        filename: '[name].js',
        publicPath: '/static/'
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        extractSass,
        new CopyWebpackPlugin([{
            context: './frontend/static.prod',
            from: '**/*',
            to: './'
        }])
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
