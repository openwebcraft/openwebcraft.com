
/**
 * Module dependencies.
 */

var express = require('express');
var http = require('http');
var path = require('path');
var xml2js = require('xml2js');
var request = require('request');
var _ = require('underscore');
var mm = require('marky-mark');
var moment = require('moment');

var app = express();

// all environments
app.set('port', process.env.PORT || 3000);
app.set('views', __dirname + '/views');
app.engine('html', require('hogan-express'));
app.set('view engine', 'html');    // use .html extension for templates
app.set('layout', 'purelayout');       // use layout.html as the default layout
app.use(express.favicon());
app.use(express.logger('dev'));
app.use(express.bodyParser());
app.use(express.methodOverride());
app.use(app.router);
app.use(require('less-middleware')({ src: __dirname + '/public' }));
app.use(express.static(path.join(__dirname, 'public')));

// development only
if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}

var blogRssFeedUrl =  process.env.BLOGRSSFEEDURL || 'http://writing.openwebcraft.com/rss/';
var latestBlogPosts = null;
request(blogRssFeedUrl, function (error, response, body) {
    if (!error && response.statusCode == 200) {
        var parseString = xml2js.parseString;
        parseString(body, function (err, result) {
            latestBlogPosts = result.rss.channel[0].item.splice(0,4);
            _.invoke(latestBlogPosts, function(){
                this.pubDateFromNow = moment(this.pubDate[0]).fromNow();
                this.author = this['dc:creator'][0];
            });
            //console.log(latestBlogPosts);
        });
    }
})

var pages = mm.parseDirectorySync(__dirname + "/pages");

app.use(function(req,res) {
    var path = req.path;

    var page = null;
    var tpl = null;

    page = _.find(pages, function(p){
        return p.meta.slug === path;
    });

    if (path === '/') {
        // default, index.html
        tpl = 'index';
        page = {
            meta: {title: 'openwebcraft.com'},
            latestBlogPosts: latestBlogPosts
        };
    } else if (page) {
        // valid pages/*.md
        tpl = 'page';
    } else {
        // neither index
        // nor page found by slug
        // we consider it a 404
        tpl = '404';
        page = { meta: {title: '404 - Page Not Found'} };
    }
    //console.log(tpl, page);
    res.render(tpl, page);
});

http.createServer(app).listen(app.get('port'), function(){
  console.log('Express server listening on port ' + app.get('port'));
});
