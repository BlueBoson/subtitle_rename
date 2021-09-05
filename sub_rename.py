import os
import re
import argparse
import shutil


parser = argparse.ArgumentParser()
parser.add_argument('-l', '--loose', action='store_true',\
    help='allow partial regex match')
parser.add_argument('-y', '--yes', action='store_true',\
    help='skip confirmation')
parser.add_argument('-v', '--verbose', action='store_true',\
    help='print detailed log')
parser.add_argument('-g', '--remove', action='store_true',\
    help='remove original files')
parser.add_argument('-s', '--src_dir', type=str, default='.',\
    help='directory where original subtitles are stored (default: current directory)')
parser.add_argument('-d', '--dst_dir', type=str, default='.',\
    help='directory where renamed subtitles will be stored (default: current directory)')
parser.add_argument('-r', '--relative_dst_dir', type=str, default='',\
    help='directory where renamed subtitles will be stored, relative to src_dir')
parser.add_argument('-p', '--pattern', type=str, default='',\
    help='regex pattern for subtitles need to be renamed, regex group is support')
parser.add_argument('-n', '--name', type=str, default='',\
    help='new name for subtitles, {group index|name} for regex group')


if __name__ == '__main__':
    args = parser.parse_args()

    def info(*_args, **kwargs):
        if args.verbose:
            print(*_args, **kwargs)

    if not args.pattern:
        args.pattern = input('please input regex pattern for subtitles need to be renamed, regex group is support:')
    if not args.name:
        args.name = input('please input new name for subtitles, {num} for regex group:')
    if args.relative_dst_dir:
        args.dst_dir = os.path.join(args.src_dir, args.relative_dst_dir)

    r = re.compile(args.pattern)
    names = {}
    for file in os.listdir(args.src_dir):
        m = r.search(file) if args.loose else r.match(file)
        if not m:
            continue
        group_list = [m.group(0)] + list(m.groups())
        names[file] = args.name.format(*group_list, **m.groupdict())
    
    if not names:
        print('no file detected')
        exit(0)
    print(f'\n{len(names)} file(s) detected:')
    for file, name in names.items():
        print(f'\t{file}')
        print(f'\t\t-> {name}')
    print(f'new files will be saved to {os.path.abspath(args.dst_dir)}')
    while True:
        ans = input('confirm?(y/n): ')
        if ans in ['n', 'no']:
            exit(0)
        elif ans in ['y', 'yes']:
            break
    os.makedirs(args.dst_dir, exist_ok=True)
    fails = 0
    for file, name in names.items():
        try:
            cfile = os.path.join(args.src_dir, file)
            cname = os.path.join(args.dst_dir, name)
            shutil.copyfile(cfile, cname)
        except Exception as e:
            print(f'rename {file} failed: {e}')
            fails += 1
        if args.remove:
            try:
                os.remove(cfile)
            except Exception as e:
                print(f'remove {file} failed: {e}')
    print(f'{len(names)-fails} success, {fails} failed')