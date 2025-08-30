
## watch api.cuiliangblog.cn/v1/blog/classify 接口了解是否有更新,考虑定时进行请求,结果保存为json

curl 'https://api.cuiliangblog.cn/v1/blog/classify/' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'origin: https://www.cuiliangblog.cn' \
  -H 'priority: u=1, i' \
  -H 'referer: https://www.cuiliangblog.cn/' \
  -H 'sec-ch-ua: "Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'

返回值如 classify.json 按月份统计文章和笔记


## 月份列表 数据同样写入json文件中,并要有字段记录是否获取成功

curl 'https://api.cuiliangblog.cn/v1/blog/classify/?month=2020-10' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'origin: https://www.cuiliangblog.cn' \
  -H 'priority: u=1, i' \
  -H 'referer: https://www.cuiliangblog.cn/' \
  -H 'sec-ch-ua: "Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'

返回值如 classify_month.json 月度文章列表,id值是最重要的值,后续访问文章就要使用id拼接url


## 文章详情页 url是使用文章id来拼接的,并且注意type(article|section)在url中也有体现

### 笔记的请求

curl 'https://api.cuiliangblog.cn/v1/blog/section/15276213/' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'origin: https://www.cuiliangblog.cn' \
  -H 'priority: u=1, i' \
  -H 'referer: https://www.cuiliangblog.cn/' \
  -H 'sec-ch-ua: "Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'

### 文章的请求

curl 'https://api.cuiliangblog.cn/v1/blog/article/21/' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'origin: https://www.cuiliangblog.cn' \
  -H 'priority: u=1, i' \
  -H 'referer: https://www.cuiliangblog.cn/' \
  -H 'sec-ch-ua: "Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'


两种请求返回值分别如 section.json 和 article.json ,正文在 body 中,并且注意换行等特殊符号,body保存为markdown格式,其他信息保存到json文件中,并且其中会有图片,想要下载到本地并替换为本地路径,下载成功与否必须要有记录(包括图片)

图片格式如:
``` 
\n\n![](https://cdn.nlark.com/yuque/0/2020/png/2308212/1604159965183-66a3167e-cb45-40c0-b443-57fd4ff239a6.png)\n\n\n
```