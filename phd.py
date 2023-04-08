import requests
import json

# 要查的一级学科专业名称和代码
major_codes = {
    '外国语言文学':'050200',
    '英语语言文学':'050201',
    '外国语言学及应用语言学':'050211',
}

requests.adapters.DEFAULT_RETRIES = 5
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5410.0 Safari/537.36'
}

# 获取拥有指定专业所有博士点的高校列表
def get_school_list(major_name):
    school_list = []
    start = 0
    url = 'https://yz.chsi.com.cn/bsmlcx/cx/listZsdw?start=%d&dwmc=&zymc=%s&dsxm=&xxfs=1&yjfxmc=&sfyjsy=false'
    first_url = url % (start, major_name)
    response = requests.get(first_url, headers = headers)
    if response.status_code == 200:
        data = response.json()
        msg = data['msg']
        for item in msg['list']:
            school_list.append(item)
        start += msg['size']
        while msg['curPage'] < msg['totalPage']:
            next_url = url % (start, major_name)
            response = requests.get(next_url, headers = headers)
            if response.status_code == 200:
                data = response.json()
                msg = data['msg']
                for item in msg['list']:
                    school_list.append(item)
            else:
                # 请求错误跳过
                break
    return school_list


# 获取指定学校指定专业的所有专业目录(来自不同院系)
def get_major_list(school_code, major_code):
    url = 'https://yz.chsi.com.cn/bsmlcx/cx/listYxsAndZyCollected?start=0&yxsdm=&zydm=%s&yjfxdm=&xxfs=&dsbh=&dwdm=%s' % (major_code, school_code)
    response = requests.get(url, headers = headers)

    if response.status_code == 200:
        data = response.json()
        return data['msg']['list']
    return []

   
# 获取指定学校指定院系指定专业的所有方向和导师
def get_major_details(school_code, college_code, major_code):
    url = 'https://yz.chsi.com.cn/bsmlcx/cx/listCxZymlCollected?dwdm=%s&yxsdm=%s&zydm=%s&yjfxdm=&xxfs=&dsbh=' % (school_code, college_code, major_code)
    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        data = response.json()
        return data['msg']
    return []

def main():
    for major_name, major_code in major_codes.items():
        major_result = []
        print('查询', major_name, major_code)
        # 院校列表
        schools = get_school_list(major_name)
        print('共%d所高校' % len(schools))
        for item in schools:
            school_name = item['dwmc']
            school_code = item['dwdm']
            school_result = {
                '高校代码':school_code,
                '高校名称':school_name,
                '院系所':[]
            }
            print('高校代码', school_name, school_code)
            print('  专业代码', major_name, major_code)
            # 先拿到高校指定专业代码的专业列表
            major_list = get_major_list(school_code, major_code)
            if len(major_list) > 0:
                for major in major_list:
                    # 拿到专业列表中的院系所代码
                    college_code = major['yxsdm']
                    college_name = major['yxsmc']
                    print('    院系所代码', college_code, college_name)
                    college_result = {
                        '院系所代码':college_code,
                        '院系所名称':college_name,
                        '方向':[]
                    }
                    # 获取对应院系该专业所有方向信息
                    major_details = get_major_details(school_code, college_code, major_code)
                    for major_detail in major_details:
                        college_result['方向'].append({
                            '方向代码':major_detail['yjfxdm'],
                            '方向名称':major_detail['yjfxmc'],
                            '导师':major_detail['dsxm']
                        })
                        print('      方向', major_detail['yjfxdm'], major_detail['yjfxmc'], '导师', major_detail['dsxm'])
                    school_result['院系所'].append(college_result)
            else:
                pass
                # print(school_code, '没有该专业', major_code)
            major_result.append(school_result)
        # print(major_result)
        with open('%s.json' % major_name, 'w', encoding='utf8') as f:
            json.dump(major_result, f, ensure_ascii=False, indent=4)
            f.close()


if __name__== "__main__" :
    main()