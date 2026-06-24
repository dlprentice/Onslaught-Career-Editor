/* address: 0x0055eb00 */
/* name: CRT__WcsNcpyZeroPad */
/* signature: short * __cdecl CRT__WcsNcpyZeroPad(void * param_1, void * param_2, int param_3) */


short * __cdecl CRT__WcsNcpyZeroPad(void *param_1,void *param_2,int param_3)

{
  short sVar1;
  uint uVar2;
  uint uVar3;
  short *psVar4;

  psVar4 = param_1;
  if (param_3 != 0) {
    do {
      sVar1 = *(short *)param_2;
      *psVar4 = sVar1;
      psVar4 = psVar4 + 1;
      param_2 = (void *)((int)param_2 + 2);
      if (sVar1 == 0) break;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
    if ((param_3 != 0) && (uVar2 = param_3 - 1, uVar2 != 0)) {
      for (uVar3 = uVar2 >> 1; uVar3 != 0; uVar3 = uVar3 - 1) {
        psVar4[0] = 0;
        psVar4[1] = 0;
        psVar4 = psVar4 + 2;
      }
      for (uVar2 = (uint)((uVar2 & 1) != 0); uVar2 != 0; uVar2 = uVar2 - 1) {
        *psVar4 = 0;
        psVar4 = psVar4 + 1;
      }
    }
  }
  return param_1;
}
