import pickle
import cv2
from src.utils.Consts import Paths


missions = pickle.load(open(Paths.ENVIRONMENT_PATHS, 'rb'))
for idx, m in enumerate(missions):
    image = cv2.imread("/Users/shlomoassaf/reps/DroneSim/data/part_new_york_3kmm.jpg", cv2.IMREAD_GRAYSCALE)
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Draw a line between the pixel coordinates
    for i in range(len(m[2]) - 1):
        start_point = m[2][i][:2][::-1]
        end_point = m[2][i + 1][:2][::-1]
        color = (0, 125, m[2][i][2] * 10)  # BGR color (red in this case)
        thickness = 15
        cv2.line(image, start_point, end_point, color, thickness)
    cv2.imwrite(f"data/path_paint_examples/path_example_{idx}.png", image)
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