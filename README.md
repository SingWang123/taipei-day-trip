# taipei-day-trip

### Create a new database named taipei_attractions

```MySql
create database taipei_attractions;
```

### Create a new table named data
### 欄位: id(key primary)、景點名稱('name')、景點分類('category')、捷運站位置('mrt')、描述('description')、地址('address')、交通方式('transport')、緯度('lat')、經度('lng')、

```MySql
create table data (id bigint primary key, name char(50) not null, category varchar (50), mrt varchar(20), description text, address varchar(255), transport text, lat varchar (20), lng varchar (20));
```

```MySql
alter table data modify id bigint auto_increment;
```

### Create a new table named images
### 欄位：id(key primary)、data_id（關聯data的id）、圖片網址('url')

```MySql
create table images (id bigint primary key, data_id bigint not null, img_url varchar(255));
```

```MySql
alter table images modify id bigint auto_increment;
alter table images add foreign key (data_id) references data(id);
```

### Create a new table named member
### 欄位：id(key primary)、name（用戶名稱）、email(用戶帳號兼信箱)、password(密碼)、create_time(帳號創建日期)、last_signin_time(最後登入日期)

```MySql
create table member (id bigint primary key, name char(50) not null, email char(50) not null, password char(255) not null, create_time datetime not null default current_timestamp, last_signin_time datetime not null default current_timestamp);
```

```MySql
alter table member modify id bigint auto_increment;
```

