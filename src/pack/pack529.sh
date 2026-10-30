set -e
R=/root/work/release529; W=/tmp/claude-0/pack529; rm -rf $W; mkdir -p $W $R
cd /root/work/xzbuild
java -cp xz.jar:t T dz528m.xz $W/check.dz && cmp $W/check.dz /root/work/out/blackops_mali_v528.dz && echo XZ_OK_M && rm $W/check.dz
python3 - <<'P'
import zipfile
src='/root/work/release40/BOZ_Kino_BO1_Remaster_v4.0_Mali_AllInOne.apk'
dst='/tmp/claude-0/pack529/unsigned_m.apk'
rep={'classes.dex':open('/tmp/claude-0/smali59/out_m/classes.dex','rb').read(),'assets/blackops_atitc.dz.xz':open('/root/work/xzbuild/dz528m.xz','rb').read(),'assets/boz.s3e':open('/root/work/v526/code/boz.s3e','rb').read()}
add={f'assets/blackops-music/nacht_radio{k}.mp3':open(f'/root/work/v42/audio/nacht_radio{k}.mp3','rb').read() for k in (1,2,3)}
add.update({f'assets/blackops-music/{g}_radio{k}.mp3':open(f'/root/work/v55/audio/{g}_radio{k}.mp3','rb').read() for g in ('shino','phone') for k in (1,2,3,4)})
add['assets/blackops-music/nacht_radio4.mp3']=open('/root/work/v55/audio/nacht_radio4.mp3','rb').read()
add['assets/intro/cotd_intro.mp4']=open('/root/work/v55/intro/cotd_intro.mp4','rb').read()
add['assets/intro/kino_loading.mp3']=open('/root/work/v514/kino_loading.mp3','rb').read()
add['assets/intro/kino_loading_screen.jpg']=open('/root/work/v514/kino_loading_screen.jpg','rb').read()
add['classes2.dex']=open('/root/work/v514/classes2.dex','rb').read()
for n in ('boz_c.mp3','boz_k.mp3'): add['assets/blackops-music/'+n]=open('/root/work/v55/intro/'+n.replace('.mp3','510.mp3'),'rb').read()
zi=zipfile.ZipFile(src); zo=zipfile.ZipFile(dst,'w'); seen=set()
for it in zi.infolist():
    if it.filename.startswith('META-INF/') and it.filename.endswith(('.SF','.RSA','.MF','.EC','.DSA')): continue
    data=rep.get(it.filename) or zi.read(it.filename); seen.add(it.filename)
    ni=zipfile.ZipInfo(it.filename,it.date_time); ni.compress_type=it.compress_type; ni.external_attr=it.external_attr
    zo.writestr(ni,data)
ref=zi.getinfo('assets/blackops-music/nacht_radio.mp3')
for n,d in add.items():
    assert n not in seen; ni=zipfile.ZipInfo(n,ref.date_time); ni.compress_type=ref.compress_type; ni.external_attr=ref.external_attr; zo.writestr(ni,d)
zo.close(); assert all(k in seen for k in rep); print('unsigned ok')
P
cd $W; mkdir -p signed_m; java -jar /root/work/signer/uber.jar -a unsigned_m.apk -o signed_m --debug 2>&1 | grep -v JAVA_TOOL | tail -2
cp signed_m/*.apk $R/BOZ_Kino_BO1_Remaster_v5.29_Mali_AllInOne.apk
cd $R && rm -f *.zip* && cp /root/work/out/CHANGELOG.txt .
zip -0 -q Kino_BO1_Remaster_v5.29_Mali.zip BOZ_Kino_BO1_Remaster_v5.29_Mali_AllInOne.apk CHANGELOG.txt
split -b 30408704 -d -a 3 --numeric-suffixes=1 Kino_BO1_Remaster_v5.29_Mali.zip Kino_BO1_Remaster_v5.29_Mali.zip.
ls -la $R
