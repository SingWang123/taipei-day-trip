# taipei-day-trip

### Create a new database named taipei_attractions

```MySql
create database taipei_attractions;
```

### Create a new table named data
## 欄位: id(key primary)、景點名稱('name')、景點分類('category')、捷運站位置('mrt')、描述('description')、地址('address')、交通方式('transport')、緯度('lat')、經度('lng')、

```MySql
create table data (id bigint primary key, name char(50) not null, category varchar (50), mrt varchar(20), description text, address varchar(255), transport varchar(255), lat int, lng int);
```

```MySql
ALTER TABLE data MODIFY COLUMN lat INT;
alter table data modify id bigint auto_increment;
```

### Create a new table named images
## 欄位：id(key primary)、data_id（關聯data的id）、圖片網址('url')

```MySql
create table images (id bigint primary key, data_id bigint not null, img_url varchar(255));
```

```MySql
alter table images modify id bigint auto_increment;
mysql> alter table images add foreign key (data_id) references data(id);
```