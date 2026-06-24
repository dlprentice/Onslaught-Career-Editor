/* address: 0x004e1260 */
/* name: CMonitor__UpdateTrackedValueAndDirection */
/* signature: void __thiscall CMonitor__UpdateTrackedValueAndDirection(void * this, int track_id, int sample_value, float delta_step, float sample_key, int flags) */


void __thiscall
CMonitor__UpdateTrackedValueAndDirection
          (void *this,int track_id,int sample_value,float delta_step,float sample_key,int flags)

{
  float *pfVar1;

  pfVar1 = *(float **)((int)this + 0xc);
  if (pfVar1 != (float *)0x0) {
    while ((pfVar1[3] != (float)track_id || (*pfVar1 != sample_key))) {
      pfVar1 = (float *)pfVar1[0x1d];
      if (pfVar1 == (float *)0x0) {
        return;
      }
    }
    pfVar1[10] = (float)sample_value;
    if ((float)sample_value < pfVar1[8]) {
      pfVar1[9] = -delta_step;
      return;
    }
    pfVar1[9] = delta_step;
  }
  return;
}
