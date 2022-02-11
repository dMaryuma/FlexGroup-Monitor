# FlexGroup-Monitor
Flexgroup best practice monitor 

This is Flexgroup monitor using 'netapp_ontap' NetApp python library with REST Api methods 

## Script contains:
* raise warning - if Flexgroup volume contains used inode aboe 1.8 Biliiard.
* raise warning - for each constituent volume above 60TB used size.
* print average used size of all DCs.
* print standard deviation of all DCs.

## Requirements
python 3.8.0+

## Installation
```bash
pip install netapp_ontap
```
can obtain from https://pypi.org/project/netapp-ontap/

## Usage
```bash
python ./fg_monitor.py -v fg1 -s svm1 -i 192.168.0.xxx -u admin -p netapp23
```
-v | --vol_name   
-s | --svm_name  
-i | --host_ip  
-u | --na_user  
-p | --na_pass  


