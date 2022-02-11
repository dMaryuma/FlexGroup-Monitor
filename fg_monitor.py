#!/usr/bin/python3
import requests,json 
from netapp_ontap import HostConnection,utils,config
from netapp_ontap.resources import Volume, CLI
import base64
import statistics
import sys
import getopt

def obfuscate(plainText):
    plainBytes = plainText.encode('ascii')
    encodedBytes = base64.b64encode(plainBytes)
    encodedText = encodedBytes.decode('ascii')
    return encodedText


def deobfuscate(obfuscatedText):
    obfuscatedBytes = obfuscatedText.encode('ascii')
    decodedBytes = base64.b64decode(obfuscatedBytes)
    decodedText = decodedBytes.decode('ascii')
    return decodedText

def volume_number_of_files(vol_name,svm_name):
    num_files = Volume.find(name=vol_name,svm=svm_name,fields='name,svm,files')
    return num_files
def get_constituent_volumes(vol_name,svm_name):
    vol_name = vol_name+"__*"
    response = CLI().execute("volume show", vserver=svm_name, volume=vol_name,is_constituent=True,fields='vserver,volume,used')
    json_dump = json.dumps(response.http_response.json())
    json_output = json.loads(json_dump)
    json_output = json_output['records']
    return json_output
def get_avg_size_constituent_volumes(constituent_volumes):
    avg = 0
    for dc in constituent_volumes:
        avg += dc['used']
    return avg/(len(constituent_volumes))
def get_standard_deviation_size_constituent_volumes(constituent_volumes):
    deviation = []
    for dc in constituent_volumes:
        deviation.append(dc['used'])
    return statistics.stdev(deviation)



################################ MAIN #########################
def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hv:s:i:u:p:",["vol_name=","svm_name=","host_ip=","na_user=","na_pass"])
    except getopt.GetoptError:
        print ('fg_monitor.py -v <vol_name> -s <svm_name> -i <host_ip> -u <na_user> -p <na_pass>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('fg_monitor.py -v <vol_name> -s <svm_name> -i <host_ip> -u <na_user> -p <na_pass>')
            sys.exit()
        elif opt in ("-v", "--vol_name"):
            vol_name = arg
        elif opt in ("-s", "--svm_name"):
            svm_name = arg
        elif opt in ("-i", "--host_ip"):
            host_ip = arg
        elif opt in ("-u", "--na_user"):
            na_user = arg
        elif opt in ("-p", "--na_pass"):
            na_pass = arg
    try:
        conn = HostConnection(host_ip, username=na_user,password=na_pass, verify=False)
        config.CONNECTION = conn
        number_of_files = volume_number_of_files(vol_name,svm_name)
        # check if number of files used bigger then 1.8 Billiad on Flexgroup
        if (number_of_files['files']['used'] > 1800000000): 
            print("number of inodes on volume '{}' on vserver '{}' is greater then 1.8 Billiad (best practice). can result performance issues".format(vol_name,svm_name))
        constituent_volumes = get_constituent_volumes(vol_name,svm_name)
        # check if any constituent volume is greater then 60TB used size
        for dc in constituent_volumes:
            if (dc['used'] > 65970697666560): 
                print("constituent volume '{}', in vserver '{}' used size '{} TB' is greater then best practice value of 60TB, should consider rebalance constituent volumes".format(dc['volume'],dc['vserver'],round(int(dc['used'])/1024/1024/1024/1024),3))
        # Print Avarage size of dc:
        average_size_of_constituents = get_avg_size_constituent_volumes(constituent_volumes)
        print ("Average size of constituent volumes on volume '{}' on Vserver '{}' is '{}' TB".format(vol_name,svm_name,round(average_size_of_constituents/1024/1024/1024/1024),3))
        # Print Standard Deviation of used size
        standard_deviation = get_standard_deviation_size_constituent_volumes(constituent_volumes)
        print ("Standard Deviation of volume '{}' on vserver '{}' is '{}'".format(vol_name,svm_name,standard_deviation))
    except Exception as e:
        print(e)
if __name__ == "__main__":
    main(sys.argv[1:])