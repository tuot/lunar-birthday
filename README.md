# Lunar Birthday

## 安装

```sh
git clone https://github.com/tuot/lunar-birthday.git
cd lunar-birthday
python setup.py install
```

## 使用前准备

-  进入Google 联系人生日栏
  - 选择自定义
  - 新建标题名称为`农历生日`
  - 选择日期为农历日期(例如：农历生日为一九九零年九月十一，选择填入为：1990/09/11)

## 使用
### 获取 client id 和 client secret

- 打开 [Google APIs](https://developers.google.com/calendar/quickstart/python)

  ![](./images/da822e775211.png)

- 获取Client ID 和 Client Secret

  ![](./images/4b1a9f507503.png)



  ### 执行命令

  - lb client_id client_secret -a
