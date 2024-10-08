# NO PLAN
import requests


imgs_string = """https://moszem.com/upload/medialibrary/c49/zu16caffch89g8h5ljf90gi9d2nhyf18.png
https://www.moedelo.org/storage/uploads/club/article-knowledge/full/91214_f589c012a1bfe41f16279a5c322e9020.png
https://static.insales-cdn.com/files/1/4093/20271101/original/5.jpg
https://www.gazeta.uz/media/img/2019/01/vXTCpF15483179356022_l.jpg
https://officenavigator.ru/upload/resize_cache/iblock/051/77uzl644794zcuuoqf4tiohvd7k9t32z/1350_700_2/vibrat_ofis.jpg
https://content.cdn-cian.ru/realty/journal/320894/970413886.jpg
https://www.avclub.pro/image/cache/catalog/dizajnbeznazvanija%282%29-855x580.png
https://storage.yandexcloud.net/incrussia-prod/wp-content/uploads/2022/10/Inv_5.jpg
https://upinc.ru/wp-content/uploads/2021/03/kak-podobrat-ofis-menedzhera-1.jpg
https://interior-design.moscow/wp-content/uploads/2017/05/dizayn-ofisa-v-sovremennom-stile-foto-02.jpg
https://teletype.in/files/45/78/4578beaa-4779-425d-871c-85db435de3b9.jpeg
https://cdn5.vedomosti.ru/image/2020/8k/1f8a/original-1v.jpg
https://profashion.ru/upload/iblock/610/wildberries_820.JPG
https://cdn5.vedomosti.ru/image/2024/3q/15rybq/original-1i55.jpg"""

imgs = imgs_string.split('\n')
# download images and save them to the folder test/no_plan named as 001_no_plan.jpg, 002_no_plan.jpg, etc.
for i, img_url in enumerate(imgs):
    response = requests.get(img_url)
    with open(f'datasets/cian-911/test/no_plan/{str(i + 1).zfill(3)}_no_plan.jpg', 'wb') as f:
        f.write(response.content)