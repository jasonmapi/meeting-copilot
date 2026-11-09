"""Local host microphone, portable CPU/CUDA. Never starts at installation."""
import pathlib,os,json,time,queue,uuid,argparse,threading,math
from asr_runtime import settings,load_model,options
ROOT=pathlib.Path(__file__).resolve().parent;STOP=ROOT/'recorder-stop.flag'
def status(message,**extra):
 p=ROOT/'results/recorder-status.json';tmp=p.with_suffix('.tmp')
 tmp.write_text(json.dumps(dict(message=message,**extra),ensure_ascii=False),encoding='utf-8');tmp.replace(p)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--audio');parser.add_argument('--output-dir');args=parser.parse_args()
 import numpy as np,psutil
 from scipy.signal import resample_poly
 try:
  if os.name=='nt':psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
  else:os.nice(5)
 except (OSError,psutil.Error):pass
 c=settings();status('正在加载本地语音模型…');model=load_model(c)
 if STOP.exists():status('录音已取消');return
 folder=pathlib.Path(args.output_dir) if args.output_dir else ROOT/'transcripts';folder.mkdir(exist_ok=True)
 path=folder/('访谈-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.txt');path.write_text('',encoding='utf-8')
 chunk=int(c.get('chunk_seconds',12)*16000)
 def transcribe(audio):
  if len(audio)<3200 or np.abs(audio).mean()<.003:return
  start=time.monotonic();segments,_=model.transcribe(audio,**options(c));text=''.join(s.text for s in segments).strip()
  if text:
   with path.open('a',encoding='utf-8') as f:f.write(text+'\n\n')
  status('录音中 · 本地 '+c['device']+' · 可切换其他软件',file=path.name,inference_seconds=round(time.monotonic()-start,2))
 if args.audio:
  from faster_whisper.audio import decode_audio
  audio=decode_audio(args.audio,sampling_rate=16000)
  for i in range(0,len(audio),chunk):transcribe(audio[i:i+chunk])
 else:
  import sounddevice as sd
  device=c.get('input_device');info=sd.query_devices(device,'input');sr=int(info['default_samplerate'])
  q=queue.Queue(maxsize=400);overflow=threading.Event();pending=np.empty(0,dtype=np.float32)
  def callback(data,frames,timing,flags):
   if flags.input_overflow:overflow.set()
   try:q.put_nowait(data[:,0].copy())
   except queue.Full:overflow.set()
  def convert(data):
   if sr==16000:return data
   g=math.gcd(sr,16000);return resample_poly(data,16000//g,sr//g).astype(np.float32)
  with sd.InputStream(device=device,samplerate=sr,channels=1,blocksize=sr//10,dtype='float32',callback=callback):
   status('录音中 · 本地 '+c['device']+' · 可切换其他软件',file=path.name)
   while not STOP.exists():
    if overflow.is_set():raise RuntimeError('音频输入溢出或处理积压，请增大分段或使用更快配置')
    try:pending=np.concatenate((pending,convert(q.get(timeout=.2))))
    except queue.Empty:continue
    while len(pending)>=chunk:
     transcribe(pending[:chunk]);pending=pending[chunk:]
  while not q.empty():pending=np.concatenate((pending,convert(q.get_nowait())))
  for i in range(0,len(pending),chunk):transcribe(pending[i:i+chunk])
 status('录音已停止 · 文字与成果已保留',file=path.name);print(str(path),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:
  status('录音或转写失败：'+type(e).__name__+'。请运行doctor检查模型、麦克风权限与设备。',error=type(e).__name__)
  raise
