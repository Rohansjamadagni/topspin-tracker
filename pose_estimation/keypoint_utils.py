import cv2
import pandas as pd
import numpy as np

PARTS_LIST = [
	'r_wrist', 'l_wrist',
	'r_elbow', 'l_elbow',
	'r_shoulder', 'l_shoulder',
	'r_hip', 'l_hip',
	'r_knee', 'l_knee',
	'r_ankle', 'l_ankle',
]

LINES_LIST = [
    ['r_wrist', 'r_elbow'],
    ['l_wrist', 'l_elbow'],
    ['r_elbow', 'r_shoulder'],
    ['l_elbow', 'l_shoulder'],
    ['r_shoulder', 'l_shoulder'],
    ['r_shoulder', 'r_hip'],
    ['l_shoulder', 'l_hip'],
    ['r_hip', 'l_hip'],
    ['r_hip', 'r_knee'],
    ['l_hip', 'l_knee'],
    ['r_knee', 'r_ankle'],
    ['l_knee', 'l_ankle']
]

COLUMN_NAMES = [
    'R-wrist', 'L-wrist',
    'R-elbow', 'L-elbow',
    'R-shoulder', 'L-shoulder',
    'R-hip', 'L-hip',
    'R-knee', 'L-knee',
    'R-ankle', 'L-ankle',
]

# (B, G, R) cv2 colors
COLORS = {
    'BLUE': (255, 0, 0),
    'WHITE': (255, 255, 255),
    'YELLOW': (0, 255, 255),
    'RED': (0, 0, 255),
    'LIME': (0, 255, 0),
    'CYAN': (255, 255, 0),
    'PINK': (255, 0, 255),
}

class KeypointMapper:
    def __init__(
        self,
        video,
        csv_file,
        hand: str = 'right',
        filtered: bool = True,
        window_length: int = 13,
        polyorder: int = 2,
    ):
        self.df = pd.read_csv(csv_file, delimiter=',')

        self.hand = hand

        self.filtered = filtered
        self.window_length = window_length
        self.polyorder = polyorder

        self.__make_attributes()

        self.frame_counter = 0

        self.vid = cv2.VideoCapture(video)

    def __make_attributes(self):
        if self.filtered:
            if self.window_length != 13 and self.polyorder != 2:
                for part, column in zip(PARTS_LIST, COLUMN_NAMES):
                    setattr(self, part,
                        (np.array(self.df[f'{column}-X-Filtered-{self.window_length}-{self.polyorder}']),
                        np.array(self.df[f'{column}-Y-Filtered-{self.window_length}-{self.polyorder}'])))
            else:
                for part, column in zip(PARTS_LIST, COLUMN_NAMES):
                    setattr(self, part,
                        (np.array(self.df[f'{column}-X-Filtered']),
                        np.array(self.df[f'{column}-Y-Filtered'])))

        else:
            for part, column in zip(PARTS_LIST, COLUMN_NAMES):
                setattr(self, part,
                    (np.array(self.df[f'{column}-X']),
                    p.array(self.df[f'{column}-Y'])))

    def get_writer_object(self, output):
        vid_fps = self.vid.get(cv2.CAP_PROP_FPS)
        size = (int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output, fourcc, vid_fps, size)

        return out

    def get_next(self):
        ret, img = self.vid.read()

        if not ret:
            self.vid.release()
            return False, None
        else:
            self.frame_counter += 1

            if self.hand == 'left':
                img = cv2.flip(img, 1)

            return True, img

    def draw(self, img, pcolor=None, lcolor=None):
        print(f'Frame no: {self.frame_counter}')
        cv2.putText(img, f"FRAME {self.frame_counter}", (40,40), cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['RED'], thickness=2)

        self.__draw_circles(img, pcolor)
        self.__draw_lines(img, lcolor)

        return img

    def __draw_circles(self, img, color):
        for part in PARTS_LIST:
            # x, y = getattr(self, part)
            x = int(getattr(self, part)[0][self.frame_counter - 1])
            y = int(getattr(self, part)[1][self.frame_counter - 1])
            # x, y = int(x[self.frame_counter-1]), int(y[self.frame_counter-1])

            if color is None:
                if 'wrist' in part:
                    cv2.circle(img, (x, y), 6, COLORS['LIME'], -1)
                elif 'elbow' in part:
                    cv2.circle(img, (x, y), 6, COLORS['BLUE'], -1)
                elif 'shoulder' in part:
                    cv2.circle(img, (x, y), 6, COLORS['RED'], -1)
                elif 'hip' in part:
                    cv2.circle(img, (x, y), 6, COLORS['PINK'], -1)
                elif 'knee' in part:
                    cv2.circle(img, (x, y), 6, COLORS['BLUE'], -1)
                elif 'ankle' in part:
                    cv2.circle(img, (x, y), 6, COLORS['LIME'], -1)
            else:
                cv2.circle(img, (x, y), 6, COLORS[color], -1)

    def __draw_lines(self, img, color):
        for line_parts in LINES_LIST:
            part_1 = getattr(self, line_parts[0])
            part_2 = getattr(self, line_parts[1])

            x_1, y_1 = int(part_1[0][self.frame_counter-1]), int(part_1[1][self.frame_counter-1])
            x_2, y_2 = int(part_2[0][self.frame_counter-1]), int(part_2[1][self.frame_counter-1])

            if color is None:
                if line_parts == ['r_wrist', 'r_elbow'] or \
                   line_parts == ['r_elbow', 'r_shoulder']:
                    cv2.line(img, (x_1, y_1), (x_2, y_2), COLORS['YELLOW'],thickness=2, lineType=8)

                elif line_parts == ['l_wrist', 'l_elbow'] or \
                     line_parts == ['l_elbow', 'l_shoulder']:
                    cv2.line(img, (x_1, y_1), (x_2, y_2), COLORS['CYAN'],thickness=2, lineType=8)

                elif line_parts == ['r_shoulder', 'l_shoulder'] or \
                     line_parts == ['r_shoulder', 'r_hip'] or \
                     line_parts == ['l_shoulder', 'l_hip']:
                    cv2.line(img, (x_1, y_1), (x_2, y_2), COLORS['WHITE'], thickness=2, lineType=8)

                elif line_parts == ['r_hip', 'r_knee'] or \
                     line_parts == ['l_hip', 'l_knee']:
                    cv2.line(img, (x_1, y_1), (x_2, y_2), COLORS['CYAN'],thickness=2, lineType=8)
                elif line_parts == ['r_knee', 'r_ankle'] or \
                     line_parts == ['l_knee', 'l_ankle']:
                    cv2.line(img, (x_1, y_1), (x_2, y_2), COLORS['YELLOW'],thickness=2, lineType=8)
            else:
                cv2.line(img, (x_1, y_1), (x_2, y_2), COLORS[color], thickness=2, lineType=8)
