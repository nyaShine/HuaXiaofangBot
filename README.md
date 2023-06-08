# HuaXiaofangBot

东华大学镜月湖畔QQ频道私域机器人

基于原先Golang的[DHUGuildBot](https://github.com/kirakiseki/DHUGuildBot)，更改为使用Python

- **/帮助**
  - 描述: 查询机器人功能。
    - @机器人 /帮助 # 显示机器人功能菜单（不含具体使用方式）
    - @机器人 /帮助 /指令名 # 显示指令使用方式
    - @机器人 /帮助 功能名 # 显示功能详情
  - 用法: 

- **/问**
  - 描述: 根据问题回答，可根据问题、答案、ID或别名搜索。
    - @机器人 /问 问题关键词1,问题关键词2,… # 显示问题和答案中包含所有关键词的问题，如果只有一个匹配的问题，则额外显示这个问题的答案
    - @机器人 /问 添加问答 问题(别名，没有可以不填):问题答案
    - @机器人 /问 添加到别名白名单 # 添加后在当前子频道内的主动消息只要含有别名，机器人就会自动回复相应的问答
    - @机器人 /问 报错 ID 报错内容 # 提交错误，我们会定期查看
  - 用法: 

- **/rss订阅**
  - 描述: 通过rss订阅自动监控和推送（23:50到6:00不推送）。
    - @机器人 /rss订阅 rss链接，仅限频道主身份组使用
  - 用法: 

- **/查询子频道**
  - 描述: 查询所有子频道的信息，仅限创建者身份组可用。
    - @机器人 /查询子频道，仅限频道主身份组使用
  - 用法: 

- **/查询身份组**
  - 描述: 查询所有身份组的信息，仅限创建者身份组可用。
    - @机器人 /查询身份组，仅限频道主身份组使用
  - 用法: 

- **/c**
  - 描述: 略
    - @机器人 /c 消息
  - 用法: 

- **关键词撤回、禁言、通知与移除**
  - 描述: 根据关键词撤回消息、禁言、通知和移除发布者，支持正则表达式。
  - 用法: 

- **东华大学勤工助学信息订阅**
  - 描述: 监控东华大学校外和校内勤工助学系统并自动推送（23:50到6:00不推送）。
  - 用法: 

- **DHU邮箱认证（暂时还没从go那边搬过来，用不了）**
  - 描述: 私信认证 DHU 校园邮箱，获得【已校园邮箱认证】身份组，在交易时更加可靠，同时解锁公告和志愿子频道的发言权限。
  - 用法:
    - 如果你的邮箱为example@dhu.edu.cn，请私信机器人example@
    - 如果你的邮箱为example@mail.dhu.edu.cn，请私信机器人example@mail
    - 如果你的邮箱为example@teacher.dhu.edu.cn，请私信机器人example@teacher
    - 如果你是学生，通常为example@mail
    - 机器人会向你的邮箱发送验证码，如【Y0000】
    - 请私信机器人【Y0000】（不包括括号）即可认证校园邮箱