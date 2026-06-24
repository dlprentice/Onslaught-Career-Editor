/* address: 0x004e1260 */
/* name: CMonitor__Helper_004e1260 */
/* signature: void __thiscall CMonitor__Helper_004e1260(void * this, int param_1, int param_2, float param_3, float param_4, int param_5) */


void __thiscall
CMonitor__Helper_004e1260
          (void *this,int param_1,int param_2,float param_3,float param_4,int param_5)

{
  float *pfVar1;

  pfVar1 = *(float **)((int)this + 0xc);
  if (pfVar1 != (float *)0x0) {
    while ((pfVar1[3] != (float)param_1 || (*pfVar1 != param_4))) {
      pfVar1 = (float *)pfVar1[0x1d];
      if (pfVar1 == (float *)0x0) {
        return;
      }
    }
    pfVar1[10] = (float)param_2;
    if ((float)param_2 < pfVar1[8]) {
      pfVar1[9] = -param_3;
      return;
    }
    pfVar1[9] = param_3;
  }
  return;
}
