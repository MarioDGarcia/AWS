import boto3
s3 = boto3.client(
        's3',
        aws_access_key_id='ASIATWFSF5MEGAOOVO4Q',
        aws_secret_access_key='dSRYkbUrZSUv4Y6bZm7r1IgQH5I7bOcS51pa1VKo',
        aws_session_token='IQoJb3JpZ2luX2VjEBMaCXVzLXdlc3QtMiJIMEYCIQDsZL5bDX+eUHI8p3CnPL/Zm55DRjD++XjXwy6sEiqhzAIhANqmQXibpRHQEN2biLxc97u77N0kdu/1kKrKx6q++D6dKr4CCMz//////////wEQABoMMjUzNzc2NzUxMzY4IgyU/SGaKA+poJWct6sqkgLPcqHWVqBE3adoJUZuhYgZvfd4ojNJbJy3ALm3LLl5Xqp/T1c9vweWfQJZEzYBKetYTvA2njlfY3aqUhkkWvXrs463CV7cKM5MZelG4YXuD1glj8mVO3+OoIvOBB9w2AlDC4f/DKoaMp6r2dqlzjWGvw4Q3FB83HEQEiilcnAIhkuZS8RQ3ieMGkJ/3gyj/xfllk9pHUQXgY+O8S/ksVtntbE/MJuLuNX1kxBqOJlZS3SZVbdoqCLRsAQgGfEhQyNcKcsyvPeJ4ri/SN/5syfcXpVJJu4+DReP9LBp3VB0Rx4lz2K+Pj3NFzmZfgspwTjn4PUsjQlan9s7egPNgFQdbNXVHcMw4grv40QnikTEjzZGMJ2OhsgGOpwBCb8Wrx+yGufvq8pjI2QdXc6BEaZvEHCpjnLj/C1xJD9e8L1NXXKLFoiIZagGPp0V9WeIBrZyDDTvjvgjjGrdkucEA4+Hdclrc7inejbY+brZ0AOkuso74PyS9DNlmUD7b1q9IMA73CZovUHL96mQpkYa+37AtfUbOvyY9E4Yx4Smgou1PZ7NbJa+ZsWF8kdnzAUpo2TXLdhUkk09',
        region_name='us-east-1'
    )



def getCredentials():
    return s3