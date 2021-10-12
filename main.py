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
parser.add_argument('--out_movie', help='動画ファイルパス')
parser.add_argument('--out_file', help='分割ファイル場所', action='store_true')
parser.add_argument('--out_size', help='動画サイズ')
parser.add_argument('--fps', help='フレームレート', default=None, type=int)
parser.add_argument('--movie_extension', help='動画ファイル拡張子', default='mp4')
parser.add_argument('--img_extension', help='画像ファイル拡張子', default='png')

args = parser.parse_args()


def make_video_writer(fps, size):
    fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # ファイル形式(ここではmp4)
    video_writer = cv2.VideoWriter(f'{args.out_dir}/{args.out_movie}.{args.movie_extension}', fmt, fps, size)  # ライター作成

    return video_writer


def arg_value_check(val, default):
    if val is None:
        return default
    else:
        return val


def common_process(image, video_writer, fps, size):
    if args.out_size is not None:
        image = cv2.resize(image, eval(args.out_size))

    if args.out_movie is not None:
        if video_writer is None:
            video_writer = make_video_writer(fps, size)
            video_writer.write(image)
        else:
            video_writer.write(image)

    if args.show:
        cv2.imshow(f'window', image)
        cv2.waitKey(1)

    return video_writer


def directroy_method(directory_path):
    '''
    ディレクトリに対する処理
    :param directory_path: ディレクトリパス
    :return:
    '''
    file_path_list = os.listdir(directory_path)
    fps = arg_value_check(args.fps, 10)

    video_writer = None
    os.makedirs(args.out_dir, exist_ok=True)
    for file_path in tqdm(file_path_list):
        image = cv2.imread(directory_path + '\\' + file_path)
        size = arg_value_check(args.out_size, (image.shape[1], image.shape[0]))
        video_writer = common_process(image, video_writer, fps, size)

    if args.out_movie is not None:
        video_writer.release()


def video_method(movie_path):
    '''
    動画ファイルに対する処理
    :param movie_path: 動画ファイルパス
    :return:
    '''
    cap = cv2.VideoCapture(movie_path)

    size = arg_value_check(args.out_size,
                           (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    fps = arg_value_check(args.fps, int(cap.get(cv2.CAP_PROP_FPS)))
    end = arg_value_check(args.end, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))

    start = args.start
    step = args.step

    video_writer = None
    os.makedirs(args.out_dir, exist_ok=True)

    for _ in tqdm(range(0, start)):
        ret = cap.grab()
        if ret is False:
            break

    for i in tqdm(range(start, end)):  # フレーム数分回す

        if i % step is 0:
            ret, frame = cap.read()
            if ret is False:
                break

            video_writer = common_process(frame, video_writer, fps, size)

            if args.out_file:
                digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))
                file_name = re.split(r"[/\\.]", movie_path)
                cv2.imwrite(f'{args.out_dir}/{file_name[-2]}_{str(i).zfill(digit)}.{args.img_extension}', frame)

        else:
            ret = cap.grab()
            if ret is False:
                break

    if args.out_movie is not None:
        video_writer.release()


def image_method(file_path):
    image = cv2.imread(file_path)

    if args.show:
        cv2.imshow(f'window', image)
        cv2.waitKey(0)


def file_choice(file_path):
    input_ext = file_path.split('.')[-1]
    if input_ext == 'mp4':
        video_method(file_path)
    elif input_ext == 'avi':
        video_method(file_path)
    elif input_ext == 'jpg':
        image_method(file_path)
    elif input_ext == 'png':
        image_method(file_path)
    else:
        print('入力形式が違います')


def main():
    input_path = args.input
    if os.path.isdir(input_path):
        directroy_method(input_path)
    else:
        file_choice(input_path)


if __name__ == '__main__':
    main()
