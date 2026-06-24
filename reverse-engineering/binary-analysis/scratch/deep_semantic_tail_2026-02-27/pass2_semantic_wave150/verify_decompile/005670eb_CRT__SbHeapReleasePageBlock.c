/* address: 0x005670eb */
/* name: CRT__SbHeapReleasePageBlock */
/* signature: void __cdecl CRT__SbHeapReleasePageBlock(int param_1, int param_2, void * param_3) */


void __cdecl CRT__SbHeapReleasePageBlock(int param_1,int param_2,void *param_3)

{
  int *piVar1;

  piVar1 = (int *)(param_1 + 0x18 + (param_2 - *(int *)(param_1 + 0x10) >> 0xc) * 8);
  *piVar1 = *piVar1 + (uint)*(byte *)param_3;
  *(undefined1 *)param_3 = 0;
  piVar1[1] = 0xf1;
  if ((*piVar1 == 0xf0) && (DAT_009d09bc = DAT_009d09bc + 1, DAT_009d09bc == 0x20)) {
    CDXTexture__Helper_00566fd2(0x10);
  }
  return;
}
