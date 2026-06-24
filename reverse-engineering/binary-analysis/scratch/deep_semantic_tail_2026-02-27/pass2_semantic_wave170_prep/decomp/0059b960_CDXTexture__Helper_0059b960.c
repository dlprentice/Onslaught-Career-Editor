/* address: 0x0059b960 */
/* name: CDXTexture__Helper_0059b960 */
/* signature: int __stdcall CDXTexture__Helper_0059b960(void * param_1) */


int CDXTexture__Helper_0059b960(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;

  iVar1 = *(int *)((int)param_1 + 0x1b8);
  if (*(int *)(iVar1 + 0x14) != 0) {
    return 2;
  }
  iVar3 = (**(code **)(*(int *)((int)param_1 + 0x1bc) + 4))(param_1);
  if (iVar3 == 1) {
    if (*(int *)(iVar1 + 0x18) != 0) {
      CDXTexture__ValidateJpegFrameAndBuildScanLayout();
      *(undefined4 *)(iVar1 + 0x18) = 0;
      return 1;
    }
    if (*(int *)(iVar1 + 0x10) == 0) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x23;
      (*(code *)*puVar2)(param_1);
    }
    CDXTexture__Helper_0059b920((int)param_1);
  }
  else if (iVar3 == 2) {
    *(undefined4 *)(iVar1 + 0x14) = 1;
    if (*(int *)(iVar1 + 0x18) == 0) {
      if (*(int *)((int)param_1 + 0x94) < *(int *)((int)param_1 + 0x9c)) {
        *(int *)((int)param_1 + 0x9c) = *(int *)((int)param_1 + 0x94);
        return 2;
      }
    }
    else if (*(int *)(*(int *)((int)param_1 + 0x1bc) + 0x10) != 0) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x3b;
      (*(code *)*puVar2)(param_1);
      return 2;
    }
  }
  return iVar3;
}
