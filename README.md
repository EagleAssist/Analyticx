# Analyticx

The analysis dashboard should be perfect
 - A logging system should be present for observability


All workloads should be on AWS

### About YOLO

https://www.v7labs.com/blog/yolo-object-detection


DB Outline should be like

main_table <small> Will change this name in future </small>
id image_id cordinate_json[each-with id] color[each-with id]

Mapping of Ports in the Application

| Service         | Internal Port | External Port |
|-----------------|---------------|---------------|
| ingestion      | 5000          | 5000          |
| detection       | 5000          | 8000          |
| minio           | 9000          | 9000          |
| minio (console) | 9001          | 9001          |
| rabbitmq        | 5672          | 5672          |
| rabbitmq (mgmt) | 15672         | 15672         |


