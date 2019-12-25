# selenium+webdriver实现淘宝模拟登陆
使用前先启动mitmdump，运行mitm.py脚本
```python 
mitmdump -s mitm.py
```
实现对访问请求抓包，并修改`js`，从而将`window.navigator.webdriver`设置为`false`（网站是根据这个参数判断是否是机器访问）
登录成功之后可以输入需要搜索的商品，程序会爬取搜索的商品的图片，价格，成交量，商品名称，店铺名称，发货地信息并存储到`mongodb`对应表`taobao_products/商品`中
## 最终实现效果
