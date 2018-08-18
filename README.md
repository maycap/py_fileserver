# 文件服务器

为了一键线上故障快照，附带实现快速高效而有安全的文件服务器

### 快速上手


	# 默认为测试sqlite，初始化数据库
	python manager.py init_db		
	
	# 开发环境启动
	python manager.py run	
	
	＃ 生产环境启动
	sh run.sh start PRODUCTION			


### 流程介绍

1、使用token申请一个文件keys（参数: user and dst_ip）

2、只能在dst_ip 上传文件（附带md5）（可配置支持类型、只能上传一次）

3、上传完成返回 （下载地址、文件名、md5）

4、通过url直接下载，只能下载一次

	配合平台可以丰富操作：
		用户（移动端）收到节点不可用报警；
		选择挂起（抑制报警）附带，选择故障快照
		运维平台收到指令，自动执行申请、快照、上传等操作
		单独返回用户一个通知（邮件、钉钉等）
	
	
### 深入了解

> 默认配置修改 app/config.py

	# 生成管理token，替换 app/config.py => APP_TOKEN
	$ openssl rand -base64 40
	hcDkK99+Sk5US/Xoeg3Fmb4t0wagzdUBDi2HrJ93kB/IWDtEv75LIg==
	
	# 修改日志，数据库，以及文件存储路径


