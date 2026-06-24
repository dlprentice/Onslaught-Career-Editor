/* address: 0x0050d720 */
/* name: CWorld__UpdateWorldTextSlotTiming */
/* signature: void __thiscall CWorld__UpdateWorldTextSlotTiming(void * this, int param_1, float param_2, float param_3, float param_4) */


void __thiscall
CWorld__UpdateWorldTextSlotTiming(void *this,int param_1,float param_2,float param_3,float param_4)

{
  float *pfVar1;
  int iVar2;

  pfVar1 = (float *)((int)this + 0x23c);
  iVar2 = 4;
  do {
    if (pfVar1[-8] == (float)param_1) {
      if (pfVar1[-0xc] == 4.2039e-45) {
        *pfVar1 = DAT_00672fd0 + param_2;
      }
      else {
        *pfVar1 = param_2;
        pfVar1[4] = param_3;
      }
    }
    pfVar1 = pfVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}
