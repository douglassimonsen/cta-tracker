cursor.execute(f'''
    truncate table cta_tracker.{name};
    SELECT aws_s3.table_import_from_s3(
        'cta_tracker.{name}', 
        '', 
        '(format csv, header true, DELIMITER '','', QUOTE ''"'', ESCAPE ''\\'')',
        '(cta-bus-and-train-tracker,schedules/raw/{name}.csv.gzip,us-east-1)', 
        aws_commons.create_aws_credentials('{envs['user']['access_key']}', '{envs['user']['secret_key']}', '')
    );
''')