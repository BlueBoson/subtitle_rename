import os
import re
import argparse
import shutil

import _locale
_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

parser = argparse.ArgumentParser(
    fromfile_prefix_chars='+',
    usage='%(prog)s [+file] [options]',
    description='Use [+file] to read arguments from file (recommanded)')

general_group = parser.add_argument_group('general options')
general_group.add_argument(
    '-y', '--yes', 
    action='store_true',
    help='ignore confirmation')
general_group.add_argument(
    '-t', '--test', 
    action='store_true',
    help='print rename intention and exit')
general_group.add_argument(
    '--overwrite', 
    action='store_true',
    help='force overwrite if file exists')
general_group.add_argument(
    '--remove', 
    action='store_true',
    help='remove original files after rename')

path_group = parser.add_argument_group('path arguments')
path_group.add_argument(
    '-s', '--src-dir', 
    dest='src_dir', metavar='SRC-DIR', type=str,
    help='path to files read (default: cwd)')
path_group.add_argument(
    '-d', '--dst-dir', 
    dest='dst_dir', metavar='DST-DIR', type=str,
    help='path to files stored (default: SRC-DIR)')

pattern_group = parser.add_argument_group('pattern arguments')
pattern_group.add_argument(
    '--with-ext',
    dest='with_ext', action='store_true',
    help='provide extension in input and correspond patterns (default: match all extensions)')
pattern_group.add_argument(
    '-i', '--input-pattern',
    dest='input_pattern', metavar='INPUT-PATTERN', type=str,
    help=(
        'name pattern for input files. '
        'substrs in parentheses are treated as regex, so use escape for raw parentheses in filename, '
        'use group with (?P<group>...)'))
pattern_group.add_argument(
    '-o', '--output-pattern-no-ext',
    dest='output_pattern', metavar='OUTPUT-PATTERN', type=str,
    help=(
        '[input-only mode] output format pattern (without ext) using only literal and input group, ' 
        '{group index|name} for group in INPUT-PATTERN, '
        'python3 format grammer is supported'))
pattern_group.add_argument(
    '-c', '--correspond-pattern',
    dest='correspond_pattern', metavar='CORRESPOND-PATTERN', type=str,
    help=(
        '[with-correspond-file mode] name pattern for correspong files, similar to INPUT-PATTERN. '
        'when set CORRESPOND-PATTERN, input and correspong pattern will be '
        'matched by named groups'))

def find_reg_parens(string):
    slices = []
    count = 0
    prev_escape = False
    for i, c in enumerate(string):
        if c == '(' and not prev_escape:
            if count == 0:
                slices.append([i, i])
            count += 1
        elif c == ')' and not prev_escape:
            count -= 1
            if count == 0:
                slices[-1][-1] = i
        prev_escape = (c == '\\')
    return slices

if __name__ == '__main__':
    ns = argparse.Namespace()
    
    parser.parse_args(namespace=ns)
    
    if not ns.input_pattern:
        print('input pattern is required')
        exit(1)
        
    if not ns.output_pattern and not ns.correspond_pattern:
        print('output pattern or correspond pattern is required')
        exit(1)
        
    if ns.output_pattern and ns.correspond_pattern:
        print('output pattern and correspond pattern cannot be set at the same time')
        exit(1)
        
    if not ns.dst_dir:
        ns.dst_dir = ns.src_dir
        
    def escape_regex(raw_sub):
        my_reserved = ['\\', '(', ')']
        reg_reserved = {'\\', '.', '+', '*', '?', '^', '$', '(', ')', '[', ']', '{', '}', '|'}
        ret = []
        i = 0
        while i < len(raw_sub):
            if raw_sub[i] == '\\' and i < len(raw_sub) - 1 and raw_sub[i+1] in my_reserved:
                ret.append(raw_sub[i:i+2])
                i += 2
            elif raw_sub[i] in reg_reserved:
                ret.append('\\' + raw_sub[i])
                i += 1
            else:
                ret.append(raw_sub[i])
                i += 1
        ret = ''.join(ret)
        return ret
        
    for regex_pattern_name in ['input_pattern', 'correspond_pattern']:
        pattern = getattr(ns, regex_pattern_name, None)
        if pattern:
            slices = find_reg_parens(pattern)
            slices.append([len(pattern), len(pattern)])
            new_pattern = []
            cur = 0
            for s, e in slices:
                raw_sub = pattern[cur:s]
                new_pattern.append(escape_regex(raw_sub))
                new_pattern.append(pattern[s:e+1])
                cur = e + 1
            new_pattern = ''.join(new_pattern)
            if not new_pattern.endswith('$'):
                new_pattern += '$'
            setattr(ns, regex_pattern_name, new_pattern)
    
    data = {}
    success = set()
    input_pattern = re.compile(ns.input_pattern)
    for file in os.listdir(ns.src_dir):
        f, e = os.path.splitext(file)
        if ns.with_ext:
            m = input_pattern.match(file)
        else:            
            m = input_pattern.match(f)
        if not m:
            continue
        data[file] = {'ext': e, 'groups': m.groupdict()}
    
    if ns.output_pattern:
        for file, attrib in data.items():
            attrib['output'] = ns.output_pattern.format(**attrib['groups']) + attrib['ext']
            success.add(file)
            
    elif ns.correspond_pattern:
        correspond_pattern = re.compile(ns.correspond_pattern)
        for cfile in os.listdir(ns.src_dir):
            cf, e = os.path.splitext(cfile)
            m = correspond_pattern.match(cf)
            if not m:
                continue
            for file, attrib in data.items():
                groupd = m.groupdict()
                for k, v in attrib['groups'].items():
                    if v != groupd.get(k, None):
                        break
                else:
                    # if file in success:
                    #     print('ambiguous rename for: {}, ignore'.format(file))
                    # else:
                    #     attrib['output'] = cf + attrib['ext']
                    #     attrib['groups'] = groupd     
                    #     success.add(file)    
                    attrib['output'] = cf + attrib['ext']
                    attrib['groups'] = groupd     
                    success.add(file)
                    break       
                    
    else:
        print('should not reach here')
        exit(1)
        
    success = sorted(list(success))
    
    if not success:
        print('no files to rename')
        exit(0)
    
    for file in success:
        print(file, '->', data[file]['output'])
        
    if ns.test:
        exit(0)
        
    if not ns.yes:
        cmd = input('confirm? (y/n)')
        if cmd not in ['y', 'Y']:
            print('aborted')
            exit(0)
            
    for file in success:
        attrib = data[file]
        src_path = os.path.join(ns.src_dir, file)
        dst_path = os.path.join(ns.dst_dir, attrib['output'])
        if os.path.exists(dst_path):
            print('file already exists:', dst_path)
            if not ns.overwrite:
                print('skip')
                continue
            else:
                print('overwrite')
        shutil.copy(src_path, dst_path)
        print('done:', src_path, '->', dst_path)
        if ns.remove:
            os.remove(src_path)
            print('remove:', src_path)        
