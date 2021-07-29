import os
import re
import cv2
import argparse
from tqdm import tqdm

SPACER = '\\'

parser = argparse.ArgumentParser(description='自作画像ライブラリ的な奴')

parser.add_argument('--input', help='入力ファイルパス', required=True)

parser.add_argument('--start', help='開始フレーム番号', default=0, type=int)
parser.add_argument('--end', help='終了フレーム番号', type=int)
parser.add_argument('--step', help='スキップフレーム', default=1, type=int)

parser.add_argument('--show', help='表示フラグ', action='store_true')


parser.add_argument('--out_dir', help='出力ディレクトリ', default='./')
parser.add_argument('--out_movie', help='動画出力場所')
parser.add_argument('--out_file', help='分割ファイル場所', type=bool)
parser.add_argument('--out_size', help='動画サイズ')
parser.add_argument('--movie_extension', help='動画ファイル拡張子', default='mp4')
parser.add_argument('--img_extension', help='画像ファイル拡張子', default='png')

args = parser.parse_args()


def image_method(args, file_path):
    image = cv2.imread(file_path)

    if args.show:
        cv2.imshow(f'window', image)
        cv2.waitKey(0)


def video_method(args, file_path):
    cap = cv2.VideoCapture(file_path)
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    start = args.start
    end = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if args.end is not None:
        end = args.end
    step = args.step

    video_writer = None
    os.makedirs(args.out_dir, exist_ok=True)

    if args.out_movie is not None:
        fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # ファイル形式(ここではmp4)
        if args.out_size is not None:
            size = eval(args.out_size)
        video_writer = cv2.VideoWriter(f'{args.out_dir}/{args.out_movie}.{args.movie_extension}', fmt, int(cap.get(cv2.CAP_PROP_FPS)), size)  # ライター作成

    for _ in tqdm(range(0, start)):
        ret = cap.grab()
        if ret is False:
            break

    for i in tqdm(range(start, end)):  # フレーム数分回す

        ret = cap.grab()

        if ret is False:
            break

        if i % step is 0:
            ret, frame = cap.read()
            if ret is False:
                break

            if args.show:
                cv2.imshow(f'window', frame)
                cv2.waitKey(1)

            if args.out_size is not None:
                frame = cv2.resize(frame, size)

            if args.out_movie is not None:
                video_writer.write(frame)

            if args.out_file:
                digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))
                file_name = re.split(r"[/\\.]", file_path)
                cv2.imwrite(f'{args.out_dir}/{file_name[-2]}_{str(i).zfill(digit)}.{args.img_extension}', frame)
        else:
            ret = cap.grab()
            if ret is False:
                break

    if args.out_movie is not None:
        video_writer.release()


def file_choice(file_path):
    input_ext = file_path.split('.')[-1]
    if input_ext == 'mp4':
        video_method(args, file_path)
    elif input_ext == 'avi':
        video_method(args, file_path)
    elif input_ext == 'jpg':
        image_method(args, file_path)
    elif input_ext == 'png':
        image_method(args, file_path)
    else:
        print('入力形式が違います')


def main(args):
    input_path = args.input

    if os.path.isdir(input_path):
        file_path_list = os.listdir(input_path)
        for file_path in file_path_list:
            file_choice(input_path + '\\' + file_path)
    else:
        file_choice(input_path)


if __name__ == '__main__':
    main(args)
