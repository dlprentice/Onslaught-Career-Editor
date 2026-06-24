/* address: 0x005928d0 */
/* name: CDXTexture__ConsumeExpectedRestartMarker */
/* signature: int __stdcall CDXTexture__ConsumeExpectedRestartMarker(void * param_1) */


int CDXTexture__ConsumeExpectedRestartMarker(void *param_1)

{
  int iVar1;
  int iVar2;

  if ((*(int *)((int)param_1 + 0x1a4) == 0) &&
     (iVar2 = CTexture__Helper_00592420(param_1), iVar2 == 0)) {
    return 0;
  }
  iVar2 = *(int *)((int)param_1 + 0x1bc);
  iVar1 = *(int *)(iVar2 + 0x14);
  if (*(int *)((int)param_1 + 0x1a4) == iVar1 + 0xd0) {
    iVar1 = *(int *)param_1;
    *(undefined4 *)(iVar1 + 0x14) = 0x62;
    *(undefined4 *)(iVar1 + 0x18) = *(undefined4 *)(iVar2 + 0x14);
    (**(code **)(iVar1 + 4))(param_1,3);
    *(undefined4 *)((int)param_1 + 0x1a4) = 0;
  }
  else {
    iVar2 = (**(code **)(*(int *)((int)param_1 + 0x18) + 0x14))(param_1,iVar1);
    if (iVar2 == 0) {
      return 0;
    }
  }
  *(uint *)(*(int *)((int)param_1 + 0x1bc) + 0x14) =
       *(int *)(*(int *)((int)param_1 + 0x1bc) + 0x14) + 1U & 7;
  return 1;
}
