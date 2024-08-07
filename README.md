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
### 欄位：id(key primary)、name（用戶名稱）、email(用戶帳號兼信箱)、password(密碼)、create_time(帳號創建日期)、last_signin_time(最後登入日期)、data_id(預約景點)、date(預約日期)、time(預約時間 morning/afternoon)、price(價格 2000/2500)

```MySql
create table member (id bigint primary key, name char(50) not null, email char(50) not null, password char(255) not null, create_time datetime not null default current_timestamp, last_update_time datetime not null default current_timestamp);
```

```MySql
alter table member modify id bigint auto_increment;
```

```MySql
alter table member add column data_id bigint;
alter table member add column date char(50);
alter table member add column time char(20);
alter table member add column price bigint;
```

```MySql
alter table member change column last_signin_time last_update_time datetime not null default current_timestamp;
```

### Create a new table named order_history
### 欄位：id(key primary)、name（用戶名稱）、member_id(對應member_ID)、order_number(訂單編號)、status(PAID/UNPAID)、data_id(預約景點)、date(預約日期)、time(預約時間 morning/afternoon)、price(價格 2000/2500)


```MySql
create table order_history (id bigint primary key, name char(50) not null, member_id bigint not null, order_number char(100), status char(10) not null, data_id bigint, date char(50), time char(20), price bigint);
```

```MySql
alter table order_history modify id bigint auto_increment;
alter table order_history add foreign key (member_id) references member(id);
alter table order_history add foreign key (data_id) references data(id);
alter table order_history add column create_time datetime not null default current_timestamp;
```



