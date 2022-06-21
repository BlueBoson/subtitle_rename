## Description

This is a tool for renaming subtitles in bench.

## Usage

### options

```
usage: sub_rename.py [+file] [options]

Use [+file] to read arguments from file (recommanded)

optional arguments:
  -h, --help            show this help message and exit

general options:
  -y, --yes             ignore confirmation
  -t, --test            print rename intention and exit
  --overwrite           force overwrite if file exists
  --remove              remove original files after rename

path arguments:
  -s SRC-DIR, --src-dir SRC-DIR
                        path to files read (default: cwd)
  -d DST-DIR, --dst-dir DST-DIR
                        path to files stored (default: SRC-DIR)

pattern arguments:
  --with-ext            provide extension in input and correspond patterns (default: match all extensions)
  -i INPUT-PATTERN, --input-pattern INPUT-PATTERN
                        name pattern for input files. substrs in parentheses are treated as regex, so use escape for   
                        raw parentheses in filename, use group with (?P<group>...)
  -o OUTPUT-PATTERN, --output-pattern-no-ext OUTPUT-PATTERN
                        [input-only mode] output format pattern (without ext) using only literal and input group,  
                        {group index|name} for group in INPUT-PATTERN, python3 format grammer is supported
  -c CORRESPOND-PATTERN, --correspond-pattern CORRESPOND-PATTERN
                        [with-correspond-file mode] name pattern for correspong files, similar to INPUT-PATTERN. when  
                        set CORRESPOND-PATTERN, input and correspong pattern will be matched by named group
```

### args from file

Use `+file` as an argument to read arguments from file (encoding in utf-8, seperated by newlines). For encoding reasons, using file is recommanded.

### patterns

For input and correspond pattern, parts inside parens will be treated as regex. So \ ( ) in file name must be escaped. e.g. cprrespond pattern in `examples/bakemono.txt`:

```
[AI-Raws] ジョジョの奇妙な冒険 黄金の風 #(?P<ep>\d+)(?P<fullep>\(\d+\)) \(BD HEVC 1920x1080 yuv444p10le FLAC\)[(?P<hash>\w+)]
```

This pattern has 3 regex group: ep, fullep, hash. The other parts are treated as plain text.

In fact, pattern will be converted to a big regex pattern, with parts outside parens escaped. i.e. the pattern above will be converted to:

```
\[AI-Raws\] ジョジョの奇妙な冒険 黄金の風 #(?P<ep>\d+)(?P<fullep>\(\d+\)) \(BD HEVC 1920x1080 yuv444p10le FLAC\)[(?P<hash>\w+)]
```

## Examples

This tool provides two mode.

### input-only mode

For example, I have some subtitles for the anime *Bakemonogatari* named:

> Bakemonogatari.01.CASO.ass
>
> Bakemonogatari.02.CASO.ass
>
> ......

However, the corresponding video files are named:

> [ReinForce] Bakemonogatari - 01 (BDRip 1920x1080 x264 FLAC).mkv
>
> [ReinForce] Bakemonogatari - 02 (BDRip 1920x1080 x264 FLAC).mkv
>
> ......

The different naming styles make players (e.g. PotPlayer) can't load subtitles automatically.

Run this tool with options:

```
-i 'Bakemonogatari.(?P<ep>\d+).CASO'
-o '[ReinForce] Bakemonogatari - {ep} (BDRip 1920x1080 x264 FLAC)'
```

For input-pattern argument, parts inside parens will be treated as regex. The tool finds all files named like *Bakemonogatari.(\d+).CASO* and extracts the episode field. Then renaming them to *Bakemonogatari.(?P `<ep>`\d+).CASO*.

```
assBakemonogatari.01.CASO.ass -> [ReinForce] Bakemonogatari - 01 (BDRip 1920x1080 x264 FLAC).ass   
assBakemonogatari.02.CASO.ass -> [ReinForce] Bakemonogatari - 02 (BDRip 1920x1080 x264 FLAC).ass 
...... 
```

### with-correspond-file mode

This time I have some subtitles and videos for the anime JoJo-V named:

```
[AI-Raws] ジョジョの奇妙な冒険 黄金の風 #01(114) (BD HEVC 1920x1080 yuv444p10le FLAC)[E6204030].mkv
[AI-Raws] ジョジョの奇妙な冒険 黄金の風 #02(115) (BD HEVC 1920x1080 yuv444p10le FLAC)[D9309E4E].mkv
......
[AI-Raws] ジョジョの奇妙な冒険 黄金の風 #01.ass
[AI-Raws] ジョジョの奇妙な冒険 黄金の風 #02.ass
......
```

The input pattern is not enough to determine output names.

Run this tool with options:

```
-i '[AI-Raws] ジョジョの奇妙な冒険 黄金の風 #(?P<ep>\d+)'
-c '[AI-Raws] ジョジョの奇妙な冒険 黄金の風 #(?P<ep>\d+)(?P<fullep>\(\d+\)) \(BD HEVC 1920x1080 yuv444p10le FLAC\)[(?P<hash>\w+)]'
```

Each matched input file is corresponded with a matched file, iff all groups in input pattern is same as corresponding files. The result will be:

```
[AI-Raws] ジョジョの奇妙な冒険 黄金の風 #01.ass -> [AI-Raws] ジョジョの奇妙な冒険 黄金の風 #01(114) (BD HEVC 1920x1080 yuv444p10le FLAC)[E6204030].ass
[AI-Raws] ジョジョの奇妙な冒険 黄金の風 #02.ass -> [AI-Raws] ジョジョの奇妙な冒険 黄金の風 #02(115) (BD HEVC 1920x1080 yuv444p10le FLAC)[D9309E4E].ass
......
```
