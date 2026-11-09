import json,os,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
def settings():
 c=json.loads((ROOT/'asr-config.json').read_text(encoding='utf-8-sig'))
 if c['device'] not in ('cpu','cuda'):raise ValueError('device must be cpu or cuda; macOS uses cpu')
 return c
DLL_HANDLES=[]
def load_model(c):
 if c['device']=='cuda':
  # Optional torch supplies runtime libraries in this deployment's own venv.
  import torch
  if not torch.cuda.is_available():raise RuntimeError('CUDA is unavailable; run doctor or choose CPU')
  folder=pathlib.Path(torch.__file__).parent/'lib'
  if os.name=='nt':DLL_HANDLES.append(os.add_dll_directory(str(folder)))
 from faster_whisper import WhisperModel
 path=pathlib.Path(c['model_path'])
 if not path.is_absolute():path=ROOT/path
 return WhisperModel(str(path),device=c['device'],compute_type='int8_float16' if c['device']=='cuda' else 'int8',cpu_threads=c.get('cpu_threads',4),local_files_only=True)
def options(c):
 return dict(language=c.get('language') or None,beam_size=5,temperature=0,condition_on_previous_text=False,initial_prompt=None,no_speech_threshold=.4,vad_filter=True,vad_parameters={'min_silence_duration_ms':300},repetition_penalty=1.1,no_repeat_ngram_size=3)
