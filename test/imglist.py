# YES PLAN
import requests


imgs_string = """https://terraingis.ru/wp-content/uploads/2013/05/eskiz.jpg
https://knin.ua/uploads/7/35230-tehnicheskij_plan_12.jpg
https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsNtxBMb8ON9UuEroCzwcNHSIeW0XD-JnDSNMNh5DTpB_7LUVMuUou_4I47EF5I6Tpr-M&usqp=CAU
https://vektor-kadastr.ru/thumb/2/nZtbZtn-81U6JuFnALGnzg/1240r/d/tekhnicheskiy-plan-pomeshcheniya.jpg
https://studfile.net/html/2706/608/html_vVZXVbT3Lu.UnVK/img-FAG_bS.png
https://www.neoluxe.ru/upload/medialibrary/1e9/1e91fc5d334573d3d446984b7d3e1c55.jpg
https://www.edrawsoft.com/ru/floorplan/images/office-layout-sample.png
https://photogrammetria.ru/uploads/posts/2023-04/plan-zdanija-obmernyj-chertezh-po-rezultatam-provedenija-arhitekturnyh-obmerov.jpg
https://www.anfilada-design.ru/test/wp-content/uploads/2018/06/vid-sverhu-3-1024x667.jpg
https://img.freepik.com/free-vector/house-plan-construction-with-blueprint_23-2148309840.jpg?size=338&ext=jpg&ga=GA1.1.1413502914.1725148800&semt=ais_hybrid
https://www.allkresla.biz/upload/iblock/184/dizayn_366.jpg"""

imgs = imgs_string.split('\n')
# download images and save them to the folder test/plan named as 001_plan.jpg, 002_plan.jpg, etc.
for i, img_url in enumerate(imgs):
    response = requests.get(img_url)
    with open(f'datasets/cian-911/test/plan/{str(i + 1).zfill(3)}_plan.jpg', 'wb') as f:
        f.write(response.content)