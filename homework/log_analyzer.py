# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '  
#                     '$request_time';

import argparse

import os

import re

import gzip

from statistics import median

import json

import logging

logger1 = logging.getLogger('logger1')

logger1.setLevel(logging.INFO)

handler1 = logging.FileHandler(f'./main_log.log', mode = 'a')#a

formatter1 = logging.Formatter('%(asctime)s;%(message)s', datefmt='%d/%m/%Y %H:%M:%S')#%(levelname)s

handler1.setFormatter(formatter1)

logger1.addHandler(handler1)

 

parser = argparse.ArgumentParser()

parser.add_argument('--config', type=str, required=False, help='Path to the configuration file')

 

args = parser.parse_args()

try:

# Чтение данных из файла JSON

    with open(args.config, 'rt') as file:

        new_config = json.load(file)

except FileNotFoundError:

    try:

        with open('./data.json', 'rt') as file:

            new_config = json.load(file)

        #print(data_dict)

    except:

        logger1.error(f'no inpit config-file')

except:

    logger1.error(f'no inpit config-file')

    quit(1)

default_config = {

    "REPORT_SIZE": 1000,

    "REPORT_DIR": "./reports",

    "LOG_DIR": "./log"

}

config = {}

for key in list(default_config.keys()):

    if key in new_config and new_config[key] != '':

        config[key] = new_config[key]

    else:

        config[key] = default_config[key]

  

 


def split_and_clear(text):

    parts = re.split(r'\s+(?=(?:[^"\[\]]|"[^"]*"|\[[^\[\]]*\])*$)', text)

    cleaned_parts = [re.sub(r'[\["\]]', '', part) for part in parts]

    return cleaned_parts


def open_log(file_name):

    with open(f'{config["LOG_DIR"]}/{file_name}','r',encoding = 'utf-8') as f:

        file = f.read().split('\n')

    yield file,file_name.split('.')[1].split('-')[1]

   

def open_log_gz(file_name):     

    with gzip.open(f'{config["LOG_DIR"]}/{file_name}','rt', encoding = 'cp1251') as f:

        file = f.read().split('\n')

    yield file,file_name.split('.')[1].split('-')[1]

def main(config):

    try:

        file_name=os.listdir(f'{config["LOG_DIR"]}')

        #print(file_name)

        try:

            max_file_name = max(file_name,key = lambda log_date: log_date.split('.')[1] if log_date.startswith('nginx-access-ui') else '')

        except:

            logger1.error(f'no files in dir - {config["LOG_DIR"]}')

        if max_file_name.startswith('nginx-access-ui'):

            file_data = open_log_gz(max_file_name) if max_file_name.endswith('.gz') else open_log(max_file_name)

            #print(file_data)

        else:

            logger1.error(f'no logs in dir - {config["LOG_DIR"]}')

            return

 

        data_dict = {}

        all_count = 0

        all_time = 0.0

        data,date = next(file_data)


        data_list = []

        file_date = list(date)

        file_date = f"{''.join(file_date[:4])}.{''.join(file_date[4:][:2])}.{''.join(file_date[4:][2:])}"

        save_file_name = f'result-{file_date}.json'



        if save_file_name in os.listdir(f'{config["REPORT_DIR"]}'):

            logger1.info(f'nothing to do. "{save_file_name}" alrdy parsed')

            return

        for line in data:

            all_count +=1

            #print(line)

            try:

                splited_line = split_and_clear(line)

            except Exception as e:

                print(line,e)

               

            if len(splited_line) == 1 and splited_line[0] == '':

                continue

                #print(splited_line)

            try:

                request_url = splited_line[4].split(' ')[1]

            except:


                request_url = splited_line[4]

            request_time = float(splited_line[12])

            all_time += request_time


            if request_url not in data_dict:

                data_dict[request_url] = {"count":1,"request_time":[request_time]}

                data_list.append(request_url)

            else:

                data_dict[request_url]["count"]+=1

                data_dict[request_url]["request_time"].append(request_time)

        for item in data_list:

            cnt = data_dict[item]["count"]

            item_time = data_dict[item]["request_time"]

            time_sum = sum(item_time)

            data_dict[item] = {"count" : cnt, "count_perc" : round(cnt/all_count*100,3), "time_sum" : round(time_sum,3), "time_perc" : round(time_sum/all_time*100,3),"time_avg" : round(time_sum/cnt,3),"time_max": round(max(item_time),3),"time_med" : round(median(item_time),3)}
      

        with open(f'{config["REPORT_DIR"]}/{save_file_name}', 'w') as fp:

            json.dump(data_dict, fp,indent=4, separators=(',', ': '))  

 
    except TypeError as e:

        logger1.error(f"Ошибка типа данных: {e}")

    except NameError as e:

        logger1.error(f"Ошибка имени переменной: {e}")

    except FileNotFoundError as e:

        logger1.error(f"Ошибка файла: {e}")

    except ValueError:

        logger1.error("Некорректный ввод ")

    except KeyboardInterrupt:

        logger1.error(f'skrypt was interrupted by keybord')

        quit(1)

    except Exception as e:

        logger1.error(f"Произошло исключение: {e}")



if __name__ == '__main__':

    main(config)

