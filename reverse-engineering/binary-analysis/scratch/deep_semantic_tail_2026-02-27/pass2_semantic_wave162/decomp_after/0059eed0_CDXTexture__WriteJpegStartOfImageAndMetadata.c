/* address: 0x0059eed0 */
/* name: CDXTexture__WriteJpegStartOfImageAndMetadata */
/* signature: void __stdcall CDXTexture__WriteJpegStartOfImageAndMetadata(void * param_1) */


void CDXTexture__WriteJpegStartOfImageAndMetadata(void *param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined1 *puVar3;
  int iVar4;
  int iVar5;

  puVar2 = *(undefined4 **)((int)param_1 + 0x18);
  puVar3 = (undefined1 *)*puVar2;
  *puVar3 = 0xff;
  *puVar2 = puVar3 + 1;
  iVar5 = puVar2[1];
  iVar4 = *(int *)((int)param_1 + 0x164);
  puVar2[1] = iVar5 + -1;
  if (iVar5 + -1 == 0) {
    iVar5 = (*(code *)puVar2[3])(param_1);
    if (iVar5 == 0) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x18;
      (*(code *)*puVar2)(param_1);
    }
  }
  puVar2 = *(undefined4 **)((int)param_1 + 0x18);
  puVar3 = (undefined1 *)*puVar2;
  *puVar3 = 0xd8;
  *puVar2 = puVar3 + 1;
  piVar1 = puVar2 + 1;
  *piVar1 = *piVar1 + -1;
  if (*piVar1 == 0) {
    iVar5 = (*(code *)puVar2[3])(param_1);
    if (iVar5 == 0) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x18;
      (*(code *)*puVar2)(param_1);
    }
  }
  iVar5 = *(int *)((int)param_1 + 0xd0);
  *(undefined4 *)(iVar4 + 0x1c) = 0;
  if (iVar5 != 0) {
    CDXTexture__WriteJpegApp0JfifSegment();
  }
  if (*(int *)((int)param_1 + 0xdc) != 0) {
    CTexture__Helper_0059ebf0();
  }
  return;
}
