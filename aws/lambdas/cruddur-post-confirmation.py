import json
import psycopg2
import os

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    print('UserAttributes')
    print(user)


    user_display_name = user['name']
    user_handle = user['preferred_username']
    user_email = user ['email']
    user_cognito_id = user ['sub']

    try:
        print('entered try')
        sql = f"""
        INSERT INTO users (
            display_name, 
            handle,
            email, 
            cognito_user_id
        ) 
        VALUES(%s, %s, %s, %s) 
        """

        print('SQL statement .....')
        print(sql)
        conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
        #     host=(os.getenv('PG_HOSTNAME')),
        #     database=(os.getenv('PG_DATABASE')),
        #     user=(os.getenv('PG_USERNAME')),
        #     password=(os.getenv('PG_SECRET'))
        # )
        cur = conn.cursor()
        params = [
            user_display_name,
            user_email,
            user_handle,
            user_cognito_id
        ]
    
        cur.execute(sql, parameters)
        conn.commit() 

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event