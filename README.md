# Wanderjahre · 文献导读

德国帮工游历年（Wanderjahre / Gesellenwanderung / Walz）文献导读，以文艺复兴前后为中心，横向比较地区、工种和时期，纵向追问劳动、学习、身份与制度之间的关系。

**[阅读网站](https://windsweeps.github.io/wanderjahre/)** · [逐条导读 Markdown](wanderjahre-annotated-bibliography.md) · [研究综述 Markdown](wanderjahre.md)

- 57条参考资料，119条观点，6条并读路径，90个外部资料链接。
- 每条包含实际阅读范围、摘要、重要观点、原文短摘、译文、出处定位、追问和证据边界。
- 支持全文搜索、分类、原生折叠、文献互链和打印；手机适配，支持文字放大。
- 右侧历史时间索引按研究对象／史料事件年代排序，可点击打开对应条目；窄屏收为可展开目录。出版／编订年份另列。
- 纯静态 HTML/CSS/JavaScript；首页约291 KiB，含字体，无运行时第三方脚本、字体或图片请求。

## 本地阅读

直接打开 `index.html` 即可阅读。也可在仓库目录运行：

```sh
python3 -m http.server 8768 --bind 127.0.0.1
```

访问 <http://127.0.0.1:8768/>。`wanderjahre.html` 是完整研究综述；相邻Markdown文件提供下载。

## 更新与构建

仅需Python 3标准库，无需安装依赖：

```sh
python3 build_annotations.py
python3 check_site.py
```

`build_annotations.py`读取 `sources.json` 与四组 `annotations-*.json`，生成逐条导读Markdown和 `index.html`；`reader_template.py`负责网站结构，`reader.css`和`reader.js`在构建时内联。研究综述作为已有静态文档保留，不会被此构建命令重写。

`historical_periods.json`记录历史时段标签、排序锚点与依据。排序锚点不是精确起年；没有可核起讫的综述与称谓指南归入跨期研究。

修改文献时先更新源记录，保留原编号、引用出处、阅读范围与证据边界。`check_site.py`检查内容覆盖、引用、相邻文件及文档锚点；它不验证外部来源是否仍可访问，也不替代浏览器检查。

## GitHub Pages

Pages从 `main` 分支根目录发布；`.nojekyll`关闭Jekyll处理。提交已生成的HTML、Markdown与资源即可更新网站，无需前端构建服务。

## 资料范围

文献核读记录日期为 **2026-10-07**，网页呈现整理日期为 **2026-10-20**。网站发布不代表对全部文献或外链重新核查。

H11、A11尚未取得实质正文；A4短摘为章节题名；A7依据馆方介绍；A17依据抄本编目；A5为Stewart的书评。各项均在页面中标明，不能当作已经通读原著。原文短摘、作者摘要、机构说明与研究者追问分别标识。

## 视觉与许可

纸色、墨色与朱红细线参考中世纪书页和Lightmind/PentimentGlyph的视觉语言。UnifrakturCook仅用于短标题，正文使用系统字体。

- 原创网站代码：[MIT](LICENSE)。
- 原创导读、摘要和译解：[CC BY 4.0](CONTENT-LICENSE.md)。
- UnifrakturCook字体：[SIL OFL 1.1](reader-assets/OFL.txt)，保留原版权和Reserved Font Name。
- 引用的第三方文字及链接目标仍归原权利人，不因本项目许可而重新授权。参见 [NOTICE](NOTICE.md)。
