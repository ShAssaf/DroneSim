import cv2

# missions = pickle.load(open(Paths.ENVIRONMENT_PATHS, 'rb'))
missions = [[(3420, 4540, 0), (3420, 4540, 10), (3410, 4530, 20), (3400, 4520, 30),
                                 (3390, 4510, 40), (3380, 4500, 50), (3370, 4490, 60), (3360, 4480, 70),
                                 (3360, 4470, 80), (3360, 4460, 90), (3370, 4450, 100), (3370, 4440, 110),
                                 (3380, 4430, 120), (3380, 4420, 130), (3380, 4410, 140), (3390, 4400, 150),
                                 (3380, 4390, 160), (3380, 4380, 170), (3370, 4370, 180), (3370, 4360, 190),
                                 (3360, 4350, 200), (3360, 4340, 210), (3370, 4330, 220), (3360, 4320, 230),
                                 (3350, 4310, 240), (3350, 4300, 250), (3350, 4290, 260), (3350, 4280, 270),
                                 (3350, 4270, 280), (3340, 4260, 290), (3350, 4250, 300), (3360, 4240, 310),
                                 (3360, 4230, 320), (3370, 4220, 330), (3370, 4210, 340), (3380, 4200, 340),
                                 (3380, 4190, 350), (3380, 4180, 360), (3390, 4170, 350), (3380, 4160, 360),
                                 (3370, 4150, 350), (3360, 4140, 350), (3350, 4130, 350), (3360, 4120, 350),
                                 (3370, 4110, 350), (3380, 4100, 340), (3380, 4090, 330), (3380, 4080, 340),
                                 (3380, 4070, 350), (3380, 4060, 350), (3390, 4050, 340), (3390, 4040, 340),
                                 (3380, 4030, 340), (3370, 4020, 340), (3370, 4010, 330), (3360, 4000, 320),
                                 (3360, 3990, 330), (3370, 3980, 340), (3380, 3970, 350), (3380, 3960, 360),
                                 (3380, 3950, 370), (3390, 3940, 360), (3380, 3930, 350), (3380, 3920, 360),
                                 (3380, 3910, 370), (3390, 3900, 360), (3400, 3890, 370), (3410, 3880, 380),
                                 (3420, 3870, 390), (3430, 3860, 380), (3440, 3850, 380), (3430, 3840, 380),
                                 (3420, 3830, 390), (3430, 3820, 400), (3440, 3810, 400), (3450, 3800, 390),
                                 (3450, 3790, 390), (3460, 3780, 380), (3470, 3770, 380), (3460, 3760, 390),
                                 (3470, 3750, 380), (3470, 3740, 380), (3460, 3730, 390), (3470, 3720, 390),
                                 (3460, 3710, 380), (3470, 3700, 390), (3460, 3690, 400), (3450, 3680, 390),
                                 (3460, 3670, 400), (3450, 3660, 390), (3450, 3650, 380), (3450, 3640, 370),
                                 (3450, 3630, 360), (3440, 3620, 350), (3430, 3610, 340), (3420, 3600, 330),
                                 (3430, 3590, 320), (3420, 3580, 310), (3410, 3570, 300), (3410, 3560, 290),
                                 (3410, 3550, 280), (3400, 3540, 270), (3410, 3530, 260), (3410, 3520, 250),
                                 (3420, 3510, 240), (3410, 3500, 230), (3410, 3490, 220), (3400, 3480, 210),
                                 (3410, 3470, 200), (3420, 3460, 190), (3410, 3450, 180), (3420, 3440, 170),
                                 (3410, 3430, 160), (3420, 3420, 150), (3420, 3410, 140), (3410, 3400, 130),
                                 (3410, 3390, 120), (3410, 3380, 110), (3410, 3370, 100), (3400, 3360, 90),
                                 (3390, 3350, 80), (3380, 3340, 70), (3370, 3330, 60), (3360, 3320, 50),
                                 (3350, 3310, 40), (3340, 3300, 30), (3330, 3290, 20), (3320, 3280, 10),
                                 (3320, 3280, 0)]]

for idx, m in enumerate(missions):
    image = cv2.imread(
"/Users/shlomoassaf/reps/DroneSim/data/maps/rescaled_map_1_pixel_per_1_meter_building_deionised.jpg",
cv2.IMREAD_GRAYSCALE)
image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

for i in range(len(m) - 1):
    start_point = (int(m[i][0]), int(m[i][1]))
    end_point = (int(m[i + 1][0]), int(m[i + 1][1]))
    color = (0, 125, m[i][2] * 10)  # BGR color (red in this case)
    thickness = 15
    cv2.line(image, start_point, end_point, color, thickness)
cv2.imwrite(f"data/path_paint_examples/path_example_N{idx}.png", image)
# from src.utils.Consts import Consts
#
# # data = {"start": (2500, 2400, 0), "target": (1000, 2500, 0)}
# # response = requests.post(f"http://127.0.0.1:{Consts.GRAPH_PORT}/graph", json=data)
#
# data2 = {"pos": {'x':0,'y':0,'z':0}}
# response2 = requests.post(f"http://127.0.0.1:{Consts.ENV_PORT}/get_close_env",json=data2)
#
# # if response.status_code == 200:
# #     result = response.json()["result"]
# #     print("Result:", result)
# # else:
# #     print("Error:", response.json()["error"])
#
# if response2.status_code == 200:
#     result = response2.json()["result"]
#     print("Result:", result)
# else:
#     print("Error:", response2.json()["error"])
# points = Path.get_path_from_server((500,500,0), (1000, 2500, 0))
# points = [((int(i[0]), int(i[1])),i[2]) for i in points]
# image = cv2.imread("/Users/shlomoassaf/reps/DroneSim/data/part_new_york_3kmm.jpg", cv2.IMREAD_GRAYSCALE)
# image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
#
# # Draw a line between the pixel coordinates
# for i in range(len(points) - 1):
#     start_point = points[i][0]
#     end_point = points[i + 1][0]
#     color = (0, 125, points[i][1]*10)  # BGR color (red in this case)
#     thickness = 15
#     cv2.line(image, start_point, end_point, color, thickness)
#
# # Save or display the image
# cv2.imwrite(f"data/path_paint_examples/path_example_{p}.png", image)
# pass
