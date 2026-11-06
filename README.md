# RF4 Fish Search

俄罗斯钓鱼4（Russian Fishing 4）鱼种资料检索工具。支持中文鱼名、饵料关键词搜索，以及 TXT、MD、CSV 文本导入。数据保存在 SQLite 中，不依赖 AI 或外部 API。

## 功能

- 按鱼名或饵料关键词搜索
- 精确鱼名优先显示完整资料
- 支持批量粘贴和 TXT / MD / CSV 文件导入
- 同名鱼种再次导入时自动更新
- 支持删除单条记录
- SQLite 持久化，容器重建不会丢失数据
- 中文网页界面

## 数据格式

每行一条记录，格式如下：

    鱼名 吃饵料1、饵料2 喜爱窝子窝子描述 限制：限制说明

示例：

    白斑红点鲑 吃Spiker系列、旋转饵、Hornet系列 喜爱窝子无 限制：底钓时实际饵深须大于1米

其中“喜爱窝子”和“限制”字段可以省略。导入时按行解析；CSV 文件也应使用上述每行一条文本的格式，而不是多列电子表格格式。

## Docker 部署

在设备上执行：

    git clone https://github.com/CatTreeStreet/rf4-fish-search.git
    cd rf4-fish-search
    docker compose up -d --build

浏览器访问：

    http://设备IP:9580

容器内服务端口为 8080，宿主机固定映射为 9580。数据库保存在项目目录的 data 文件夹中。

## 更新

    git pull
    docker compose up -d --build

## 安全说明

默认没有登录认证，请仅在可信任的局域网内使用，不要直接将服务暴露到公网。
