import PySimpleGUI as sg
import cv2
import math
import matplotlib.pyplot as plt
import dataset_processor as dp
import image_processor as ip
import image_comparator as ic
from os.path import join

# WINDOW SETTINGS

WINDOW_DIM = (1200, 700)

def width(proportion):
  return math.floor(WINDOW_DIM[0] * proportion)

def height(proportion):
  return math.floor(WINDOW_DIM[1] * proportion)

# GLOBAL PARAMETERS

ROOT = "/Users/scott/Local/VS Code Projects/scotthallauer[cbir-wavelets]"

IMAGE_DIM = (128, 128)

DATABASE = dp.load_database(join(ROOT, "data/database.pickle"))

QUERY = {
  "image": {
    "path": join(ROOT, "data/query1.jpg"),
    "small": None,
    "large": None
  },
  "params": {
    "percent": 50,
    "threshold": 100000,
    "w_quad": [1,1,1,1],
    "w_comp": [1,2,2],
    "limit": 20
  }
}

RESULTS = []

BLANK_IMAGE = ip.resize_image(cv2.imread(join(ROOT, "data/blank.jpg")), (width(0.137), width(0.137)))

# FUNCTIONS

def load_query_image(values):
  QUERY["image"]["path"] = values["QUERY_PATH"]
  image = cv2.imread(QUERY["image"]["path"])
  QUERY["image"]["small"] = ip.resize_image(image, IMAGE_DIM)
  QUERY["image"]["large"] = ip.resize_image(image, (width(0.2), width(0.2)))

def display_query_image():
  WINDOW["QUERY_IMAGE"].update(data=ip.img2bytes(QUERY["image"]["large"]))

def load_query_param(values):
  QUERY["params"] = {
    "percent": int(values["PARAM_PERCENT"]),
    "threshold": int(values["PARAM_THRESHOLD"]),
    "w_quad": [
      int(values["PARAM_W11"]),
      int(values["PARAM_W12"]),
      int(values["PARAM_W21"]),
      int(values["PARAM_W22"])
    ],
    "w_comp": [
      int(values["PARAM_WC1"]),
      int(values["PARAM_WC2"]),
      int(values["PARAM_WC3"])
    ],
    "limit": int(values["PARAM_LIMIT"])
  }

def update_query(values):
  load_query_image(values)
  display_query_image()
  load_query_param(values)
  print(QUERY["params"])

def process_query():
  global RESULTS
  RESULTS.clear()
  query_vector = ip.img2vec(QUERY["image"]["path"], IMAGE_DIM)
  for candidate in DATABASE["image"]:
    passed, score = ic.pair2score(query_vector, candidate["vector"], QUERY["params"])
    if passed:
      RESULTS.append({
        "image": ip.resize_image(cv2.imread(join(ROOT, f"data/original/{candidate['file']}")), (width(0.137), width(0.137))),
        "score": score
      })
  RESULTS = sorted(RESULTS, key=lambda r: r["score"])

def display_results():
  for i in range(50):
    if i < min(len(RESULTS), QUERY["params"]["limit"]):
      WINDOW[f"RESULT_IMAGE_{i}"].update(data=ip.img2bytes(RESULTS[i]["image"]))
      WINDOW[f"RESULT_IMAGE_{i}"].set_tooltip(str(RESULTS[i]["score"]))
    else:
      WINDOW[f"RESULT_IMAGE_{i}"].update(data=ip.img2bytes(BLANK_IMAGE))
  if len(RESULTS) == 0:
    WINDOW["_EXPORT_"].update(visible=False)
  else:
    WINDOW["_EXPORT_"].update(visible=True)

def export_results():
  num_images = min(len(RESULTS), QUERY["params"]["limit"])
  if num_images > 0:
    cols = 5
    rows = math.ceil(num_images/cols)
    fig, axs = plt.subplots(rows, cols, figsize=(cols*3,rows*3), dpi=100)
    for i in range(rows*cols):
      if i >= num_images:
        axs[math.floor(i/5), i%5].axis('off')
      else:
        axs[math.floor(i/5), i%5].imshow(cv2.cvtColor(RESULTS[i]["image"], cv2.COLOR_BGR2RGB), interpolation="bilinear", cmap=plt.cm.gray)
        axs[math.floor(i/5), i%5].set_title(f"Image {i + 1}", fontsize=10)
        axs[math.floor(i/5), i%5].set_xticks([])
        axs[math.floor(i/5), i%5].set_yticks([])
    fig.tight_layout()
    plt.savefig(join(ROOT, "data/results.png"))

def display_stats():
  return None

# WINDOW LAYOUT

load_query_image({"QUERY_PATH": QUERY["image"]["path"]})

MATRIX_WEIGHT_LEFT_COLUMN = [
  [sg.Slider(default_value=QUERY["params"]["w_quad"][0], range=(1,5), size=(17,15), pad=(5, (5, 0)), orientation="h", key="PARAM_W11")],
  [sg.Text("w11", pad=(5, (0, 5)), justification="center", expand_x=True)],
  [sg.Slider(default_value=QUERY["params"]["w_quad"][2], range=(1,5), size=(17,15), pad=(5, (5, 0)), orientation="h", key="PARAM_W21")],
  [sg.Text("w21", pad=(5, (0, 5)), justification="center", expand_x=True)],
]

MATRIX_WEIGHT_RIGHT_COLUMN = [
  [sg.Slider(default_value=QUERY["params"]["w_quad"][1], range=(1,5), size=(17,15), pad=(5, (5, 0)), orientation="h", key="PARAM_W12")],
  [sg.Text("w12", pad=(5, (0, 5)), justification="center", expand_x=True)],
  [sg.Slider(default_value=QUERY["params"]["w_quad"][3], range=(1,5), size=(17,15), pad=(5, (5, 0)), orientation="h", key="PARAM_W22")],
  [sg.Text("w22", pad=(5, (0, 5)), justification="center", expand_x=True)],
]

COMPONENT_WEIGHT_FRAME = [
  [sg.Slider(default_value=QUERY["params"]["w_comp"][0], range=(1,5), size=(17,15), pad=(5, (5, 0)), orientation="h", key="PARAM_WC1")],
  [sg.Text("wc1", pad=(5, (0, 5)), justification="center", expand_x=True)],
  [sg.Slider(default_value=QUERY["params"]["w_comp"][1], range=(1,5), size=(17,15), pad=(5, (5, 0)), orientation="h", key="PARAM_WC2")],
  [sg.Text("wc2", pad=(5, (0, 5)), justification="center", expand_x=True)],
  [sg.Slider(default_value=QUERY["params"]["w_comp"][2], range=(1,5), size=(17,15), pad=(5, (5, 0)), orientation="h", key="PARAM_WC3")],
  [sg.Text("wc3", pad=(5, (0, 5)), justification="center", expand_x=True)],
]

SELECTION_SETTING_FRAME = [
  [sg.Slider(default_value=QUERY["params"]["percent"], range=(1,100), size=(17,15), pad=(5, (5, 0)), orientation="h", key="PARAM_PERCENT")],
  [sg.Text("percent", pad=(5, (0, 5)), justification="center", expand_x=True)],
  [sg.Slider(default_value=QUERY["params"]["threshold"], range=(50000,1000000), size=(17,15), pad=(5, (5, 0)), orientation="h", key="PARAM_THRESHOLD")],
  [sg.Text("threshold", pad=(5, (0, 5)), justification="center", expand_x=True)],
  [sg.Slider(default_value=QUERY["params"]["limit"], range=(1,50), size=(17,15), pad=(5, (5, 0)), orientation="h", key="PARAM_LIMIT")],
  [sg.Text("max results", pad=(5, (0, 5)), justification="center", expand_x=True)],
]

QUERY_COLUMN = [
  [
    sg.Text("Query", font=("Helvetica", 20, "bold")),
  ],
  [
    sg.Image(data=ip.img2bytes(QUERY["image"]["large"]), pad=(width(0.02), 5), key="QUERY_IMAGE")
  ],
  [
    sg.Text("Path"),
    sg.Input(QUERY["image"]["path"], size=(33, 1), enable_events=True, key="QUERY_PATH"),
    sg.Button("Load")
  ],
  [
    sg.Frame(title="Matrix Weights", font=("Helvetica", 11), layout=[[sg.Column(MATRIX_WEIGHT_LEFT_COLUMN), sg.Column(MATRIX_WEIGHT_RIGHT_COLUMN)]])
  ],
  [
    sg.Frame(title="Component Weights", font=("Helvetica", 11), pad=((5, 8), 5), layout=COMPONENT_WEIGHT_FRAME),
    sg.Frame(title="Selection Settings", font=("Helvetica", 11), pad=((8, 5), 5), layout=SELECTION_SETTING_FRAME),
  ],
  [
    sg.Button("Search", pad=(5, 10), expand_x=True)
  ]
]

RESULTS_COLUMN = [
  [
    sg.Text("Results", font=("Helvetica", 20, "bold"), key="RESULTS"),
    sg.Button("Export", visible=False, key="_EXPORT_")
  ]
]

for row in range(10):
  result_images = []
  for col in range(5):
    result_images.append(sg.Image(data=ip.img2bytes(BLANK_IMAGE), key=f"RESULT_IMAGE_{row*5 + col}"))
  RESULTS_COLUMN.append(result_images)


LAYOUT = [
  [
    sg.Column(QUERY_COLUMN, size=(width(0.25), height(1))),
    sg.VSeparator(),
    sg.Column(RESULTS_COLUMN, size=(width(0.75), height(1)), scrollable=True, vertical_scroll_only=True),
  ]
]

# RUN

WINDOW = sg.Window("CBIR Search Engine", LAYOUT)

while True:
  event, values = WINDOW.read()
  if event == "Exit" or event == sg.WIN_CLOSED:
    break
  if event == "Load":
    load_query_image(values)
    display_query_image()
  if event == "Search":
    update_query(values)
    process_query()
    print(len(RESULTS))
    display_results()
  if event == "_EXPORT_":
    export_results()

WINDOW.close()
