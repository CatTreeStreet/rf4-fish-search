# RF4 Fish Search

俄罗斯钓鱼4（Russian Fishing 4）鱼种资料检索工具。支持中文鱼名、饵料关键词搜索，以及 TXT、MD、CSV 文本导入。数据保存在 SQLite 中，不依赖 AI 或外部 API。

## 功能

- 按鱼名或饵料关键词搜索，精确鱼名优先
- 支持批量粘贴和 TXT / MD / CSV 文件导入
- 同名鱼种再次导入时自动更新
- 支持删除单条记录
- SQLite 持久化，容器重建不会丢失数据
- 中文网页界面
- Docker Hub 提供 AMD64 和 ARM64 镜像

## 端口统一为 9580

应用在容器内部直接监听 `0.0.0.0:9580`。无论使用 bridge 还是 host 网络，服务端口都是 9580。

### Bridge 模式（默认）

```sh
mkdir -p /overlay/docker-data/rf4-fish-search
cd /overlay/docker-data/rf4-fish-search
```

创建 `docker-compose.yml`：

```yaml
services:
  rf4-fish-search:
    image: liwangfei2/rf4-fish-search:latest
    container_name: rf4-fish-search
    restart: unless-stopped
    pull_policy: always
    ports:
      - "9580:9580"
    volumes:
      - ./data:/data
```

启动：

```sh
docker compose pull
docker compose up -d
```

### Host 模式

使用仓库中的 `docker-compose.host.yml`：

```sh
docker compose -f docker-compose.host.yml pull
docker compose -f docker-compose.host.yml up -d
```

Host 模式不需要 ports 映射，应用直接在宿主机网络命名空间监听 9580。注意同一台设备的 9580 端口不能被其他程序占用。

浏览器访问：

```
http://设备IP:9580
```

数据保存在部署目录的 `data` 文件夹中。容器内部端口和宿主机端口均为 9580。

## 更新镜像

```sh
docker compose pull
docker compose up -d
```

Host 模式更新：

```sh
docker compose -f docker-compose.host.yml pull
docker compose -f docker-compose.host.yml up -d
```

## 从源码构建

```sh
git clone https://github.com/CatTreeStreet/rf4-fish-search.git
cd rf4-fish-search
docker compose up -d --build
```

## 数据格式

每行一条记录，格式如下：

```
鱼名 吃饵料1、饵料2 喜爱窝子窝子描述 限制：限制说明
```

示例：

```
白斑红点鲑 吃Spiker系列、旋转饵、Hornet系列 喜爱窝子无 限制：底钓时实际饵深须大于1米
```

其中“喜爱窝子”和“限制”字段可以省略。导入时按行解析；CSV 文件也应使用上述每行一条文本的格式，而不是普通多列电子表格格式。

## 安全说明

默认没有登录认证，请仅在可信任的局域网内使用，不要直接将服务暴露到公网。
