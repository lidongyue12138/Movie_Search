# Movie_Search
本次实验运用到较多python库和其他开源工具：

- python库：selenium，urllib2，bs4，flask
- Elasticsearch搜索引擎框架
- Flask web框架
- D3.js 可视化工具

我们允许时候数据已经导入了，但是由于数据巨大无法上传到GitHub，我们上传到了百度云，链接为，提取码为。

如要使用，请在百度云中下载，先安装elasticsearch，将movies压缩包解压中的网页拷贝到到crawler_douban/movies中，解压pics图片文件拷贝到douban602/pic/dataset中。

助教需要允许我们程序的话，需要安装以上工具，允许时：

1. 安装好elasticsearch以后允许elasticsearch，配置mapping文件
2. 请打开crawler_douban，在此路径下允许datacollector.py，则此程序启动。
3. 进入到douban602文件夹后，允许app.py启动web框架
4. 进入浏览器访问localhost:5000，可使用我们的搜索引擎。

