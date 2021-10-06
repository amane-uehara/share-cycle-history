import json
import sys
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime


EVENT_NO_DICT = {
  'login'           : '21401',
  'register'        : '21403',
  'd_account_login' : '21405',
  'billing_amount'  : '21605',
  'conf_chg'        : '21606',
  'logout'          : '21607',
  'select_cycle'    : '21611',
  'from_port'       : '21614'
}


def main(args):
  if len(args) != 5:
    sys.exit("ERROR: invalid argument number\nUSAGE (2021/03/01-2021/03/31) : python3 fetch_history.py url member_id password 2021 3")
  url       = args[0]
  member_id = args[1]
  password  = args[2]
  year      = int(args[3])
  month     = int(args[4])

  if year < 1900 or year > 3000 or month < 1 or month > 12:
    sys.exit("ERROR: invalid argument number\nUSAGE (2021/03/01-2021/03/31) : python3 fetch_history.py url member_id password 2021 3")

  login_dict = open_login_page(url, member_id, password)
  menu_soup  = send_post(url, login_dict)
  menu_forms = find_all_form(menu_soup)
  history    = open_history_page(url, menu_forms, year, month)
  print(json.dumps(history, separators=(',', ':'), ensure_ascii=False))
  send_logout_post(url, menu_forms)


def open_login_page(url, member_id, password):
  soup = send_post(url, {})
  all_form = find_all_form(soup)

  login_dict = all_form[EVENT_NO_DICT['login']]
  login_dict['MemberID'] = member_id
  login_dict['Password'] = password

  return login_dict


def open_history_page(url, menu_forms, year, month):
  post_dict = menu_forms[EVENT_NO_DICT['billing_amount']]
  post_dict['StartYear']  = str(year)
  post_dict['StartMonth'] = str(month)
  soup = send_post(url, post_dict)
  raw_table = get_history_raw_table(soup)
  return parse_history_raw_table(raw_table)


def get_history_raw_table(soup):
  tr_list = []
  for f in soup.find_all('table'):
    if f.get('class') is None:
      continue
    if f.get('class')[0] != 'rnt_ref_table':
      continue

    for tr in f.find_all('tr'):
      td_list = []
      for td in tr.find_all('td'):
        text = td.get_text()
        td_list.append(text)
      tr_list.append(td_list)
    break

  return tr_list


def parse_history_raw_table(history_raw_table):
  ret = []
  for r in history_raw_table:
    if r[1] is None:
      continue

    if ':' not in r[1]:
      continue

    bgn = {}
    bgn_dt = r[1].replace('\n','')
    bgn['dt'] = format(datetime.strptime(bgn_dt + ':00', '%Y/%m/%d %H:%M:%S'), '%Y%m%d%H%M%S')
    bgn_name = r[2].rstrip().lstrip().split('\n')
    bgn['symbol']  = bgn_name[0].split('.')[0]
    bgn['name_ja'] = ''.join(bgn_name[0].split('.')[1:])
    bgn['name_en'] = ''.join(bgn_name[1].split('.')[1:])

    end = {}
    end_dt = r[4].replace('\n','')
    end['dt'] = format(datetime.strptime(end_dt + ':00', '%Y/%m/%d %H:%M:%S'), '%Y%m%d%H%M%S')
    end_name = r[5].rstrip().lstrip().split('\n')
    end['symbol']  = end_name[0].split('.')[0]
    end['name_ja'] = ''.join(end_name[0].split('.')[1:])
    end['name_en'] = ''.join(end_name[1].split('.')[1:])

    cost = r[6].replace('\n','').replace(u'円','')

    ret.append({'bgn':bgn, 'end':end, 'cost':cost})
  return ret


def send_logout_post(url, menu_forms):
  logout_dict = menu_forms[EVENT_NO_DICT['logout']]
  send_post(url, logout_dict)


def send_post(url, post_dict):
  login_post = urllib.parse.urlencode(post_dict).encode()
  req = urllib.request.Request(url, login_post)
  with urllib.request.urlopen(req) as res:
    html = res.read()
  soup = BeautifulSoup(html, 'html.parser')
  return soup


def find_all_form(soup):
  ret = {}
  for f in soup.find_all('form'):
    f_name = 'NULL'
    form_dict = {}
    for i in f.find_all('input'):
      name  = i.get('name')
      value = i.get('value')
      if name is None:      continue
      if name == 'EventNo': f_name = value
      form_dict[name] = i.get('value')
    ret[f_name] = form_dict
  return ret


if __name__ == '__main__':
  main(sys.argv[1:])
