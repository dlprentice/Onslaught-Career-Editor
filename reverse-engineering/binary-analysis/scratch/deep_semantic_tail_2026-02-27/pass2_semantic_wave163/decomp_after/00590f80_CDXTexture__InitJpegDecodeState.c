/* address: 0x00590f80 */
/* name: CDXTexture__InitJpegDecodeState */
/* signature: void __stdcall CDXTexture__InitJpegDecodeState(void * param_1, int param_2, int param_3) */


void CDXTexture__InitJpegDecodeState(void *param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  int iVar4;

  *(undefined4 *)((int)param_1 + 4) = 0;
  if (param_2 != 0x3e) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0xc;
    puVar3[6] = 0x3e;
    puVar3[7] = param_2;
    (*(code *)*puVar3)(param_1);
  }
  if (param_3 != 0x1d8) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x15;
    puVar3[6] = 0x1d8;
    puVar3[7] = param_3;
    (*(code *)*puVar3)(param_1);
  }
  uVar1 = *(undefined4 *)param_1;
  uVar2 = *(undefined4 *)((int)param_1 + 0xc);
  puVar3 = param_1;
  for (iVar4 = 0x76; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar3 = 0;
    puVar3 = puVar3 + 1;
  }
  *(undefined4 *)param_1 = uVar1;
  *(undefined4 *)((int)param_1 + 0xc) = uVar2;
  *(undefined4 *)((int)param_1 + 0x10) = 1;
  CDXTexture__InitDecodeAllocatorVtable(param_1);
  *(undefined4 *)((int)param_1 + 8) = 0;
  *(undefined4 *)((int)param_1 + 0x18) = 0;
  *(undefined4 *)((int)param_1 + 0xa8) = 0;
  *(undefined4 *)((int)param_1 + 0xac) = 0;
  *(undefined4 *)((int)param_1 + 0xb0) = 0;
  *(undefined4 *)((int)param_1 + 0xb4) = 0;
  puVar3 = (undefined4 *)((int)param_1 + 200);
  iVar4 = 4;
  do {
    puVar3[-4] = 0;
    *puVar3 = 0;
    puVar3 = puVar3 + 1;
    iVar4 = iVar4 + -1;
  } while (iVar4 != 0);
  *(undefined4 *)((int)param_1 + 0x134) = 0;
  CDXTexture__InitJpegMarkerReader((int)param_1);
  CDXTexture__DecodeState_CreateCallbackContext((int)param_1);
  *(undefined4 *)((int)param_1 + 0x14) = 200;
  return;
}
