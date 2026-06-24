/* address: 0x004f78c0 */
/* name: CDXBattleLine__Helper_004f78c0 */
/* signature: short * __thiscall CDXBattleLine__Helper_004f78c0(void * this, int param_1, int param_2, int param_3) */


short * __thiscall CDXBattleLine__Helper_004f78c0(void *this,int param_1,int param_2,int param_3)

{
  short sVar1;
  short *psVar2;
  int iVar3;

  psVar2 = *(short **)((int)this + 4);
  iVar3 = *(int *)((int)this + 0xc);
  if (iVar3 != 0) {
    do {
      if ((*psVar2 == (short)param_1) && (psVar2[1] == (short)param_2)) {
        return psVar2;
      }
      if ((psVar2[1] == (short)param_1) && (psVar2[2] == (short)param_2)) {
        sVar1 = *psVar2;
        *psVar2 = psVar2[1];
        psVar2[1] = psVar2[2];
        psVar2[2] = sVar1;
        return psVar2;
      }
      if ((psVar2[2] == (short)param_1) && (*psVar2 == (short)param_2)) {
        sVar1 = *psVar2;
        *psVar2 = psVar2[2];
        psVar2[2] = psVar2[1];
        psVar2[1] = sVar1;
        return psVar2;
      }
      psVar2 = psVar2 + 3;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
  }
  return (short *)0x0;
}
