/* address: 0x0055fc5d */
/* name: CD3DApplication__Helper_0055fc5d */
/* signature: char * __cdecl CD3DApplication__Helper_0055fc5d(void * param_1, int param_2, void * param_3) */


char * __cdecl CD3DApplication__Helper_0055fc5d(void *param_1,int param_2,void *param_3)

{
  int *piVar1;
  uint uVar2;
  char *pcVar3;

  if (param_2 < 1) {
    param_1 = (char *)0x0;
  }
  else {
    CRT__LockRouteByAddress((uint)param_3);
    pcVar3 = param_1;
    do {
      param_2 = param_2 + -1;
      if (param_2 == 0) break;
      piVar1 = (int *)((int)param_3 + 4);
      *piVar1 = *piVar1 + -1;
      if (*piVar1 < 0) {
        uVar2 = CRT__ReadByteWithBufferRefill(param_3);
      }
      else {
        uVar2 = (uint)**(byte **)param_3;
        *(byte **)param_3 = *(byte **)param_3 + 1;
      }
      if (uVar2 == 0xffffffff) {
        if (pcVar3 == param_1) {
          param_1 = (char *)0x0;
          goto LAB_0055fcb1;
        }
        break;
      }
      *pcVar3 = (char)uVar2;
      pcVar3 = pcVar3 + 1;
    } while ((char)uVar2 != '\n');
    *pcVar3 = '\0';
LAB_0055fcb1:
    CRT__UnlockRouteByAddress((uint)param_3);
  }
  return param_1;
}
